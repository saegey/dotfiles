#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "ERROR: not inside a git repository" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "${repo_root}"

base_ref="${1:-origin/main}"
template_path=".github/pull_request_template.md"

echo "== REPO ROOT =="
echo "${repo_root}"
echo

echo "== BASE REF =="
echo "${base_ref}"
echo

if git show-ref --verify --quiet "refs/remotes/${base_ref}"; then
  merge_base="$(git merge-base HEAD "${base_ref}")"
  echo "== MERGE BASE =="
  echo "${merge_base}"
  echo

  echo "== COMMITS (${base_ref}...HEAD) =="
  git log --no-merges --format='%h %s' "${base_ref}...HEAD"
  echo

  echo "== DIFF STAT (${base_ref}...HEAD) =="
  git diff --stat "${base_ref}...HEAD"
  echo

  echo "== CHANGED FILES (${base_ref}...HEAD) =="
  git diff --name-status "${base_ref}...HEAD"
  echo
else
  echo "WARNING: base ref ${base_ref} not found locally"
  echo
fi

echo "== WORKTREE STATUS =="
git status --short
echo

if [[ -f "${template_path}" ]]; then
  echo "== PR TEMPLATE PATH =="
  echo "${template_path}"
  echo
  echo "== PR TEMPLATE =="
  cat "${template_path}"
  echo
else
  echo "== PR TEMPLATE PATH =="
  echo "MISSING"
  echo
fi
