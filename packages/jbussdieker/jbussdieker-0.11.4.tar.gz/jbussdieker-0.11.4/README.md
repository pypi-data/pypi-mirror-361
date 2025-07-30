# python-jbussdieker

**A modern Python project generator — zero to PyPI with automated releases.**

## 🚀 What it does

**`jbussdieker`** scaffolds a best-practice Python project with:

- ✅ `pyproject.toml` using **PEP 621**
- ✅ GitHub Actions CI for linting, typing, tests, and publishing
- ✅ `Makefile` with simple install, lint, test commands
- ✅ `.gitignore` for Python best practices
- ✅ **release-please** workflow for versioning and changelogs
- ✅ Publish to **PyPI** using [Trusted Publishers](https://docs.pypi.org/trusted-publishers/)

**No tokens. No manual uploads. Just push, merge, and release.**

## 📦 Install

```bash
pip install jbussdieker --upgrade
```

## 🧑‍💻 Create a new project

```bash
jbussdieker create myproject
cd myproject
git init
git add .
git commit -m "feat: initial commit"
gh repo create --source=. --public --push
```

## ✅ Set up automated releases

1️⃣ **Ensure GitHub Actions has required permissions**

For `release-please` to work, your repository’s Actions must have write access and permission to create PRs.

* **Allow workflows to write to your repo:**
   - Go to your repo’s **Settings → Actions → General** ([GitHub Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#configuring-the-default-github_token-permissions))
   - Under **Workflow permissions**, select **Read and write permissions**

* **Allow Actions to create PRs:**
   - In the same [Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#preventing-github-actions-from-creating-or-approving-pull-requests)
   - Check **Allow GitHub Actions to create and approve pull requests**

These are **required** so the workflows can open changelog PRs and publish your releases automatically.

2️⃣ **Add a Trusted Publisher on PyPI**

Configure PyPI to trust your GitHub repo for publishing

* Visit [PyPI Publishing](https://pypi.org/manage/account/publishing/)
* **Scroll down** to **“Add a new pending publisher”**
* Fill out:

  * **GitHub Owner** → your username or org
  * **Repository Name** → your repo name (`myproject`)
  * **Workflow Name** →

    ```plaintext
    publish.yml
    ```
  * **Environment Name** →

    ```plaintext
    release
    ```
* Click **Add**.

**Note:** The generated `publish.yml` uses an environment named `release` by default. You can edit or remove this later — just keep it in sync with your PyPI settings.

3️⃣ **Push your first tag**

Once `release-please` opens a version bump PR, merging it will automatically publish your package. No API keys needed — PyPI trusts your GitHub Action.

Want to learn more? See the [release-please GitHub repo](https://github.com/googleapis/release-please).

## 🧹 Local development

Your project includes a simple `Makefile`:

```bash
make venv    # create .venv
make install # pip install -e .
make lint    # black + mypy
make format  # run black
make test    # run unittest
make clean   # remove .venv
```

## 🔒 Recommended GitHub repo settings

- ✅ Use **Squash merge only** (keeps your history tidy and compatible with release-please)
  See [release-please’s recommendation for a linear git commit history](https://github.com/googleapis/release-please?tab=readme-ov-file#linear-git-commit-history-use-squash-merge)
- ✅ Enable **Auto-delete branches after merge**

## 📢 Example workflow

```bash
# 1. Scaffold
jbussdieker create myproject

# 2. Init and push
cd myproject
git init
git add .
git commit -m "chore: initial commit"
gh repo create --source=. --public --push

# 3. Configure GitHub Actions permissions (required!)
# 4. Link Trusted Publisher on PyPI
# 5. Merge your first release-please PR
# 6. Done! 🚀
```

## 📝 License

This project is licensed under **MIT**.

## 🎉 Ship faster

No config sprawl. No secrets rotation. Just `git push` and publish Python packages the *modern* way.

---

**Enjoy! 🚀**
