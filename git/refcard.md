---
title: Git - Useful Commands
description: Daily needs
published: true
date: 2026-10-26T14:13:42.980Z
tags: gitea, git
editor: markdown
dateCreated: 2026-07-13T15:19:26.552Z
---

# Git & GitHub Cheat Sheet

A practical quick reference for the most common repository tasks.

> **Assumptions:** The default branch is `main`, the remote is called `origin`, and GitHub CLI (`gh`) is optional. Replace placeholders such as `OWNER`, `REPO`, and `BRANCH_NAME`.

## 1. Clone a repository

```bash
# HTTPS
git clone https://github.com/OWNER/REPO.git

# SSH
git clone git@github.com:OWNER/REPO.git

cd REPO
```

Check the configured remote:

```bash
git remote -v
git status
```

## 2. Start a new branch

Always start from an up-to-date default branch:

```bash
git switch main
git pull --ff-only origin main

git switch --create feature/short-description
```

Common branch prefixes:

- `feature/` — new functionality
- `fix/` — bug fix
- `docs/` — documentation
- `refactor/` — code restructuring
- `test/` — tests
- `chore/` — maintenance

Older Git versions can use `git checkout -b BRANCH_NAME` instead of `git switch --create BRANCH_NAME`.

## 3. Inspect changes

```bash
# Working-tree summary
git status

# Unstaged changes
git diff

# Staged changes
git diff --cached

# List local and remote branches
git branch --all
```

## 4. Make changes, commit, and push

Edit the files, run the relevant tests, then review and commit only the intended changes:

```bash
git add path/to/file path/to/another-file
# Or stage all tracked and untracked changes after reviewing them:
# git add .

git diff --cached
git commit -m "feat: describe the change"

git push --set-upstream origin HEAD
```

Useful commit prefixes:

```text
feat: add a new capability
fix: correct an error
docs: update documentation
test: add or update tests
refactor: simplify implementation
chore: update tooling
```

## 5. Create a pull request

### With GitHub CLI

Install and authenticate `gh` first, then run:

```bash
gh pr create \
  --base main \
  --head "$(git branch --show-current)" \
  --title "feat: describe the change" \
  --body "## Summary
- Explain what changed

## Testing
- Explain what you tested"
```

Create a draft PR:

```bash
gh pr create --draft --base main --title "WIP: describe the change"
```

### In the GitHub web interface

1. Push the branch to GitHub.
2. Open the repository on GitHub.
3. Select **Compare & pull request** or **New pull request**.
4. Choose `main` as the base branch and your feature branch as the compare branch.
5. Add a clear title and summary.
6. Describe tests and any operational impact.
7. Select reviewers, labels, or a project if needed.
8. Create the pull request.

## 6. Update an existing PR

A PR updates automatically when new commits are pushed to its branch:

```bash
git switch feature/short-description
# edit files and run tests

git add .
git commit -m "fix: address review feedback"
git push
```

View the PR and checks with `gh`:

```bash
gh pr view --web
gh pr checks
```

## 7. Keep a branch up to date

Update the local default branch, then rebase your feature branch:

```bash
git fetch origin
git switch main
git pull --ff-only origin main

git switch feature/short-description
git rebase main

git push --force-with-lease
```

Use `--force-with-lease`, not plain `--force`, because it protects against overwriting someone else's newer remote work.

## 8. Delete branches

After the PR is merged or abandoned:

```bash
# Delete the local branch; -d refuses if it is not merged
git switch main
git branch --delete feature/short-description

# Force-delete a local branch only when you are certain it is no longer needed
git branch --delete --force feature/short-description

# Delete the remote branch
git push origin --delete feature/short-description

# Remove stale remote-tracking references
git fetch --prune
```

With GitHub CLI:

```bash
gh pr close PR_NUMBER
gh pr delete-branch PR_NUMBER
```

## 9. Fetch, pull, and push

```bash
# Download remote updates without changing local files
git fetch origin

# Fetch and integrate the current branch
git pull --ff-only

# Push the current branch
git push
```

Prefer `git pull --ff-only` when you want Git to stop instead of creating an unexpected merge commit.

## 10. Undo common mistakes

```bash
# Unstage a file, keeping its changes
git restore --staged path/to/file

# Discard local changes in a file — destructive
git restore path/to/file

# Amend the last commit before it has been shared
git commit --amend

# Undo a published commit safely by creating a new commit
git revert COMMIT_SHA
```

> Do not use `git reset --hard` or rewrite shared history unless you understand the impact and have authorization.

## 11. Review and merge a PR

Before merging:

- Confirm the PR targets the correct base branch.
- Review the diff and conversation.
- Ensure CI checks pass.
- Resolve or document review comments.
- Confirm required approvals and branch-protection rules.

With GitHub CLI:

```bash
gh pr checks PR_NUMBER
gh pr merge PR_NUMBER --squash --delete-branch
```

The exact merge method depends on repository policy. Common choices are **merge commit**, **squash**, and **rebase**.

## Minimal end-to-end workflow

```bash
git clone https://github.com/OWNER/REPO.git
cd REPO

git switch main
git pull --ff-only origin main
git switch --create feature/my-change

# Make and test changes
git add .
git diff --cached
git commit -m "feat: implement my change"
git push --set-upstream origin HEAD

# Create the PR in GitHub or with:
gh pr create --base main --title "feat: implement my change"
```

## Official references

- [GitHub — Cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
- [GitHub — Getting changes from a remote repository](https://docs.github.com/en/get-started/using-git/getting-changes-from-a-remote-repository)
- [GitHub — Collaborating with pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests)
- [GitHub CLI — `gh pr`](https://cli.github.com/manual/gh_pr)
- [Git — `clone`](https://git-scm.com/docs/git-clone)
- [Git — `branch`](https://git-scm.com/docs/git-branch)
- [Git — `push`](https://git-scm.com/docs/git-push)
- [Git — `pull`](https://git-scm.com/docs/git-pull)
- [Git — `restore`](https://git-scm.com/docs/git-restore)
- [Git — `revert`](https://git-scm.com/docs/git-revert)
