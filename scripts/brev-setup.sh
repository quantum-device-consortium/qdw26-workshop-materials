#!/usr/bin/env bash
set -euo pipefail

repo_dir=""
for candidate in \
  "$HOME/qdw26-workshop-materials" \
  "$HOME/qdw-workshop-materials" \
  "$HOME/workspace/qdw26-workshop-materials" \
  "$HOME/workspace/qdw-workshop-materials" \
  "/home/ubuntu/qdw26-workshop-materials" \
  "/home/ubuntu/qdw-workshop-materials" \
  "/home/ubuntu/workspace/qdw26-workshop-materials" \
  "/home/ubuntu/workspace/qdw-workshop-materials"; do
  if [[ -d "$candidate" ]]; then
    repo_dir="$candidate"
    break
  fi
done

if [[ -z "$repo_dir" ]]; then
  repo_dir="$(find /home/ubuntu -maxdepth 3 -type d \( -name qdw26-workshop-materials -o -name qdw-workshop-materials \) -print -quit 2>/dev/null || true)"
fi

if [[ -z "$repo_dir" ]]; then
  echo "Could not find qdw-workshop-materials checkout on this Brev instance." >&2
  exit 1
fi

cd "$repo_dir"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for the shared workshop environment but was not found." >&2
  exit 1
fi

compose_file="${QDW_COMPOSE_FILE:-compose.deploy.yaml}"
pull_image="${QDW_PULL_IMAGE:-1}"
run_smoke="${QDW_RUN_SMOKE:-1}"
tmp_docker_config=""

cleanup() {
  if [[ -n "$tmp_docker_config" && -d "$tmp_docker_config" ]]; then
    rm -rf "$tmp_docker_config"
  fi
}
trap cleanup EXIT

if [[ ! -f "$compose_file" ]]; then
  echo "Could not find $compose_file in $repo_dir." >&2
  exit 1
fi

if [[ -n "${GHCR_USERNAME:-}" && -n "${GHCR_TOKEN:-}" ]]; then
  tmp_docker_config="$(mktemp -d)"
  export DOCKER_CONFIG="$tmp_docker_config"
  printf '%s' "$GHCR_TOKEN" | docker login ghcr.io --username "$GHCR_USERNAME" --password-stdin
else
  echo "GHCR_USERNAME/GHCR_TOKEN are not set; assuming the image is public or Docker is already authenticated."
fi

compose_cmd=(docker compose -f "$compose_file")

echo "Using repository: $repo_dir"
echo "Using Compose file: $compose_file"

if [[ "$pull_image" == "1" ]]; then
  "${compose_cmd[@]}" pull
else
  echo "Skipping image pull because QDW_PULL_IMAGE=$pull_image."
fi

"${compose_cmd[@]}" up -d --no-build
"${compose_cmd[@]}" ps

if [[ "$run_smoke" == "1" ]]; then
  "${compose_cmd[@]}" exec -T dev python scripts/smoke_environment.py
fi
