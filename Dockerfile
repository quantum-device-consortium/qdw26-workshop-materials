# syntax=docker/dockerfile:1
FROM abhishekchak52/palace_env:latest

ENV PALACE_BIN=/opt/qdw/bin/palace
RUN set -eux; \
    palace_path="$(command -v palace)"; \
    test -x "$palace_path"; \
    mkdir -p "$(dirname "$PALACE_BIN")"; \
    printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$palace_path" > "$PALACE_BIN"; \
    chmod +x "$PALACE_BIN"; \
    test -x "$PALACE_BIN"; \
    runuser -u ubuntu -- "$PALACE_BIN" --version

# Runtime libs for PySide6 / Qt6 (X11, xcb, GL/EGL, fonts) — common import failures
# without these — plus a lightweight in-browser desktop (TigerVNC + fluxbox + noVNC)
# so attendees can open GUI apps (KLayout, the Qiskit Metal GUI) from a browser tab
# during the design project without any local X server. Managed by supervisor.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	git \
    gmsh \
	klayout \
	paraview \
	python3-paraview \
	supervisor \
	tigervnc-standalone-server \
	tigervnc-common \
	fluxbox \
	novnc \
	websockify \
	xterm \
	dbus-x11 \
	libdbus-1-3 \
	libdrm2 \
	libegl1 \
	libfontconfig1 \
	libfreetype6 \
	libgbm1 \
	libgl1 \
	libgl1-mesa-dri \
	libglib2.0-0 \
	libgles2 \
	libglu1-mesa \
	libice6 \
	libopengl0 \
	libsm6 \
	libx11-6 \
	libx11-xcb1 \
	libxcb-cursor0 \
	libxcb-icccm4 \
	libxcb-image0 \
	libxcb-keysyms1 \
	libxcb-randr0 \
	libxcb-render0 \
	libxcb-render-util0 \
	libxcb-shape0 \
	libxcb-shm0 \
	libxcb-sync1 \
	libxcb-xfixes0 \
	libxcb-xinerama0 \
	libxcb1 \
	libxext6 \
	libxi6 \
	libxkbcommon0 \
	libxkbcommon-x11-0 \
	libxrender1 \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*


# Copy uv from astral-sh/uv:0.11.2
COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /uvx /bin/

ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=automatic
ENV UV_PYTHON_INSTALL_DIR=/opt/qdw/uv-python

WORKDIR /home/ubuntu/qdw-workshop-materials

# Keep uv-managed Python outside /root so the runtime ubuntu user can execute
# the virtualenv interpreter without broadening root directory permissions.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv python install \
    && python_path="$(uv python find --managed-python --no-project "$(cat .python-version)")" \
    && uv sync --locked --no-install-project --python "$python_path"
# NOTE: debugpy is intentionally kept (it ships transitively via ipykernel). It is
# what lets attendees set breakpoints / use the VS Code & Cursor debuggers against
# the kernel in this container, so it must NOT be uninstalled.

# Copy workshop materials after dependency installation so dependency layers stay cacheable.
COPY --chown=ubuntu:ubuntu . /home/ubuntu/qdw-workshop-materials

RUN chown -R ubuntu:ubuntu /home/ubuntu/qdw-workshop-materials \
 && chmod -R a+rX /opt/qdw/uv-python \
 && runuser -u ubuntu -- /home/ubuntu/qdw-workshop-materials/.venv/bin/python -c "import matplotlib.font_manager as fm; fm._load_fontmanager(try_read_cache=False)"

ENV PATH="/home/ubuntu/qdw-workshop-materials/.venv/bin:$PATH"
ENV PYTHONPATH="/home/ubuntu/qdw-workshop-materials/shared/python"


USER ubuntu
ENTRYPOINT ["/home/ubuntu/qdw-workshop-materials/scripts/container-entrypoint.sh"]
