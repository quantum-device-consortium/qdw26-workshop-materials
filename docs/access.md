# Access Paths

The workshop environment supports several access paths. Each path uses the same
repository checkout and shared runtime.

> **Participants:** the simplest path is
> [participant-quickstart.md](participant-quickstart.md). JupyterLab (port
> `8888`) and a noVNC web desktop (port `6080`, `/vnc.html`) auto-start in the
> workspace — there is nothing to launch by hand. The notes below are mainly for
> maintainers and local development.

## Hosted Workspace Flow

Participants using hosted compute should start from the workshop launchable and
the event credit code provided by the organizers.

Typical flow:

1. Open the launchable or access link distributed by the organizers.
2. Sign in and apply the event credit code, if required.
3. Create a workspace using the workshop-provided configuration.
4. Choose an interface: browser JupyterLab (port `8888`), the noVNC web desktop
   (port `6080`), browser terminal, SSH, or VS Code/Cursor.
5. Open the relevant folder under `workshops/`.
6. Follow that workshop's `README.md`.
7. Stop the workspace when not in a scheduled workshop session.

Workspace access instructions, participant lists, and credit-code distribution
are handled through event-approved channels and are not stored in this
repository.

Use the prebuilt GHCR image for hosted workspaces. Do not rebuild the workshop
image during participant startup:

```bash
cd ~/qdw26-workshop-materials
bash scripts/brev-setup.sh
```

For a same-workspace resume when no image update has been announced:

```bash
cd ~/qdw26-workshop-materials
QDW_PULL_IMAGE=0 bash scripts/brev-setup.sh
```

See [workspace persistence](workspace-persistence.md) for stop/start and
state-preservation guidance.

## JupyterLab

JupyterLab auto-starts inside the container. Both `compose.yaml` (dev) and
`compose.deploy.yaml` (attendee) run `scripts/start-services.sh`, which launches
JupyterLab on port `8888` (and the noVNC web desktop on port `6080`) under
supervisor. There is no manual `jupyter lab` command to run.

Just open the port-`8888` URL. JupyterLab is tokenless by default — access is
gated by the Brev workspace proxy. To set a token anyway, provide the
`QDW_JUPYTER_TOKEN` environment variable.

Both published ports bind to `${QDW_BIND:-127.0.0.1}` by default; hosted
launchables expose `8888` (and `6080`) through Brev's authenticated proxy.

## noVNC Web Desktop

A noVNC web desktop also auto-starts on port `6080` at path `/vnc.html`. Open it
in a browser to reach GUI applications (Terminal, KLayout, ParaView) without a
local X server. See [GUI forwarding](gui-forwarding.md).

## VS Code Or Cursor

Use an editor for a full project tree, terminals, and notebook support in one
place.

Hosted workspace:

1. Start the environment with `bash scripts/brev-setup.sh`.
2. Attach the editor to the running `dev` container.
3. Open `/home/ubuntu/qdw-workshop-materials`.

Local development:

1. Start the environment with `docker compose up -d --build`.
2. Attach the editor to the running `dev` container.
3. Open `/home/ubuntu/qdw-workshop-materials`.

## SSH

Use SSH on Brev or another remote host when terminal access is the most direct
route:

```bash
cd qdw26-workshop-materials
bash scripts/brev-setup.sh
docker compose -f compose.deploy.yaml exec dev bash
```

## GUI Applications

The recommended way to open GUI apps (KLayout, the Quantum Metal GUI, ParaView)
is the built-in noVNC web desktop on port `6080` (`/vnc.html`) — open it in a
browser and right-click the desktop for Terminal/KLayout/ParaView. No local X
server is required. X11-over-SSH forwarding remains available as a secondary
path for power users who want native windows.

See [GUI forwarding](gui-forwarding.md) for the web desktop and X11/SSH setup notes.

## Local Terminal

Use Docker Compose directly when developing locally:

```bash
docker compose up --build
docker compose exec dev bash
```

All paths use the same repository checkout and shared environment.

---

## Troubleshooting

### Apple Silicon (M1/M2/M3/M4 Macs)

The base image `abhishekchak52/palace_env:latest` is **amd64-only** (no
arm64 variant). On Apple Silicon, Docker must run it under QEMU emulation.

`compose.yaml` pins `platform: linux/amd64` to make this consistent.
Without it, `uv sync` inside the container
detects the host arch (arm64) but the container itself is emulated amd64,
producing the cryptic build failure:

```
error: Python interpreter not found at
  /root/.local/share/uv/python/cpython-3.12.13-linux-aarch64-gnu/...
```

Expect a ~2–3× slowdown vs native on Apple Silicon (unavoidable until the
base image ships a multi-arch manifest). Native Linux / Intel Mac users
are unaffected by the pin.

### JupyterLab does not need a token

JupyterLab is tokenless by default — open the port-`8888` URL directly with no
token or password. Access is gated by the Brev workspace proxy. If you set
`QDW_JUPYTER_TOKEN`, append `?token=<value>` to the URL.

### Browser shows the wrong file tree at `localhost:8888`

**Symptom:** opening `http://localhost:8888/` shows an unrelated project instead
of `workshops/quantum-device-design/notebooks/`.

**Cause:** another JupyterLab process is already running locally on port 8888.
macOS routes `localhost:8888` to the local process before the Docker-mapped
one.

Two fixes:

```bash
# Option A: stop the local jupyter; localhost:8888 → Docker
lsof -i :8888 | grep -v COMMAND     # find the local PID
kill <PID>
# then hard-refresh browser

# Option B: bind the container's published ports to a different host address.
# Both compose files publish 8888 and 6080 on ${QDW_BIND:-127.0.0.1}; override
# QDW_BIND to move them off the conflicting localhost:
QDW_BIND=127.0.0.2 docker compose up -d --force-recreate
# then open http://127.0.0.2:8888/
```

### `MetalGUI(design)` fails with "could not connect to display" / `xcb` errors

```
WARNING: could not connect to display
WARNING: xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin
INFO: Could not load the Qt platform plugin "xcb"
```

The Docker container has no X server or display by default. The Qt-based
`MetalGUI` class needs GUI forwarding or a local desktop environment.

Recommended options:

1. Use the headless viewer instead. Anywhere you see:
   ```python
   gui = MetalGUI(design)
   gui.rebuild()
   gui.screenshot('foo.png')
   ```
   replace with the single line:
   ```python
   qm.view(design)   # returns a matplotlib.figure.Figure, renders inline
   ```
   This uses the same render path as GDS export and works in Docker, Brev,
   Codespaces, and other non-Qt environments.

2. Set up GUI forwarding to your laptop's display server (XQuartz on macOS,
   native X11 on Linux, VcXsrv/X410 on Windows). See [gui-forwarding.md](gui-forwarding.md)
   for the full setup. Once forwarding is connected, launch the notebook
   server with `DISPLAY` passed through and `MetalGUI(design)` will open a Qt
   window on the local machine.

3. Run the workshop **outside Docker** on a machine with a display. Install
   the dependencies locally:
   ```bash
   pip install 'quantum-metal[full]' sqdmetal
   # plus install palace separately — see https://github.com/awslabs/palace
   ```
   Then open the notebooks in your local Jupyter — `MetalGUI(design)` will
   open a window and `gui.rebuild()` / `gui.screenshot()` will work.

   This trades the Docker workflow for native GUI behavior.

### `palace --version` exits with "Illegal instruction" on Apple Silicon

```
/home/abhis/spack/opt/spack/linux-zen2/palace-.../bin/palace: line 179:
   157 Illegal instruction     $MPIRUN $PALACE $CONFIG
subprocess.CalledProcessError: Command '['palace', '--version']'
   returned non-zero exit status 132.
```

Exit 132 = SIGILL. The Palace binary in the base image is spack-built for
`linux-zen2` — AMD Zen2 microarchitecture, which uses AVX2 instructions
that QEMU's x86_64 emulator on Apple Silicon does not fully support. The
binary crashes the moment it executes one.

Impact:

- Notebooks 1 & 2 (`01_welcome.ipynb`, `02_first_chip_layout.ipynb`) — pure
  Metal layout, unaffected.
- Notebooks 3 & 4 (`03_transmon_and_resonator.ipynb`,
  `04_qubit_qubit_coupling.ipynb`) — the design / mesh / `qm.view()` parts all
  work, but the actual Palace eigenmode / capacitance solve step will SIGILL.
  The same applies to the electromagnetic-simulations notebooks
  (`eigenmode_EPR.ipynb`, `electrostatic_LOM.ipynb`).
- Notebook 5 (`05_project.ipynb`) — depends on what design you build.

**Fixes:**

1. **Run the solves on a native amd64 host.** Brev's Linux/x86 instances,
   any Intel/AMD Linux box, or an Intel Mac all have native AVX2 and run
   Palace at full speed.
2. **Local-only iteration:** do layout work on your M-series Mac (notebooks 1 &
   2, plus the layout cells of 3 & 4), then push the design to a Brev instance
   for the Palace solve.

Native amd64 Linux, Intel Mac, and Brev users are unaffected.

### `gmsh-4.15.2.data` directory not empty on container startup

If a previous `uv sync` was interrupted and you cleaned `.venv/` on the
host, you may hit:

```
error: Failed to install: gmsh-4.15.2-py2.py3-none-manylinux_2_24_x86_64.whl
  Caused by: failed to remove directory
    `.venv/lib/python3.12/site-packages/gmsh-4.15.2.data`: Directory not empty
```

Caused by a partial install leaving a non-empty data dir that uv's
atomic-replace can't overwrite. Fix:

```bash
docker compose down
rm -rf .venv
docker compose up -d   # container will uv sync cleanly into a fresh .venv
```
