#!/usr/bin/env bash
set -euo pipefail

socket_path="${QDW_PALACE_RUNNER_SOCKET:-/tmp/qdw-palace-runner.sock}"
export QDW_PALACE_RUNNER_SOCKET="$socket_path"

rm -f "$socket_path"
python -m qdw_workshop.palace_runner_service --socket "$socket_path" &
runner_pid="$!"

cleanup() {
  kill "$runner_pid" >/dev/null 2>&1 || true
  wait "$runner_pid" >/dev/null 2>&1 || true
  rm -f "$socket_path"
}
trap cleanup EXIT INT TERM

for _ in $(seq 1 50); do
  if [[ -S "$socket_path" ]]; then
    break
  fi
  sleep 0.1
done

if [[ ! -S "$socket_path" ]]; then
  echo "Palace runner service did not start at $socket_path" >&2
  exit 1
fi

exec "$@"
