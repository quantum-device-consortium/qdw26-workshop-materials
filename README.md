# QDW Workshop Materials

Shared workshop materials and runtime environment for the Quantum Device
Workshop 2026.

The environment supports layout, electromagnetic simulation, visualization, and
circuit-analysis workflows using Quantum Metal, SQDMetal, Palace, pyPalace,
Gmsh, ParaView, KLayout, SQuADDS, scqubits, scikit-rf, meshwell, and JupyterLab.

## Contents

- [Quick Start](#quick-start)
- [Access Paths](#access-paths)
- [Workshop Materials](#workshop-materials)
- [Contributing](#contributing)
- [Hosted Deployment](#hosted-deployment)
- [Maintainer Checks](#maintainer-checks)
- [AI Agent Setup Prompts](#ai-agent-setup-prompts)

## Quick Start

**Workshop participants:** you don't need anything below — start at
[docs/participant-quickstart.md](docs/participant-quickstart.md). It walks
through launching your cloud workspace and connecting via your IDE or the
browser.

**Local development / maintainers:** start the environment. `docker compose up`
syncs dependencies and then auto-starts JupyterLab (port `8888`) and the noVNC
web desktop (port `6080`):

```bash
docker compose up --build
# JupyterLab:   http://localhost:8888
# Web desktop:  http://localhost:6080/vnc.html
```

For a plain shell instead of the service stack:

```bash
docker compose run --rm dev bash
```

For hosted deployment testing, use the published image (same auto-started
services):

```bash
docker compose -f compose.deploy.yaml pull
docker compose -f compose.deploy.yaml up -d --no-build
```

## Access Paths

Use whichever interface fits the session:

- JupyterLab (port `8888`) for notebooks.
- VS Code or Cursor for editor-based work (attach to the `dev` container).
- SSH or terminal for command-line work.
- noVNC web desktop (port `6080`, `/vnc.html`) for ParaView, KLayout, or the
  Qiskit Metal GUI in a browser tab — no local X server needed. X11-over-SSH
  remains available for native windows.

See [docs/participant-quickstart.md](docs/participant-quickstart.md),
[docs/access.md](docs/access.md), and
[docs/gui-forwarding.md](docs/gui-forwarding.md).

## Workshop Materials

Current materials:

- `workshops/quantum-device-design/`: Quantum Metal, SQDMetal, and Palace
  notebooks.
- `workshops/electromagnetic-simulations/`: Quantum Metal, pyPalace, and Palace
  notebooks for eigenmode/EPR and electrostatic/LOM workflows.

Planned additions:

- Design layout.
- Hamiltonian and circuit analysis.
- EM and circuit analysis.

Each workshop folder should include:

```text
workshops/<slug>/
  README.md
  workshop.yaml
  notebooks/
  assets/
  references/
```

## Contributing

Workshop leads should add or update materials through pull requests.

Before opening a pull request:

```bash
python scripts/validate_workshops.py
python scripts/check_notebooks.py
bash -n scripts/*.sh
docker compose config
docker compose -f compose.deploy.yaml config
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/workshop-lead-guide.md](docs/workshop-lead-guide.md).

## Hosted Deployment

The Brev launchable is kept current through this repository and the published
GHCR image:

```text
ghcr.io/quantum-device-consortium/qdw-workshop-materials:main
```

Participants will receive credit codes and launchable instructions through
workshop channels. Participants should stop Brev workspaces when not in
scheduled workshop sessions and delete them only after saving any needed work.
Workspace configuration, credit-code distribution, and access details will be
finalized separately before the workshop.

Do not commit participant lists, access codes, credentials, or billing records.

See [docs/brev.md](docs/brev.md),
[docs/workspace-persistence.md](docs/workspace-persistence.md), and
[docs/deployment-security.md](docs/deployment-security.md).

## Maintainer Checks

If Docker is running locally, build and smoke-test the image:

```bash
docker build -t qdw-workshop-materials:local .
docker run --rm --platform linux/amd64 qdw-workshop-materials:local python scripts/smoke_environment.py
docker run --rm --platform linux/amd64 \
  -e QISKIT_METAL_HEADLESS=1 \
  -e MPLBACKEND=Agg \
  -e QT_QPA_PLATFORM=offscreen \
  qdw-workshop-materials:local \
  python scripts/run_workshop_execution.py
```

Smoke checks confirm the environment starts. Workshop execution checks run the
manifest-declared attendee notebooks and Python scripts inside the image. The
execution check can take several minutes because it includes simulation
notebooks.

## AI Agent Setup Prompts

<details>
<summary>Copy-paste prompts for coding agents</summary>

Use this repository context before making changes:

```text
You are working in the qdw26-workshop-materials repository.

Goal:
- Maintain a professional workshop repository for Quantum Device Workshop materials.
- Keep the root environment shared across all workshops.
- Keep each workshop self-contained under workshops/<slug>/.
- Preserve support for JupyterLab, VS Code/Cursor, SSH, terminal, and optional GUI forwarding.

Rules:
- Do not commit credentials, participant lists, credit codes, billing data, license files, or private installer files.
- Do not add long generated outputs unless explicitly needed.
- Update workshop.yaml when adding notebooks, assets, dependencies, or smoke checks.
- Run the validation checks before proposing a PR.

Checks:
python scripts/validate_workshops.py
python scripts/check_notebooks.py
bash -n scripts/*.sh
docker compose config
docker compose -f compose.deploy.yaml config
```

Codex:

```text
Please inspect this repository, update only the files needed for the requested
change, preserve the workshop folder structure, run the validation checks, and
summarize the result with file references.
```

Cursor:

```text
Use the repository README and docs as source of truth. Keep edits focused,
update workshop.yaml for workshop content changes, and run the listed checks
before suggesting a commit.
```

Claude:

```text
Review the repository structure first. Make concise, professional changes.
Avoid adding private operational details to public docs. Validate manifests,
notebooks, shell scripts, and Docker Compose before reporting completion.
```

Gemini:

```text
Help maintain this workshop repository. Keep root files for the shared
environment, keep workshop materials under workshops/<slug>/, and verify changes
with the README checks.
```

Antigravity:

```text
Use this repository as a workshop hub. When adding material, keep the workshop
self-contained, declare dependencies in workshop.yaml, and avoid committing
private event or billing information.
```

</details>
