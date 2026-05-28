# QDW Workshop Materials

Joint workspace for **Quantum Device Workshop** materials and the shared environment used by workshop attendees. End-to-end superconducting qubit chip design: **layout → simulation → analysis**, using only open-source tools.

## The toolchain

- **[Quantum Metal](https://github.com/qiskit-community/qiskit-metal)** (formerly Qiskit Metal, v0.7.x): Python-first chip layout and design API. Defines transmons, resonators, CPW routing, and exports to GDS. Lite-by-default install since v0.7.0 — works headless in Docker / Colab / Brev / Codespaces. We use `quantum-metal[full]` here because the workshop exercises the GUI + meshing + EM pieces.
- **[SQDMetal](https://github.com/sqdlab/SQDMetal)** (Sydney Quantum Design lab): integration layer that bridges Quantum Metal designs to open-source EM solvers — handles mesh generation, boundary conditions, post-processing.
- **[Palace](https://github.com/awslabs/palace)** (AWS Labs): scalable open-source FEM solver for full-wave EM and eigenmode simulation. The numerical workhorse behind every simulation in this workshop. Comes pre-installed in the Docker base image (`abhishekchak52/palace_env`).
- **Analytical framework — Energy Participation Ratio (EPR)**: the method we use to extract qubit Hamiltonian parameters (frequencies, anharmonicities, dispersive shifts, cross-Kerr) from the EM eigenmodes Palace computes. Foundational paper: [Minev et al., *Energy-participation quantization of Josephson circuits*, npj Quantum Information (2021)](https://arxiv.org/abs/2010.00620). Quantum Metal's `EPRanalysis` class implements this; see also the [pyEPR-quantum](https://github.com/zlatko-minev/pyEPR) library.

## What Lives Here

- `Dockerfile`, `compose.yaml`, `compose.deploy.yaml`, `pyproject.toml`, `uv.lock`: shared runtime environment.
- `workshops/`: self-contained workshop folders, each with a `workshop.yaml` manifest.
- `shared/`: examples and files intended for more than one workshop.
- `docs/`: attendee, workshop lead, Brev, environment, and deployment security notes.
- `scripts/`: validation, smoke-test, and Brev setup helpers.

## Quick Start

Use whichever access path fits your workflow. All paths should point at the same checked-out materials and shared environment.

```bash
docker compose up --build
```

Then choose an interface:

- JupyterLab: `docker compose exec dev uv run jupyter lab --ip 0.0.0.0 --port 8888 --no-browser`
- Shell: `docker compose exec dev bash`
- VS Code or Cursor: attach to the running `dev` container.
- SSH on Brev: connect to the instance, then use Docker Compose from the repo checkout.
- GUI tools: optional; see `docs/gui-forwarding.md` for display forwarding setup.

Brev/attendee deployments should use the published image:

```bash
docker compose -f compose.deploy.yaml up -d
```

The repository is public so Brev can clone workshop materials without a deploy
key. The attendee image is intended to be public at
`ghcr.io/quantum-device-consortium/qdw-workshop-materials:main` so launchables
can pull it without GHCR credentials. If the image is private, see
[docs/brev.md](docs/brev.md) before creating attendee-facing launchables.

## Current Workshops

- **`workshops/quantum-device-design/`** — 4-notebook progression covering the full Metal × SQDMetal × Palace flow:
  1. `intro_to_layout.ipynb` — Quantum Metal basics: DesignPlanar, components, GDS export, `qm.view()`.
  2. `transmon_resonator.ipynb` — capacitance + eigenmode simulation of a transmon coupled to a readout resonator, EPR analysis extracts qubit frequency / anharmonicity / dispersive shift.
  3. `qubit_qubit_coupling.ipynb` — two-qubit chip with shared bus, eigenmode + EPR for the cross-Kerr.
  4. `project.ipynb` — open-ended design challenge for attendees.

  See [docs/access.md](docs/access.md) for how to run + troubleshooting (Apple Silicon notes, JupyterLab token gotchas, port collisions, …).

## Further reading on the analytical framework

- **EPR (Energy Participation Ratio)** — Minev, Leghtas, et al., [*Energy-participation quantization of Josephson circuits*](https://arxiv.org/abs/2010.00620), npj Quantum Information **7**, 131 (2021). The method behind extracting Hamiltonian parameters from EM eigenmodes.
- **EPR review / tutorial** — Minev, [*Energy participation approach to the design of quantum Josephson circuits*](https://arxiv.org/abs/2010.00620) — concept overview; explains why we care about modal participation ratios when designing real chips.
- **Black-Box Quantization** — Nigg et al., [*Black-Box Superconducting Circuit Quantization*](https://arxiv.org/abs/1204.0587), PRL 108, 240502 (2012). Earlier framework that EPR generalises.
- **Quantum Metal tutorials & docs** — [https://qiskit-community.github.io/qiskit-metal/](https://qiskit-community.github.io/qiskit-metal/) — the upstream package's full tutorial set, including 40+ notebooks covering qubit / resonator / route variants beyond what this workshop touches.

## Contributor Checks

Before opening a pull request:

```bash
python scripts/validate_workshops.py
python scripts/check_notebooks.py
bash -n scripts/*.sh
docker compose config
docker compose -f compose.deploy.yaml config
```

If Docker is running locally, also build and smoke-test the image:

```bash
docker build -t qdw-workshop-materials:local .
docker run --rm qdw-workshop-materials:local python scripts/smoke_environment.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/workshop-lead-guide.md](docs/workshop-lead-guide.md) for the workflow for adding or updating workshop materials.
See [docs/deployment-security.md](docs/deployment-security.md) for deployment security expectations.
