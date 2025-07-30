#!/usr/bin/env python3
"""
deploy.py – robuste + logs d’étapes
----------------------------------

Pipeline entièrement automatisé :
    1. Vérif pré-requis (git, libs Python, token GitHub)
    2. Bootstrap fichiers (pyproject, README, LICENCE, .gitignore, …)
    3. Nettoyage build/
    4. Bump patch de version (format X.Y.Z)
    5. Build éventuel frontend npm
    6. Build paquet Python + install -e .
    7. Git init / remote / push / tag
    8. Upload dist/* sur PyPI via Twine

Chaque étape est loggée ; en cas d’échec, message clair – pas de traceback
brut.
"""

def main():

    # ────────────────────────── IMPORTS STANDARD ─────────────────────────
    import os
    import sys
    import json
    import shutil
    import subprocess
    import textwrap
    from pathlib import Path
    from contextlib import contextmanager

    # ────────────────────────── LOGGING HELPERS ──────────────────────────
    def log(step: str, msg: str):
        print(f"▶️  [{step}] {msg}")

    def fail(step: str, msg: str, code: int = 1):
        print(f"❌ [{step}] {msg}")
        sys.exit(code)

    def run(cmd, step, cwd=None, quiet=False):
        """Subprocess wrapper avec message d’erreur propre."""
        if not quiet:
            log(step, " ".join(cmd))
        try:
            subprocess.run(cmd, cwd=cwd, check=True)
        except subprocess.CalledProcessError as e:
            fail(step, f"commande « {' '.join(e.cmd)} » → code {e.returncode}")

    @contextmanager
    def step(name: str):
        log(name, "démarrage…")
        try:
            yield
            log(name, "OK")
        except Exception as exc:
            fail(name, str(exc))

    # ────────────────────────── PRÉ-REQUIS SYSTÈME ───────────────────────
    if shutil.which("git") is None:
        fail("Pré-requis", "git introuvable dans le PATH")

    # ────────────────────────── LIBS PYTHON ──────────────────────────────
    def ensure_libs():
        try:
            import toml, build, twine, dotenv, requests  # noqa
        except ImportError:
            run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "build",
                    "twine",
                    "toml",
                    "python-dotenv",
                    "requests",
                ],
                step="Install dépendances",
                quiet=True,
            )


    ensure_libs()
    import toml, requests
    from dotenv import load_dotenv
    from requests.exceptions import RequestException

    # ────────────────────────── FONCTIONS UTIL ───────────────────────────
    def safe_get(url, **kw):
        try:
            return requests.get(url, timeout=10, **kw)
        except RequestException as e:
            raise RuntimeError(f"erreur réseau : {e}") from None

    def bump_patch(version: str) -> str:
        """Incrémente le patch X.Y.Z → X.Y.(Z+1) avec validation."""
        parts = version.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise RuntimeError(f"format de version invalide : « {version} »")
        major, minor, patch = map(int, parts)
        return f"{major}.{minor}.{patch + 1}"

    # ────────────────────────── CONTEXTE GLOBAL ─────────────────────────
    ROOT = Path.cwd()
    PYPROJECT = ROOT / "pyproject.toml"

    load_dotenv()
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or fail("ENV", "GITHUB_TOKEN manquant dans .env")
    HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    # Détermination du nom de paquet
    if PYPROJECT.exists():
        PKG_NAME = toml.load(PYPROJECT)["project"]["name"]
    else:
        PKG_NAME = os.getenv("PKG_NAME") or ROOT.name.replace(" ", "_")

    # ────────────────────────── PIPELINE ────────────────────────────────
    try:
        with step("Infos GitHub"):
            user = safe_get("https://api.github.com/user", headers=HEADERS).json()
            GH_LOGIN = user.get("login") or "unknown"
            GH_NAME = user.get("name") or GH_LOGIN
            GH_MAIL = user.get("email") or f"{GH_LOGIN}@users.noreply.github.com"

        with step("Bootstrap fichiers"):
            if not PYPROJECT.exists():
                # Avertissement si nom pris sur PyPI
                if safe_get(f"https://pypi.org/pypi/{PKG_NAME}/json").status_code == 200:
                    log("Bootstrap fichiers", f"Nom « {PKG_NAME} » déjà présent sur PyPI.")
                PYPROJECT.write_text(
                    toml.dumps(
                        {
                            "project": {
                                "name": PKG_NAME,
                                "version": "0.0.1",
                                "readme": "README.md",
                                "license": {"text": "MIT"},
                                "authors": [{"name": GH_NAME, "email": GH_MAIL}],
                                "requires-python": ">=3.8",
                            },
                            "build-system": {
                                "requires": ["setuptools>=64", "wheel"],
                                "build-backend": "setuptools.build_meta",
                            },
                        }
                    )
                )

            defaults = {
                "README.md": f"# {PKG_NAME}\n",
                "LICENSE": "MIT License\n",
                "MANIFEST.in": "include README.md\ninclude LICENSE\n",
                ".gitignore": "__pycache__/\n.env\n*.egg-info/\ndist/\nbuild/\n",
            }
            for file, content in defaults.items():
                path = ROOT / file
                if not path.exists():
                    path.write_text(content, encoding="utf8")

        with step("Nettoyage build"):
            for d in ("build", "dist"):
                shutil.rmtree(ROOT / d, ignore_errors=True)
            for egg in ROOT.glob("*.egg-info"):
                shutil.rmtree(egg, ignore_errors=True)
            for p in ROOT.rglob("__pycache__"):
                shutil.rmtree(p, ignore_errors=True)

        with step("Bump version"):
            data = toml.load(PYPROJECT)
            old_version = data["project"]["version"]
            new_version = bump_patch(old_version)
            data["project"]["version"] = new_version
            PYPROJECT.write_text(toml.dumps(data))
            log("Bump version", f"{old_version} → {new_version}")

        with step("Frontend (si présent)"):
            pkg_json = next(ROOT.glob("**/package.json"), None)
            if pkg_json:
                if shutil.which("npm") is None:
                    raise RuntimeError("npm requis mais introuvable")
                pkg_data = json.loads(pkg_json.read_text())
                pkg_data["version"] = new_version
                pkg_json.write_text(json.dumps(pkg_data, indent=2))
                run(["npm", "install"], "npm install", cwd=pkg_json.parent, quiet=True)
                run(["npm", "run", "build"], "npm build", cwd=pkg_json.parent)

        with step("Build & install"):
            run([sys.executable, "-m", "build"], "python -m build", quiet=True)
            run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "-e", "."],
                "pip install -e .",
                quiet=True,
            )

        with step("Git init/push"):
            if not (ROOT / ".git").exists():
                run(["git", "init"], "git init")
                run(["git", "add", "."], "git add .")
                run(["git", "commit", "-m", "Initial commit"], "git commit")

            remotes = (
                subprocess.run(["git", "remote"], capture_output=True, text=True)
                .stdout.splitlines()
            )
            if "origin" not in remotes:
                repo_url = f"https://github.com/{GH_LOGIN}/{PKG_NAME}.git"
                resp = safe_get(repo_url, headers=HEADERS)
                if resp.status_code == 404:
                    create = requests.post(
                        "https://api.github.com/user/repos",
                        headers=HEADERS,
                        json={"name": PKG_NAME, "private": False},
                    )
                    if create.status_code not in (201, 422):
                        raise RuntimeError(f"création repo GitHub : {create.text}")
                run(["git", "remote", "add", "origin", repo_url], "git remote add")
                run(["git", "branch", "-M", "main"], "git branch -M main")
                run(["git", "push", "-u", "origin", "main"], "git push -u origin main")

            run(["git", "add", "."], "git add .")
            run(["git", "commit", "-m", f"patch update #{new_version}"], "git commit")
            run(["git", "tag", f"v{new_version}"], "git tag v")
            run(["git", "push"], "git push")
            run(["git", "push", "--tags"], "git push tags")

        with step("Upload PyPI"):
            if shutil.which("twine") is None:
                raise RuntimeError("twine introuvable")
            run(["twine", "upload", "dist/*"], "twine upload")

        print("🎉  Déploiement terminé sans accroc.")

    except KeyboardInterrupt:
        fail("Global", "interrompu par l’utilisateur")
    except Exception as e:
        fail(
            "Global",
            textwrap.dedent(
                f"""
                Erreur inattendue : {type(e).__name__}: {e}
                Active un mode verbose ou consulte la trace pour le détail.
                """
            ).strip(),
        )


if __name__=="__main__":
    main()