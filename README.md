🛰️ SPHY Solar System - Orbital Dynamics & Telemetry Auditor

This repository contains the visualization and data analysis ecosystem for the SPHY Engine. The project focuses on the physical auditing of complex orbital trajectories over a 20,000-frame dataset, comparing SPHY's unique physics engine results against classical Newtonian mechanics.
📂 Repository Contents
1. telemetria_solar_sphy.parquet

The core of the project. A high-performance dataset containing:

    20,000 frames of continuous simulation.

    Data for 10 primary bodies (9 planets + Ceres), including moons and the asteroid belt.

    Unified Cartesian position vectors (x,y,z) for scientific auditing.

2. player_solar_system3.py

The Cinematic 3D Viewer.

    Interactive visualizer built with PyQt5 and PyQtGraph.OpenGL.

    Renders the Sun, planets, moons, asteroid belt, and planetary rings.

    Key Feature: Accurate axial tilt implementation for Uranus (vertical/diagonal rings) and a minimalist UI (occupying only 3% of the screen).

3. analisador_sphy_orbital.py

Gravitational Anomaly Detector.

    Compares SPHY's real-time position data against a trajectory calculated via Newton's Inverse-Square Law.

    Generates Residual Error reports and Coherence Signatures.

    Successfully identified a total accumulated deviation of 13.46 AU for Mercury, proving the engine's non-Newtonian signatures.

4. analisador_sphy_orbital1.py

Unification Gradient Map.

    Analyzes the entire solar system gradient, from Mercury to Pluto.

    Calculates the "Deviation Rate" per frame for each celestial body.

    Generates a log-log scale plot mapping how SPHY's influence varies according to the distance from the Sun.

📊 Audit Highlights (20k Frame Analysis)
Metric	Result
Highest Anomaly Detected	Mercury (8.04 AU/frame)
Classical Stability Point	Earth (3.97 AU/frame)
Coherence Factor (α)	1.00000000 (Full Coherence)
🚀 Getting Started

    Ensure the .parquet file is in the same directory as the scripts.

    To visualize the system: python3 player_solar_system3.py

    To audit a specific planet: python3 analisador_sphy_orbital.py

    To generate the system-wide gradient map: python3 analisador_sphy_orbital1.py

Note: This project is part of a series of articles on Gravitic Coherence and serves as a proof-of-concept for non-Newtonian simulation engines.
