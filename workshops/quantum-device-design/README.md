# Quantum Device Design

## Start Here

Recommended notebook sequence:

1. `notebooks/01_welcome.ipynb`
2. `notebooks/02_first_chip_layout.ipynb`
3. `notebooks/03_transmon_and_resonator.ipynb`
4. `notebooks/04_qubit_qubit_coupling.ipynb`
5. `notebooks/05_project.ipynb`

Supporting files are in `assets/` and `references/`. Reference papers should
be cited or linked unless redistribution rights are explicit.

## Overview

This workshop introduces an open-source workflow for superconducting quantum
device design. Participants create layouts with [Quantum Metal](https://github.com/qiskit-community/qiskit-metal),
prepare simulations with [SQDMetal](https://github.com/sqdlab/SQDMetal), and
run electrostatic or eigenmode studies with [Palace](https://github.com/awslabs/palace).

We will learn to:

1. Define superconducting qubit and resonator layouts.
2. Prepare Metal designs for electromagnetic simulation.
3. Run electrostatic and eigenmode workflows.
4. Interpret simulated quantities in the context of circuit design.
5. Build toward an open-ended design exercise.

## Requirements

The shared repository environment installs Quantum Metal, SQDMetal, Palace,
Gmsh, ParaView, KLayout, SQuADDS, scqubits, scikit-rf, PyPalace, meshwell, and
the supporting Python packages listed in the root environment files. Additional
workshop-specific dependency requests should be declared in `workshop.yaml`.

## Background

For additional Quantum Metal examples, see the upstream
[documentation](https://qiskit-community.github.io/qiskit-metal/) and
[tutorials](https://qiskit-community.github.io/qiskit-metal/tut/index.html).
