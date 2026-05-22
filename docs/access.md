# Access Paths

The attendee environment should be usable from several entry points. None of these paths is the only supported path.

## JupyterLab

Use JupyterLab for notebook-first workshops:

```bash
docker compose -f compose.deploy.yaml exec dev uv run jupyter lab --ip 0.0.0.0 --port 8888 --no-browser
```

Open the URL printed by JupyterLab.

The compose files bind port `8888` to localhost by default. Use Brev's authenticated access or an SSH tunnel for remote access unless the deployment owner intentionally sets `QDW_JUPYTER_BIND=0.0.0.0`.

## VS Code Or Cursor

Use an editor when you want a full project tree, terminals, and notebook support in one place.

1. Start the environment with `docker compose up -d --build`.
2. Attach the editor to the running `dev` container.
3. Open `/home/ubuntu/qdw-workshop-materials`.

## SSH

Use SSH on Brev or another remote host when terminal access is the most direct route:

```bash
cd qdw-workshop-materials
docker compose -f compose.deploy.yaml up -d
docker compose -f compose.deploy.yaml exec dev bash
```

## GUI Applications

GUI applications are optional and need a display server on the attendee's local machine. Use `pvpython`, `pvbatch`, notebooks, or terminal workflows when possible; use GUI forwarding only when a desktop window is actually needed.

See [GUI forwarding](gui-forwarding.md) for macOS, Linux, Windows, and remote-host setup notes.

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

`compose.yaml` pins `platform: linux/amd64` to make this consistent —
**don't remove that line**. Without it, `uv sync` inside the container
detects the host arch (arm64) but the container itself is emulated amd64,
producing the cryptic build failure:

```
error: Python interpreter not found at
  /root/.local/share/uv/python/cpython-3.12.13-linux-aarch64-gnu/...
```

Expect a ~2–3× slowdown vs native on Apple Silicon (unavoidable until the
base image ships a multi-arch manifest). Native Linux / Intel Mac users
are unaffected by the pin.

### JupyterLab token shows as `...` in the log

When JupyterLab starts it prints:

```
Jupyter Server 2.18.2 is running at:
    http://127.0.0.1:8888/lab?token=...
```

Those literal three dots are **JupyterLab masking the token** in log
output (security default in 2.x). The token is NOT `...` — that's just
what you see in the terminal.

To get the real token, read JupyterLab's runtime json directly:

```bash
docker compose exec dev bash -c \
  'cat /home/ubuntu/.local/share/jupyter/runtime/jpserver-*.json' | grep token
```

Or start JupyterLab with an **explicit known token** (avoids the lookup):

```bash
docker compose exec dev uv run jupyter lab \
  --ip 0.0.0.0 --port 8888 --no-browser \
  --IdentityProvider.token=mytoken
# then in browser: http://localhost:8888/?token=mytoken
```

### Browser shows the wrong file tree at `localhost:8888`

**Symptom:** you open `http://localhost:8888/?token=...` and instead of
seeing `workshops/quantum-device-design/notebooks/` you see some
unrelated project's files.

**Cause:** you already have a JupyterLab running locally on port 8888
(e.g. from a `jupyter lab` you started in another terminal hours ago).
macOS routes `localhost:8888` to the local process before the
Docker-port-mapped one.

Two fixes:

```bash
# Option A: stop the local jupyter; localhost:8888 → Docker
lsof -i :8888 | grep -v COMMAND     # find the local PID
kill <PID>
# then hard-refresh browser

# Option B: move Docker to a different host port (both can coexist)
# edit compose.yaml: change "8888:8888" to "8889:8888"
docker compose up -d --force-recreate
# then open http://localhost:8889/?token=...
```

### `MetalGUI(design)` fails with "could not connect to display" / `xcb` errors

```
WARNING: could not connect to display
WARNING: xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin
INFO: Could not load the Qt platform plugin "xcb"
```

The Docker container has **no X server / display** — the Qt-based `MetalGUI`
class cannot work here. The workshop notebooks (`transmon_resonator.ipynb`,
`qubit_qubit_coupling.ipynb`) were originally written for a local install
with a display.

**Three paths forward, in order of effort:**

1. **(Recommended)** Use the headless viewer instead. Anywhere you see:
   ```python
   gui = MetalGUI(design)
   gui.rebuild()
   gui.screenshot('foo.png')
   ```
   replace with the single line:
   ```python
   qm.view(design)   # returns a matplotlib.figure.Figure, renders inline
   ```
   Same render path that GDS export uses — what you see is what you fab.
   Works in Docker, Brev, Codespaces, any non-Qt environment.

2. Set up GUI forwarding to your laptop's display server (XQuartz on macOS,
   native X11 on Linux, VcXsrv/X410 on Windows). See [gui-forwarding.md](gui-forwarding.md)
   for the full setup. Once forwarding is connected, launch the notebook
   server with `DISPLAY` passed through and `MetalGUI(design)` will open
   a real Qt window on your laptop. Best for workshop leads who want the
   full interactive GUI without leaving Docker.

3. Run the workshop **outside Docker** on a machine with a display. Install
   the dependencies locally:
   ```bash
   pip install 'quantum-metal[full]' sqdmetal
   # plus install palace separately — see https://github.com/awslabs/palace
   ```
   Then open the notebooks in your local Jupyter — `MetalGUI(design)` will
   open a window and `gui.rebuild()` / `gui.screenshot()` will work.

   This costs you the Docker workflow but gains the interactive Qt GUI.
   Native install also drops the ~2-3× QEMU slowdown on Apple Silicon.

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

What this means for the workshop:

- Notebook 1 (`intro_to_layout.ipynb`) — pure Metal layout, unaffected.
- Notebooks 2 & 3 (`transmon_resonator.ipynb`, `qubit_qubit_coupling.ipynb`)
  — the design / mesh / `qm.view()` parts all work, but the actual Palace
  eigenmode / capacitance solve step will SIGILL.
- Notebook 4 — depends on what design you build.

**Fixes:**

1. **Run the solves on a native amd64 host.** Brev's Linux/x86 instances,
   any Intel/AMD Linux box, or an Intel Mac all have native AVX2 and run
   Palace at full speed. The workshop's published Brev path is the
   intended end-to-end flow.
2. **Local-only iteration:** do layout work on your M-series Mac (notebook
   1, plus the layout cells of 2 & 3), then push the design to a Brev
   instance for the Palace solve.

Native amd64 Linux / Intel Mac / Brev users are unaffected — Palace runs
normally there.

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
