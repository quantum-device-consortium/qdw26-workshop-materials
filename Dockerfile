# syntax=docker/dockerfile:1
FROM abhishekchak52/palace_env:latest

# Runtime libs for PySide6 / Qt6 (X11, xcb, GL/EGL, fonts) — common import failures without these.
RUN apt-get update && apt-get install -y \
	git \
    gmsh \
	paraview \
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

# Note on Python install location:
# Earlier versions of this Dockerfile set UV_PYTHON_INSTALL_DIR=/opt/uv-python
# to keep the managed Python in a shared location (both root at build time
# and the ubuntu user at runtime). But uv 0.11.x silently ignores that env
# var (and the --install-dir flag) for the install step — Python lands in
# /root/.local/share/uv/python regardless — while still respecting it for
# the lookup step, producing "Python interpreter not found" errors.
# Dropping the override here so install and lookup both use uv's default.
# The venv created by ``uv sync`` lives at .venv/ (chowned to ubuntu via
# the COPY below) and contains a symlink to the managed Python in
# /root/.local/share/uv/python. The chown line further down ensures the
# ubuntu user can read those Python files at runtime.

WORKDIR /home/ubuntu/qdw-workshop-materials

# uv sync installs Python (since UV_PYTHON_DOWNLOADS=automatic) and the
# project deps in one shot — keeping install and lookup paths consistent.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --locked --no-install-project

# Copy workshop materials after dependency installation so dependency layers stay cacheable.
COPY --chown=ubuntu:ubuntu . /home/ubuntu/qdw-workshop-materials

# Chown the workshop dir + the uv-managed Python install so the runtime
# ``ubuntu`` user (set below) can read both. /root/.local/share/uv/python
# is where uv 0.11.x puts its managed interpreters; the venv at .venv/
# symlinks into this directory, so it must remain readable post-USER switch.
RUN chown -R ubuntu:ubuntu /home/ubuntu/qdw-workshop-materials \
 && chmod -R a+rX /root/.local/share/uv/python 2>/dev/null || true

ENV PATH="/home/ubuntu/qdw-workshop-materials/.venv/bin:$PATH"


USER ubuntu
