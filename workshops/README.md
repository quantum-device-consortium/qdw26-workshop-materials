# Workshops

Each workshop lives in its own folder and declares its entrypoints,
dependencies, and smoke checks in `workshop.yaml`.

## Current Materials

- `quantum-device-design/`: Qiskit Metal, Palace, and SQDMetal tutorial materials.
- `electromagnetic-simulations/`: Qiskit Metal, Palace, and pyPalace tutorial materials.

## Required Layout

```text
workshops/<slug>/
  README.md
  workshop.yaml
  notebooks/
  assets/
  references/
```

Optional files such as Binder notes, datasets, or helper scripts should stay inside the workshop folder unless they are useful across multiple workshops.
