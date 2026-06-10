# Participant Quickstart

Welcome to the Quantum Device Workshop! This guide gets you from "I have the
launchable link" to "I'm running the tutorials and writing my own code" in a few
minutes. No local installation is required — everything runs in your cloud
workspace.

You can work however you prefer:

- **Section 1 — Your own IDE** (VS Code / Cursor): edit and run notebooks with
  your familiar editor, autocomplete, and debugger.
- **Section 2 — Browser (JupyterLab)**: nothing to install locally; just open a
  tab.
- **Section 3 — GUI apps in the browser** (KLayout, the Qiskit Metal GUI): for
  the design project, when you want to open real desktop tools.

Pick one to start — you can switch anytime; they all share the same files and
environment.

---

## Step 0 — Create your workspace

1. Open the launchable link the organizers sent you.
2. Choose the **recommended workspace size: `TBD`** *(organizers will confirm the
   exact instance before the event)*. This workshop is **CPU‑only — you do not
   need a GPU.** The simulations (Palace) run on CPU cores, so a GPU would add
   cost without making anything faster.
3. Create the workspace and wait for it to finish starting.

On the **first** start, the workspace automatically pulls the prebuilt workshop
image and launches everything (this one‑time step takes a few minutes). When
it's done, two services are already running inside your workspace:

| Service | Port | What it's for |
|---|---|---|
| JupyterLab | `8888` | Run the notebooks in your browser (Section 2) |
| Web desktop (noVNC) | `6080` | Open GUI apps like KLayout (Section 3) |

You don't need to start anything by hand — both come back automatically every
time you resume the workspace.

> **Accessing a port.** In the Brev console, open your workspace and use its
> port/URL access to reach port `8888` (Jupyter) or `6080` (desktop). If you
> prefer the CLI, you can forward a port to your laptop:
> ```bash
> brev port-forward <your-workspace-name> --port 8888:8888
> # then open http://localhost:8888
> ```

---

## Section 1 — Connect your IDE (VS Code or Cursor)

This is the best path if you want autocomplete, an integrated terminal, and a
debugger while writing code for the design project.

1. **Open the workspace in your editor.** From the Brev console choose
   **Open in VS Code** (or use Remote‑SSH to the workspace). Cursor uses the same
   Remote‑SSH flow.
2. **Attach to the running container.** The environment lives in a Docker
   container called `dev`. Install the **Dev Containers** extension, then run
   *"Dev Containers: Attach to Running Container…"* and pick the `dev` container.
   *(Alternatively, from a workspace terminal: `docker compose -f compose.deploy.yaml exec dev bash`.)*
3. **Open the materials folder:** `/home/ubuntu/qdw-workshop-materials`.
4. **Open a notebook** under `workshops/…/notebooks/` and, when prompted for a
   kernel, choose the **Python 3** interpreter at
   `/home/ubuntu/qdw-workshop-materials/.venv/bin/python`.
5. Run cells normally. Breakpoints and the debugger work — `debugpy` is included.

Everything you save here is the same set of files you'd see in JupyterLab.

---

## Section 2 — Run notebooks in your browser (JupyterLab)

The zero‑setup path.

1. Open port **`8888`** for your workspace (see "Accessing a port" above).
2. JupyterLab opens directly — no password or token needed (your workspace is
   already private to you).
3. In the file browser on the left, open:
   - `workshops/quantum-device-design/notebooks/` — start at `01_welcome.ipynb`
     and work upward (`02_…`, `03_…`, `04_…`, `05_project.ipynb`).
   - `workshops/electromagnetic-simulations/notebooks/` — `eigenmode_EPR.ipynb`
     and `electrostatic_LOM.ipynb`.
4. Run cells with **Shift+Enter**. Layout previews and plots render inline.

---

## Section 3 — Open GUI apps in your browser (design project)

For the open‑ended design project you may want real desktop tools — **KLayout**
to inspect a GDS layout, or the **Qiskit Metal GUI**. These run on a lightweight
Linux desktop inside your workspace that you reach from a browser tab. No
XQuartz / VcXsrv / X‑server setup needed.

1. Open port **`6080`** for your workspace and go to `/vnc.html` (e.g.
   `http://localhost:6080/vnc.html` if you port‑forwarded), then click
   **Connect**.
2. You'll see a desktop. **Right‑click the desktop background** to open the
   menu:
   - **Terminal** — a shell already in the materials directory.
   - **KLayout** — open a `.gds` file via *File → Open* (export one from a
     notebook first, e.g. with `design.export_to_gds(...)`).
   - **ParaView** — inspect Palace field results.
3. To open the **Qiskit Metal Qt GUI**, use a desktop **Terminal** and run:
   ```python
   python
   >>> from qiskit_metal import designs, MetalGUI
   >>> design = designs.DesignPlanar()
   >>> gui = MetalGUI(design)
   ```
   The window appears on the web desktop.

> Notebooks themselves always render **inline** (the kernel is intentionally
> headless), so the GUI desktop is only needed when you explicitly want a
> separate application window.

### Power‑user alternative: X11 over SSH

If you'd rather have native windows on your own machine, you can forward X11
over SSH instead of using the web desktop. This requires a local X server
(XQuartz on macOS, VcXsrv on Windows; Linux works out of the box). See
[gui-forwarding.md](gui-forwarding.md).

---

## Pause between sessions, resume in seconds

To preserve your allotted compute, **pause (stop) your workspace whenever you're
not actively using it** — during lectures, breaks, and overnight.

- **Pause:** stop the workspace from the Brev console (or `brev stop <name>`).
- **Resume:** start it again (or `brev start <name>`). JupyterLab and the desktop
  **restart automatically** — just reopen the port `8888` / `6080` URLs. Resume
  is fast because the image is already cached on your workspace disk; nothing is
  rebuilt or re‑downloaded.

You do **not** need to re‑run any setup commands on resume.

---

## Saving your work

- Files you edit inside the materials directory **persist across pause/resume**.
- For a permanent copy you keep after the workshop, either **download** notebooks
  from JupyterLab (right‑click → Download) or push to your **own** git repo.
- Don't rely on the workspace as long‑term storage — back up anything important
  before the workshop ends.

---

## Quick troubleshooting

| Symptom | Fix |
|---|---|
| Jupyter / desktop tab won't load right after resume | Give it ~15–30s to restart, then refresh. |
| "Kernel not found" in your IDE | Select `/home/ubuntu/qdw-workshop-materials/.venv/bin/python`. |
| A simulation is slow | Expected — Palace is CPU/MPI. Don't add a GPU; it isn't used. |
| Web desktop is black | Click into it once; if still black, refresh `/vnc.html` and **Connect** again. |
| Lost the port URL | Reopen it from the Brev console, or re‑run `brev port-forward`. |

Stuck? Reach the organizers at **quantum.ucla@gmail.com**.
