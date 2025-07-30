# deploy_pkg

<p align="center">
  <b>Zero-click Python package deployment.</b><br>
  Build → GitHub → PyPI in a single command, without prompts.
</p>

---

## ✨ What is it?

**deploy_pkg** is a one-file deployment tool that:

1. Bootstraps a project (creates `pyproject.toml`, `README.md`, `LICENSE`, etc.).
2. Cleans build artifacts.
3. Bumps the patch version (`X.Y.Z → X.Y.(Z+1)`).
4. Builds an optional **frontend** (`npm install && npm run build` if a `package.json` is found).
5. Builds your Python package (`python -m build`) and installs it locally in *editable* mode.
6. Initializes a Git repository, or re-uses the existing one.
7. Creates a **GitHub** repo via the API (if none exists), adds it as `origin`, commits, tags, and pushes.
8. Uploads the freshly built distribution to **PyPI** with `twine`.

All of that **without asking a single question**.

---

## 🚀 Quick Start

```bash
pip install deploy-pkg        # install the script
deploy-pkg                    # run it in any project directory
```

* First run in an **empty folder**?  
  → deploy_pkg scaffolds a minimal package and publishes it immediately.

* Run it again later?  
  → deploy_pkg just bumps the version, rebuilds, commits, tags and republishes.

---

## 📦 Installation

### From PyPI

```bash
pip install deploy_pkg
```

### From source

```bash
git clone https://github.com/<you>/deploy_pkg.git
cd deploy_pkg
pip install -e .
```

---

## 🔧 Prerequisites

| Tool / Env var      | Purpose                                        |
|---------------------|------------------------------------------------|
| **git**             | version control, pushing to GitHub            |
| **Python ≥ 3.8**    | runtime                                        |
| **GITHUB_TOKEN**    | Personal Access Token with `repo` + `user:email` scopes |
| _(optional)_ **npm**| builds `/frontend` if present                  |

Create a **`.env`** file in your project root:

```env
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
# PKG_NAME=my_custom_name   # (optional) overrides the default package name
```

---

## 🖥️ Usage

```bash
deploy-pkg          # or:  python -m deploy_pkg
```

Works in **any** directory:

* **Blank directory** → bootstraps + publishes a first 0.0.1 release.  
* **Existing package** → bumps patch version, rebuilds, commits & tags.  
* **Dirty git status** → aborts with a clear error (keeps you safe).

---

## How it works – Step by Step

| # | Action | Details |
|---|--------|---------|
| 1 | _Requirements_ | Checks for `git`, installs missing Python libs (`build`, `twine`, `toml`, `requests`, `python-dotenv`). |
| 2 | _Scaffolding_  | Creates `pyproject.toml`, `README.md`, `LICENSE`, `MANIFEST.in`, `.gitignore` if absent. |
| 3 | _Clean_        | Removes `build/`, `dist/`, `*.egg-info`, `__pycache__`. |
| 4 | _Version bump_ | Reads `project.version` from *pyproject*, increments patch. |
| 5 | _Frontend_     | If a `package.json` exists anywhere: bumps its `version`, runs `npm install` & `npm run build`. |
| 6 | _Build & install_ | `python -m build` then `pip install -U -e .` |
| 7 | _Git / GitHub_ | Init repo, create GitHub repo (via REST API), add remote, commit `"patch update #<ver>"`, tag `v<ver>`, push. |
| 8 | _Publish_      | `twine upload dist/*` – your new package is live on PyPI. |

Any failure aborts the pipeline with a **clear, human-friendly error**.

---

## CLI Flags

_No flags yet._ deploy_pkg is intentionally minimal – but a `--dry-run` or
`--verbose` flag is planned (see Roadmap).

---

## Examples

### First-time release

```bash
mkdir awesome_pkg
cd awesome_pkg
deploy-pkg
# → 0.0.1 built, repo created on GitHub, uploaded to PyPI, installed locally
```

### Routine patch release

```bash
cd awesome_pkg
git status   # should be clean
deploy-pkg
# → 0.0.2 built, commit, tag v0.0.2, push, PyPI upload
```

### Using a custom package name

```bash
echo "PKG_NAME=super_lib" >> .env
deploy-pkg
```

---

## 🛡️ Security

* Access tokens are **never printed**.
* Git working tree must be **clean** or the run aborts (prevents accidental commits).
* Network operations (`requests`) use a 10-second timeout and explicit error handling.

---

## 🛠  Contributing

Pull Requests welcome!  
Clone the repo, install dev deps, run tests (to be added):

```bash
pip install -e ".[dev]"
pytest
```

Feel free to open issues for feature requests or bug reports.

---

## 🗺️ Roadmap

* `--dry-run` flag (show all steps, no side-effects)  
* Colorised logging (`rich`)  
* Pre-/post-deploy hooks  
* Config file for per-project overrides  
* Verbose mode with full traceback

---

## 🙋 Author

**Baptiste** – math teacher, Python developer, and despiser of tedious release checklists.

---

## 📝 License

deploy_pkg is released under the **MIT License** – do whatever you want,
just keep the copyright.

---

## ❤️ Acknowledgements

Inspired by the hundreds of times we forgot one of the following:

* bumping the version number  
* tagging the commit  
* uploading with Twine  
* pushing the tag  
* building the frontend first…

deploy_pkg never forgets.
