#!/usr/bin/env bash
# Attendee entry command: start JupyterLab + the noVNC web desktop under
# supervisor and stay in the foreground so the container keeps running.
#
# The Palace runner service is already started by container-entrypoint.sh (the
# image ENTRYPOINT) before this script is exec'd, so it is not managed here.
set -euo pipefail

export QDW_VNC_GEOMETRY="${QDW_VNC_GEOMETRY:-1440x900}"

# Clear any stale X lock left behind by a previously paused/stopped container so
# that resuming the workspace brings the desktop straight back up.
rm -f /tmp/.X1-lock 2>/dev/null || true
rm -f /tmp/.X11-unix/X1 2>/dev/null || true

mkdir -p /home/ubuntu/.vnc /home/ubuntu/.fluxbox

# Install the right-click desktop menu (Terminal / KLayout / ParaView).
cp -f /home/ubuntu/qdw-workshop-materials/scripts/desktop/fluxbox-menu /home/ubuntu/.fluxbox/menu

exec supervisord -c /home/ubuntu/qdw-workshop-materials/scripts/supervisord.conf -n
