#!/usr/bin/env bash
# Launch JupyterLab with the kernel forced into headless / inline mode.
#
# DISPLAY is intentionally cleared and QT_QPA_PLATFORM=offscreen is set so that
# notebook cells render Qiskit Metal / matplotlib *inline* and never try to open
# a window — even though a real X display (:1) exists in this container for the
# noVNC desktop. Attendees who want the real KLayout / Metal Qt GUI use the web
# desktop instead (a terminal there has DISPLAY=:1). This keeps the two worlds
# cleanly separated: notebooks = inline, desktop = windowed.
set -euo pipefail

cd /home/ubuntu/qdw-workshop-materials

unset DISPLAY
export QISKIT_METAL_HEADLESS=1
export QT_QPA_PLATFORM=offscreen
export MPLBACKEND=Agg

# Tokenless by default: access is already gated by the Brev workspace proxy.
# Set QDW_JUPYTER_TOKEN to require a token instead.
exec .venv/bin/jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --ServerApp.token="${QDW_JUPYTER_TOKEN:-}" \
  --ServerApp.password="" \
  --ServerApp.root_dir=/home/ubuntu/qdw-workshop-materials
