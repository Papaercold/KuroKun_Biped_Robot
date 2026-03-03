# KuroKun Biped Robot — Official Design Documentation

**Language:** English | [中文](README_CN.md)

KuroKun is an open-source bipedal robot platform. This repository serves as the **official design documentation** for KuroKun, covering mechanical design, simulation, and real-world deployment.

> **Course Project** — This project was developed as part of the **Duke University Robot Studio** course, Spring 2026. You are welcome to use this project as a reference and source of inspiration. However, please build upon it with your **own original improvements** — do not copy or submit this work as your own.

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

## Locomotion Training (Isaac Lab)

Bipedal locomotion is trained with **PPO** (Proximal Policy Optimization) using [Isaac Lab](https://github.com/isaac-sim/IsaacLab). The policy learns velocity-tracking locomotion on flat terrain.

### Prerequisites

1. **Generate the USD** from the URDF (run once, or whenever the URDF changes):

```bash
cd /path/to/KuroKun_Biped_Robot/IsaacLab

CONDA_PREFIX=$(python -c "import sys; print(sys.prefix)") \
./isaaclab.sh -p scripts/tools/convert_urdf.py \
  --input ../model/kurokun.urdf \
  --output ../model/kurokun.usd \
  --merge-joints
```

> `--merge-joints` merges fixed joints (thigh, shank, foot) into their parent rigid bodies, which is required for Isaac Lab's articulation system.

### Training

Run training from the **repository root** (not from inside `IsaacLab/`) so that logs are saved under `KuroKun_Biped_Robot/logs/`:

```bash
cd /path/to/KuroKun_Biped_Robot

./IsaacLab/isaaclab.sh -p IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-KuroKun-v0 \
  --num_envs 1024 \
  --headless \
  --video \
  --video_length 300 \
  --video_interval 5000
```

| Argument | Description | Default |
|---|---|---|
| `--task` | Environment ID | `Isaac-Velocity-Flat-KuroKun-v0` |
| `--num_envs` | Number of parallel simulation environments | 1024 |
| `--headless` | Run without GUI (faster) | off |
| `--video` | Record video clips during training | off |
| `--video_length` | Length of each video clip (steps) | 200 |
| `--video_interval` | Steps between video recordings | 2000 |

### Monitoring with TensorBoard

In a separate terminal (can be started at any time during training):

```bash
cd /path/to/KuroKun_Biped_Robot
tensorboard --logdir logs/rsl_rl/kurokun_flat
```

Open `http://localhost:6006` in a browser. Key metrics to watch:

| Metric | Meaning | Target |
|---|---|---|
| `Train/mean_episode_length` | Steps survived per episode | Approaches max (~1000) |
| `Train/mean_reward` | Average total reward | Increasing |
| `Episode/rew_track_lin_vel_xy_exp` | Velocity-tracking reward | Positive and stable |
| `Episode/rew_termination_penalty` | Fall penalty | Near 0 (robot stops falling) |

Training is considered successful when `mean_episode_length` saturates near the maximum (20 s ÷ simulation dt) and the termination penalty approaches 0.

### Evaluating a Trained Policy

```bash
cd /path/to/KuroKun_Biped_Robot

./IsaacLab/isaaclab.sh -p IsaacLab/scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-KuroKun-Play-v0 \
  --num_envs 50 \
  --load_run <timestamp> \
  --video \
  --video_length 500
```

Replace `<timestamp>` with the run directory name under `logs/rsl_rl/kurokun_flat/` (e.g. `2026-03-03_13-05-37`).

### Output Structure

```
KuroKun_Biped_Robot/
└── logs/rsl_rl/kurokun_flat/<timestamp>/
    ├── params/
    │   ├── env.yaml            # Environment config snapshot
    │   └── agent.yaml          # PPO config snapshot
    ├── videos/
    │   ├── train/              # Clips recorded during training
    │   └── play/               # Clips recorded during evaluation
    ├── model_*.pt              # Checkpoints saved every 50 iterations
    └── events.out.tfevents.*   # TensorBoard logs
```

### Configuration Files

| File | Description |
|---|---|
| `IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/kurokun.py` | Robot asset config (USD path, actuators, initial pose) |
| `IsaacLab/source/isaaclab_tasks/.../config/kurokun/flat_env_cfg.py` | Flat-terrain environment config |
| `IsaacLab/source/isaaclab_tasks/.../config/kurokun/rough_env_cfg.py` | Rough-terrain environment config and reward weights |
| `IsaacLab/source/isaaclab_tasks/.../config/kurokun/agents/rsl_rl_ppo_cfg.py` | PPO hyperparameters |

Key design choices:

| Parameter | Value | Reason |
|---|---|---|
| `enabled_self_collisions` | `False` | Adjacent motor boxes would cause jitter; standard practice for locomotion training |
| `action_scale` | 0.25 | Small robot — reduced action scale prevents over-actuation |
| `effort_limit_sim` | 1.5 N·m | Matches LX-16A stall torque |
| `max_iterations` (flat) | 1000 | Sufficient for flat-terrain convergence |
| `actor_hidden_dims` | [128, 128, 128] | Compact network suitable for 8-DOF robot |
| Contact body for foot air-time | `.*_ankle_link` | `foot_link` is merged into `ankle_link` by `--merge-joints` |

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
