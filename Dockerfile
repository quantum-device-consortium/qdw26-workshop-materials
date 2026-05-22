# syntax=docker/dockerfile:1
FROM abhishekchak52/palace_env:latest

# Runtime libs for PySide6 / Qt6 (X11, xcb, GL/EGL, fonts) — common import failures without these.
RUN apt-get update && apt-get install -y \
	git \
    gmsh \
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
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python
# Force uv sync to download missing Pythons (default in some versions but
# explicit here so behaviour is the same across uv minor versions).
ENV UV_PYTHON_DOWNLOADS=automatic

# Ensure the install dir exists + is writable BEFORE uv tries to use it.
# Without this, uv 0.11.x silently falls back to its user default
# (/root/.local/share/uv/python) while ``uv sync`` still looks at
# /opt/uv-python — producing the install/lookup mismatch.
RUN mkdir -p /opt/uv-python && chmod 755 /opt/uv-python

WORKDIR /home/ubuntu/qdw-workshop-materials

# Single step: sync installs Python (via UV_PYTHON_DOWNLOADS=automatic)
# AND project deps. Doing both in one ``uv`` invocation guarantees that
# the install location and the lookup location agree.
RUN --mount=type=cache,target=/home/ubuntu/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    set -e ; \
    echo "=== /opt/uv-python before sync ==="; \
    ls -la /opt/uv-python; \
    uv sync --locked --no-install-project ; \
    echo "=== /opt/uv-python after sync ==="; \
    ls -la /opt/uv-python

# Copy workshop materials after dependency installation so dependency layers stay cacheable.
COPY --chown=ubuntu:ubuntu . /home/ubuntu/qdw-workshop-materials

RUN chown -R ubuntu:ubuntu /home/ubuntu/qdw-workshop-materials /opt/uv-python

ENV PATH="/home/ubuntu/qdw-workshop-materials/.venv/bin:$PATH"


USER ubuntu
