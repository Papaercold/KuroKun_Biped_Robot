# KuroKun Biped Robot — Official Design Documentation

**Language:** English | [中文](README_CN.md)

KuroKun is an open-source bipedal robot platform. This repository serves as the **official design documentation** for KuroKun, covering mechanical design, simulation, and real-world deployment.

---

## Overview

![KuroKun Design Sketch](Design%20sketch.jpg)

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

## Robot Model

The `model/` directory contains the robot description in two formats:

| File | Format | Used by |
|---|---|---|
| `model/kurokun.urdf` | URDF | ROS 2 (visualisation, kinematics) |
| `model/kurokun.usd` | USD | NVIDIA Isaac Sim (physics simulation / training) |

`kurokun.urdf` is a **simplified box-model** for rigid-body dynamics. Every part is approximated as a uniform solid box — visual fidelity is intentionally traded away in favor of correct mass, center of mass, and inertia tensor, which are the only properties that affect dynamics.

### Quick View (ROS 2 Jazzy)

**Install dependencies** (skip if already installed):

```bash
sudo apt install ros-jazzy-robot-state-publisher \
                 ros-jazzy-joint-state-publisher-gui \
                 ros-jazzy-rviz2
```

**Launch:**

```bash
ros2 launch model/view_robot.launch.py
```

This opens three windows simultaneously:
- **RViz2** — 3D visualization with `base_link` as the fixed frame
- **joint_state_publisher_gui** — sliders to move every joint interactively

### Coordinate Convention

| Axis | Direction |
|---|---|
| X | Forward (robot facing direction) |
| Y | Left |
| Z | Up |

### Kinematic Chain

```
base_link  (1 g, kinematic root — no visual)
├── head_link  [fixed]  →  head_link  (65×75.28×42 mm, 250 g, torso body)
├── left_hip_roll   [revolute, X]  →  left_hip_roll_link   (48 g)
│     └── left_hip_pitch  [revolute, Y]  →  left_hip_pitch_link  (48 g)
│           └── [fixed]  →  left_thigh_link  (10 g)
│                 └── left_knee  [revolute, Y]  →  left_knee_link  (48 g)
│                       └── [fixed]  →  left_shank_link  (10 g)
│                             └── left_ankle  [revolute, Y]  →  left_ankle_link  (48 g)
│                                   └── [fixed]  →  left_foot_link  (10 g)
└── right_hip_roll  [revolute, X]  →  (mirror of left leg)
```

### Links

| Link | Box size (mm) | Mass | Notes |
|---|---|---|---|
| `base_link` | 120 × 100 × 60 | 1 g | Kinematic root frame only — no visual, negligible mass |
| `head_link` | 65 × 75.28 × 42 | 250 g | Torso body (RPi 4B + PSU); sits between legs, protrudes ~20 mm forward of hip motors |
| `*_hip_roll_link` | 24.72 × 36.3 × 45.22 | 48 g | LX-16A; long axis along Z; shaft +12.5 mm above geometric centre |
| `*_hip_pitch_link` | 36.3 × 24.72 × 45.22 | 48 g | LX-16A; long axis along Z; shaft +12.5 mm above geometric centre |
| `*_thigh_link` | 37 × 25 × 35 | 10 g | 3D-printed thigh connector |
| `*_knee_link` | 36.3 × 24.72 × 45.22 | 48 g | LX-16A; long axis along Z; shaft +12.5 mm above geometric centre |
| `*_shank_link` | 37 × 25 × 35 | 10 g | 3D-printed shank connector |
| `*_ankle_link` | 36.3 × 24.72 × 45.22 | 48 g | LX-16A; long axis along Z; shaft +12.5 mm above geometric centre |
| `*_foot_link` | 80 × 45 × 10 | 10 g | 3D-printed foot; CoM centred on ankle axis (±40 mm fore/aft) |

### Joints

| Joint | Type | Axis | Range | Effort | Velocity |
|---|---|---|---|---|---|
| `*_hip_roll` | revolute | X | ±30° (±0.524 rad) | 1.5 N·m | 6.1 rad/s |
| `*_hip_pitch` | revolute | Y | ±45° (±0.785 rad) | 1.5 N·m | 6.1 rad/s |
| `*_knee` | revolute | Y | −90° ~ 0° | 1.5 N·m | 6.1 rad/s |
| `*_ankle` | revolute | Y | ±30° (±0.524 rad) | 1.5 N·m | 6.1 rad/s |
| `*_thigh_joint`, `*_shank_joint`, `*_ankle_to_foot` | fixed | — | — | — | — |

### Hip Assembly (L-shape)

The two hip motors form an **L-shape** when viewed from above (XY plane):

```
+X (forward)
     ↑
     │  ┌──────────────┐
     │  │  hip_pitch   │  ← revolute, Y-axis; 36.3(X) × 24.72(Y) mm in top view
     │  └──────────────┘
     │       ┌──────────┐
     └────────┤ hip_roll │  ← revolute, X-axis; 24.72(X) × 36.3(Y) mm in top view
              └──────────┘
              ↑ L opens inward; both motors 45.22 mm tall (Z)
```

- **All 8 motors** have their **long axis along Z** (45.22 mm vertical); shaft is **+12.5 mm above the geometric centre**, with 10.11 mm of motor body above the shaft
- **hip_pitch** is the front motor: 36.3 mm wide (X) × 24.72 mm deep (Y) in the XY plane
- **hip_roll** is the rear motor: 24.72 mm wide (X) × 36.3 mm deep (Y) in the XY plane
- The L opens **inward**, so hip_roll extends toward the robot center

---

## Repository Structure

```
KuroKun_Biped_Robot/
├── 3DPrintDocuments/        # 3D print files for all structural parts
├── FusionDocuments/         # Fusion 360 CAD source files
├── model/
│   ├── kurokun.urdf         # Simplified box-model URDF (ROS 2 / kinematics)
│   ├── kurokun.usd          # USD for Isaac Sim (generated — not committed)
│   ├── view_robot.launch.py # ROS 2 launch file (RSP + joint_state_publisher_gui + RViz2)
│   └── kurokun.rviz         # Pre-configured RViz2 layout (Fixed Frame = base_link)
├── IsaacLab/                # Isaac Lab submodule (not committed — see .gitignore)
├── README.md                # This file (English)
└── README_CN.md             # 中文文档
```

---

## License

This project is open source. See LICENSE for details.
