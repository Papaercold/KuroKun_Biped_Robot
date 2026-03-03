# KuroKun 双足机器人 — 官方设计文档

**语言：** [English](README.md) | 中文

KuroKun 是一个开源双足机器人平台。本仓库是 KuroKun 的**官方设计文档**，涵盖机械设计、仿真与实机部署的完整内容。

> **课程项目声明** — 本项目为**杜克大学（Duke University）Robot Studio** 课程 2026 年春季学期的课程项目。欢迎您将本项目作为参考与灵感来源，但请在此基础上做出**属于您自己的原创改进**，请勿直接抄袭或将本项目作为您自己的作品提交。

---

## 项目简介

![KuroKun 设计草图](Design%20sketch.jpg)

KuroKun 是一款全 3D 打印双足机器人，采用 **LX-16A 串行总线舵机**作为执行器，以**树莓派**作为主控制器。项目完整实现了从仿真到硬件的全流程，包括在 **NVIDIA Isaac Sim** 中完成的双足行走训练，以及将策略迁移至实体机器人的 **sim-to-real** 转移。

---

## 硬件配置

| 组件 | 详情 |
|---|---|
| 执行器 | LX-16A 串行总线舵机 |
| 主控 | 树莓派 4B（Raspberry Pi 4B） |
| 电源 | 6V 12W |
| 结构 | 全 3D 打印固件 |

### 电机构成

KuroKun 每条腿使用 **4 个电机**，共 8 个。规定机器人面向方向为 **+X 轴方向**，电机布局如下：

| 关节 | 数量 | 旋转轴 | 功能描述 |
|---|---|---|---|
| 髋关节（横滚） | 1 | X 轴 | 控制腿部外展 / 内收 |
| 髋关节（俯仰） | 1 | Y 轴 | 控制腿部前摆 / 后摆 |
| 膝关节 | 1 | Y 轴 | 控制膝部屈曲 / 伸展 |
| 踝关节 | 1 | Y 轴 | 控制踝部屈曲 / 伸展 |

---

## 3D 打印配置

所有结构件均使用以下切片参数打印（使用 PrusaSlicer，已在 **Original Prusa CORE One** 上验证）。

| 参数 | 数值 |
|---|---|
| 打印机 | Original Prusa CORE One |
| 切片预设 | Prusa Core one |
| 喷嘴直径 | 0.4 mm |
| 打印配置 | 0.20mm SPEED |
| 耗材 | Generic PLA |
| 层厚 | 0.2 mm |
| 周长壁数 | 3 |
| 填充密度 | 15% |
| 填充图案 | Grid（网格） |
| 裙边类型 | 无裙边（No brim） |
| 支撑类型 | Organic（仅生成在热床上） |

**温度设置：**

| | 热床温度（°C） | 喷嘴温度（°C） |
|---|---|---|
| 首层 | 60 | 230 |
| 其余层 | 60 | 220 |

---

## 仿真与 Sim-to-Real

双足行走策略在 **NVIDIA Isaac Sim** 中完成训练，随后迁移至实体 KuroKun 机器人。Sim-to-Real 流程弥合了仿真环境与现实动力学之间的差异，实现了策略的实机部署。

---

## 机器人模型

`model/` 目录下包含两种格式的机器人描述文件：

| 文件 | 格式 | 用途 |
|---|---|---|
| `model/kurokun.urdf` | URDF | ROS 2（可视化、运动学） |
| `model/kurokun.usd` | USD | NVIDIA Isaac Sim（物理仿真 / 训练） |

`kurokun.urdf` 是用于刚体动力学仿真的**简化 Box 模型**。所有结构件均以均质长方体近似，放弃视觉精度，换取正确的质量、质心与惯性张量——这三者才是动力学仿真中唯一起作用的物理量。

### 快速查看（ROS 2 Jazzy）

**安装依赖**（已安装可跳过）：

```bash
sudo apt install ros-jazzy-robot-state-publisher \
                 ros-jazzy-joint-state-publisher-gui \
                 ros-jazzy-rviz2
```

**启动：**

```bash
ros2 launch model/view_robot.launch.py
```

该命令同时打开以下窗口：
- **RViz2** — 3D 可视化界面，固定坐标系为 `base_link`
- **joint_state_publisher_gui** — 滑动条，可交互式拖动每个关节

### 坐标系约定

| 轴 | 方向 |
|---|---|
| X | 机器人正前方 |
| Y | 机器人左侧 |
| Z | 竖直向上 |

### 运动学链

```
base_link  （1 g，运动学根节点——无视觉模型）
├── head_link  [固定]  →  head_link  （65×75.28×42 mm，250 g，机身主体）
├── left_hip_roll   [转动，X 轴]  →  left_hip_roll_link   (48 g)
│     └── left_hip_pitch  [转动，Y 轴]  →  left_hip_pitch_link  (48 g)
│           └── [固定]  →  left_thigh_link  (10 g)
│                 └── left_knee  [转动，Y 轴]  →  left_knee_link  (48 g)
│                       └── [固定]  →  left_shank_link  (10 g)
│                             └── left_ankle  [转动，Y 轴]  →  left_ankle_link  (48 g)
│                                   └── [固定]  →  left_foot_link  (10 g)
└── right_hip_roll  [转动，X 轴]  →  （右腿与左腿镜像对称）
```

### 链接（Links）

| 链接名 | 箱体尺寸（mm） | 质量 | 说明 |
|---|---|---|---|
| `base_link` | 120 × 100 × 60 | 1 g | 运动学根节点（无视觉模型，质量可忽略） |
| `head_link` | 65 × 75.28 × 42 | 250 g | 机身主体（树莓派 4B + 电源），位于两腿之间，向前突出约 20 mm |
| `*_hip_roll_link` | 24.72 × 36.3 × 45.22 | 48 g | LX-16A 舵机；长轴沿 Z；出力轴在几何中心上方 +12.5 mm |
| `*_hip_pitch_link` | 36.3 × 24.72 × 45.22 | 48 g | LX-16A 舵机；长轴沿 Z；出力轴在几何中心上方 +12.5 mm |
| `*_thigh_link` | 37 × 25 × 35 | 10 g | 3D 打印大腿连接件 |
| `*_knee_link` | 36.3 × 24.72 × 45.22 | 48 g | LX-16A 舵机；长轴沿 Z；出力轴在几何中心上方 +12.5 mm |
| `*_shank_link` | 37 × 25 × 35 | 10 g | 3D 打印小腿连接件 |
| `*_ankle_link` | 36.3 × 24.72 × 45.22 | 48 g | LX-16A 舵机；长轴沿 Z；出力轴在几何中心上方 +12.5 mm |
| `*_foot_link` | 80 × 45 × 10 | 10 g | 3D 打印脚板；质心居中（踝关节轴前后各 40 mm） |

### 关节（Joints）

| 关节 | 类型 | 旋转轴 | 范围 | 力矩 | 速度 |
|---|---|---|---|---|---|
| `*_hip_roll` | 转动 | X | ±30°（±0.524 rad） | 1.5 N·m | 6.1 rad/s |
| `*_hip_pitch` | 转动 | Y | ±45°（±0.785 rad） | 1.5 N·m | 6.1 rad/s |
| `*_knee` | 转动 | Y | −90° ~ 0° | 1.5 N·m | 6.1 rad/s |
| `*_ankle` | 转动 | Y | ±30°（±0.524 rad） | 1.5 N·m | 6.1 rad/s |
| `*_thigh_joint`、`*_shank_joint`、`*_ankle_to_foot` | 固定 | — | — | — | — |

### 髋关节 L 形布局

从上方（XY 平面）俯视，两个髋部电机构成 **L 形**：

```
+X（正前方）
     ↑
     │  ┌──────────────┐
     │  │  hip_pitch   │  ← 转动关节，Y 轴；俯视 36.3(X)×24.72(Y) mm
     │  └──────────────┘
     │       ┌──────────┐
     └────────┤ hip_roll │  ← 转动关节，X 轴；俯视 24.72(X)×36.3(Y) mm
              └──────────┘
              ↑ L 形开口朝内；两电机高度均为 45.22 mm（Z 方向）
```

- **全部 8 个电机**长轴均沿 **Z 轴**（竖向 45.22 mm）；出力轴位于几何中心**上方 +12.5 mm**，电机顶部超出出力轴 10.11 mm
- **hip_pitch**（前侧）：俯视截面 36.3 mm（X）× 24.72 mm（Y）
- **hip_roll**（后侧）：俯视截面 24.72 mm（X）× 36.3 mm（Y）
- L 形开口**朝内**，hip_roll 朝机器人中心延伸

---

## 运动控制训练（Isaac Lab）

双足行走策略使用 **PPO**（近端策略优化）在 [Isaac Lab](https://github.com/isaac-sim/IsaacLab) 中训练，目标为在平坦地形上完成速度跟踪行走。

### 前置步骤

1. **从 URDF 生成 USD**（首次运行或 URDF 有改动时执行）：

```bash
cd /path/to/KuroKun_Biped_Robot/IsaacLab

CONDA_PREFIX=$(python -c "import sys; print(sys.prefix)") \
./isaaclab.sh -p scripts/tools/convert_urdf.py \
  --input ../model/kurokun.urdf \
  --output ../model/kurokun.usd \
  --merge-joints
```

> `--merge-joints` 将固定关节（大腿、小腿、脚板）合并到其父刚体中，这是 Isaac Lab 关节系统的要求。

### 开始训练

**从仓库根目录运行**（而非 `IsaacLab/` 目录内），这样日志会保存在 `KuroKun_Biped_Robot/logs/` 下：

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

| 参数 | 说明 | 默认值 |
|---|---|---|
| `--task` | 环境 ID | `Isaac-Velocity-Flat-KuroKun-v0` |
| `--num_envs` | 并行仿真环境数 | 1024 |
| `--headless` | 无 GUI 模式（速度更快） | 关闭 |
| `--video` | 训练过程中录制视频片段 | 关闭 |
| `--video_length` | 每段视频长度（步数） | 200 |
| `--video_interval` | 每隔多少步录制一次 | 2000 |

### 使用 TensorBoard 监控训练

在另一个终端中运行（训练中任何时候都可以启动）：

```bash
cd /path/to/KuroKun_Biped_Robot
tensorboard --logdir logs/rsl_rl/kurokun_flat
```

浏览器打开 `http://localhost:6006`，关键指标如下：

| 指标 | 含义 | 目标 |
|---|---|---|
| `Train/mean_episode_length` | 每个 episode 存活步数 | 趋近最大值（约 1000） |
| `Train/mean_reward` | 平均总奖励 | 持续上升 |
| `Episode/rew_track_lin_vel_xy_exp` | 速度跟踪奖励 | 正值且稳定 |
| `Episode/rew_termination_penalty` | 摔倒惩罚 | 趋近 0（机器人不再摔倒） |

当 `mean_episode_length` 趋近最大值、摔倒惩罚趋近 0 时，视为训练成功。

### 评估已训练策略

```bash
cd /path/to/KuroKun_Biped_Robot

./IsaacLab/isaaclab.sh -p IsaacLab/scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-KuroKun-Play-v0 \
  --num_envs 50 \
  --load_run <时间戳> \
  --video \
  --video_length 500
```

将 `<时间戳>` 替换为 `logs/rsl_rl/kurokun_flat/` 下对应的运行目录名（例如 `2026-03-03_13-05-37`）。

### 输出目录结构

```
KuroKun_Biped_Robot/
└── logs/rsl_rl/kurokun_flat/<时间戳>/
    ├── params/
    │   ├── env.yaml            # 环境配置快照
    │   └── agent.yaml          # PPO 配置快照
    ├── videos/
    │   ├── train/              # 训练过程录制的视频片段
    │   └── play/               # 评估过程录制的视频片段
    ├── model_*.pt              # 每 50 次迭代保存一次的模型检查点
    └── events.out.tfevents.*   # TensorBoard 日志
```

### 配置文件说明

| 文件 | 说明 |
|---|---|
| `IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/kurokun.py` | 机器人资产配置（USD 路径、执行器、初始姿态） |
| `IsaacLab/source/isaaclab_tasks/.../config/kurokun/flat_env_cfg.py` | 平坦地形环境配置 |
| `IsaacLab/source/isaaclab_tasks/.../config/kurokun/rough_env_cfg.py` | 崎岖地形环境配置及奖励权重 |
| `IsaacLab/source/isaaclab_tasks/.../config/kurokun/agents/rsl_rl_ppo_cfg.py` | PPO 超参数 |

关键设计说明：

| 参数 | 取值 | 原因 |
|---|---|---|
| `enabled_self_collisions` | `False` | 相邻电机碰撞体会导致抖动；这是 locomotion 训练的标准做法 |
| `action_scale` | 0.25 | 小型机器人，缩小 action scale 防止过激励 |
| `effort_limit_sim` | 1.5 N·m | 与 LX-16A 堵转力矩一致 |
| `max_iterations`（平坦地形） | 1000 | 平坦地形训练收敛所需迭代次数 |
| `actor_hidden_dims` | [128, 128, 128] | 适合 8 自由度机器人的紧凑网络 |
| 脚部接触传感器 body | `.*_ankle_link` | `--merge-joints` 将 `foot_link` 合并入 `ankle_link` |

---

## 仓库结构

```
KuroKun_Biped_Robot/
├── 3DPrintDocuments/        # 所有结构件的 3D 打印文件
├── FusionDocuments/         # Fusion 360 CAD 源文件
├── model/
│   ├── kurokun.urdf         # 简化 Box 模型 URDF（ROS 2 / 运动学）
│   ├── kurokun.usd          # Isaac Sim 用 USD（自动生成，不提交到仓库）
│   ├── view_robot.launch.py # ROS 2 启动文件（RSP + joint_state_publisher_gui + RViz2）
│   └── kurokun.rviz         # 预配置 RViz2 布局（固定坐标系 = base_link）
├── IsaacLab/                # Isaac Lab 子仓库（不提交，见 .gitignore）
├── README.md                # 英文文档
└── README_CN.md             # 本文件（中文）
```

---

## 开源协议

本项目开源发布，详见 LICENSE 文件。
