#!/usr/bin/env bash
set -euo pipefail

repo_url="${QDW_REPO_URL:-git@github.com:quantum-device-consortium/qdw-workshop-materials.git}"
repo_dir="${QDW_REPO_DIR:-$HOME/qdw-workshop-materials}"

mkdir -p "$HOME/.ssh"
ssh-keyscan github.com >> "$HOME/.ssh/known_hosts" 2>/dev/null || true

if [[ -d "$repo_dir/.git" ]]; then
  git -C "$repo_dir" pull --ff-only
else
  git clone "$repo_url" "$repo_dir"
fi

bash "$repo_dir/scripts/brev-setup.sh"
