# Access Paths

The attendee environment should be usable from several entry points. None of these paths is the only supported path.

## JupyterLab

Use JupyterLab for notebook-first workshops:

```bash
docker compose exec dev uv run jupyter lab --ip 0.0.0.0 --port 8888 --no-browser
```

Open the URL printed by JupyterLab.

## VS Code Or Cursor

Use an editor when you want a full project tree, terminals, and notebook support in one place.

1. Start the environment with `docker compose up -d --build`.
2. Attach the editor to the running `dev` container.
3. Open `/home/ubuntu/qdw-workshop-materials`.

## SSH

Use SSH on Brev or another remote host when terminal access is the most direct route:

```bash
cd qdw-workshop-materials
docker compose up -d
docker compose exec dev bash
```

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

**Two paths forward, in order of effort:**

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

2. Run the workshop **outside Docker** on a machine with a display. Install
   the dependencies locally:
   ```bash
   pip install 'quantum-metal[full]' sqdmetal
   # plus install palace separately — see https://github.com/awslabs/palace
   ```
   Then open the notebooks in your local Jupyter — `MetalGUI(design)` will
   open a window and `gui.rebuild()` / `gui.screenshot()` will work.

   This costs you the Docker workflow but gains the interactive Qt GUI.
   Native install also drops the ~2-3× QEMU slowdown on Apple Silicon.

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
