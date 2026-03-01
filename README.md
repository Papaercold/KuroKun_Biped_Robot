# KuroKun Biped Robot — Official Design Documentation

KuroKun is an open-source bipedal robot platform. This repository serves as the **official design documentation** for KuroKun, covering mechanical design, simulation, and real-world deployment.

---

## Overview

KuroKun is a fully 3D-printed bipedal robot driven by **LX-16A serial bus servos** and a **Raspberry Pi** controller. The project demonstrates a complete pipeline from simulation to hardware, including bipedal locomotion training in **NVIDIA Isaac Sim** and **sim-to-real transfer** to the physical platform.

---

## Hardware

| Component | Details |
|---|---|
| Actuators | LX-16A Serial Bus Servo |
| Controller | Raspberry Pi 4B |
| Power Supply | 6V 12W |
| Structure | Fully 3D-printed body |

### Motor Configuration

KuroKun uses **4 motors per leg** (8 total), arranged as follows. The robot's forward-facing direction is defined as the **+X axis**.

| Joint | Count | Rotation Axis | Description |
|---|---|---|---|
| Hip (roll) | 1 | X axis | Lateral leg abduction / adduction |
| Hip (pitch) | 1 | Y axis | Forward / backward leg swing |
| Knee | 1 | Y axis | Knee flexion / extension |
| Ankle | 1 | Y axis | Ankle flexion / extension |

---

## 3D Printing Configuration

All structural parts are printed with the following slicer settings (PrusaSlicer, tested on **Original Prusa CORE One**).

| Parameter | Value |
|---|---|
| Printer | Original Prusa CORE One |
| Slicing Profile | Prusa Core one |
| Nozzle Diameter | 0.4 mm |
| Print Profile | 0.20mm SPEED |
| Filament | Generic PLA |
| Layer Thickness | 0.2 mm |
| Perimeters | 3 |
| Infill Density | 15% |
| Infill Pattern | Grid |
| Brim Type | No brim |
| Support Type | Organic (on build plate only) |

**Temperature settings:**

| | Bed (°C) | Nozzle (°C) |
|---|---|---|
| First Layer | 60 | 230 |
| Other Layers | 60 | 220 |

---

## Simulation & Sim-to-Real

Bipedal locomotion was developed and trained in **NVIDIA Isaac Sim**, then transferred to the physical KuroKun hardware. The sim-to-real pipeline bridges the gap between the simulated environment and real-world dynamics.

---

## Repository Structure

```
KuroKun_Biped_Robot/
├── 3DPrintDocuments/   # 3D print files for all structural parts
├── FusionDocuments/    # Fusion 360 CAD source files
├── README.md           # This file (English)
└── README_CN.md        # 中文文档
```

---

## License

This project is open source. See LICENSE for details.
