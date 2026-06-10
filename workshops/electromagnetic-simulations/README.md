# Simulating **Qiskit Metal** Designs with **Palace** and **pyPalace**

## Start Here

**Prerequisite:** complete the transmon–resonator layout in the
[`quantum-device-design`](../quantum-device-design/) workshop —
[`notebooks/03_transmon_and_resonator.ipynb`](../quantum-device-design/notebooks/03_transmon_and_resonator.ipynb).
This workshop reuses that chip geometry and walks through FEM simulation with pyPalace.

Recommended notebooks (in order):

1. [`notebooks/eigenmode_EPR.ipynb`](notebooks/eigenmode_EPR.ipynb) — eigenmode + EPR analysis
2. [`notebooks/electrostatic_LOM.ipynb`](notebooks/electrostatic_LOM.ipynb) — electrostatic + LOM analysis

Supporting files are in `assets/` and `references/`. Reference papers should
be cited or linked unless redistribution rights are explicit.

## Overview

This tutorial is interwoven with a lecture led by Sara Sussman. During the lecture, we will learn about the fundamentals of finite element method (FEM) simulations for superconducting circuits, including:

* Why we need electromagnetic simulations to design superconducting circuits.
* What geometry and physics a simulation must encompass.
* Open questions and challenges in superconducting circuit modeling.
* What meshing is and why we need it.
* Different simulation types and analysis methods used to extract quantum device parameters.
* The classical equations FEM simulations actually solve.

The hands-on portion introduces FEM concepts for superconducting circuits using [pyPalace](https://github.com/FirasAbouzahr/pyPalace), a Python wrapper for AWS Palace with utilities for analyzing superconducting qubits. We simulate the same transmon–resonator device built in the quantum-device-design workshop.

Unlike higher-level frameworks, `pyPalace` is intentionally low-level, exposing Palace's native configuration schema directly through a Python API. For this tutorial, that provides an excellent opportunity to learn FEM concepts by working directly with the ingredients of a simulation, including:

* How to define materials and the electromagnetic properties assigned to them.
* How to define boundary conditions, which ones are commonly used in superconducting quantum device modeling, and why.
* How simulation parameters influence both accuracy and computational cost.

For researchers, the low-level nature of pyPalace provides direct access to all of Palace's capabilities, giving users complete control over simulation setup, solver configuration, and post-processing workflows. While pyPalace includes direct integration with Qiskit Metal, it is not tied to any specific CAD or meshing workflow. Any geometry and mesh compatible with Palace can be imported, allowing users to leverage their preferred design and mesh generation tools. For consistency with the Quantum Device Workshop, however, we use the Qiskit Metal → pyPalace workflow throughout this tutorial.

**About pyPalace**

[pyPalace](https://github.com/FirasAbouzahr/pyPalace/tree/main)
([docs](https://pypalace.readthedocs.io/en/latest/), [examples](https://github.com/FirasAbouzahr/pyPalace/tree/main/Examples))

pyPalace is an open-source Python toolkit built around AWS Palace for the simulation and analysis of superconducting quantum devices. It enables users to build Palace configuration files, run simulations locally or on HPC systems, visualize computed electromagnetic fields, and extract simulation results through streamlined Python workflows.

For superconducting devices, pyPalace includes quantum analysis tools based on methods such as Lumped Oscillator Modeling (LOM) and Energy Participation Ratio (EPR), along with related techniques for extracting important physical parameters of superconducting circuits and qubits.

> pyPalace is a community-driven project currently developed and maintained by a single contributor. If you'd like to help shape its future, contributions are warmly encouraged.

**Requirements**

The shared repository environment installs Qiskit Metal, SQDMetal, Palace, and (once consolidated by maintainers) pyPalace. If you need additional packages for this workshop, add them to `workshop.yaml` first so maintainers can wire them into the shared environment.

Let us begin the exploration.
