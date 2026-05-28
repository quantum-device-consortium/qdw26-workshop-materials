#!/usr/bin/env bash
set -euo pipefail

repo_url="${QDW_REPO_URL:-https://github.com/quantum-device-consortium/qdw26-workshop-materials.git}"
repo_dir="${QDW_REPO_DIR:-$HOME/qdw26-workshop-materials}"

mkdir -p "$HOME/.ssh"
known_hosts="$HOME/.ssh/known_hosts"
touch "$known_hosts"
chmod 600 "$known_hosts"

if command -v curl >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  tmp_known_hosts="$(mktemp)"
  cp "$known_hosts" "$tmp_known_hosts"
  curl -fsSL https://api.github.com/meta \
    | python3 -c 'import json, sys; print("\n".join(f"github.com {key}" for key in json.load(sys.stdin)["ssh_keys"]))' \
    >> "$tmp_known_hosts"
  sort -u "$tmp_known_hosts" > "$known_hosts"
  rm -f "$tmp_known_hosts"
else
  echo "curl and python3 are required to load GitHub SSH host keys from GitHub metadata." >&2
  exit 1
fi

if [[ -d "$repo_dir/.git" ]]; then
  git -C "$repo_dir" pull --ff-only
else
  git clone "$repo_url" "$repo_dir"
fi

QDW_COMPOSE_FILE="${QDW_COMPOSE_FILE:-docker-compose.yml}" bash "$repo_dir/scripts/brev-setup.sh"
