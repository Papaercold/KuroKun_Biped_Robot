# KuroKun 双足机器人 — 官方设计文档

KuroKun 是一个开源双足机器人平台。本仓库是 KuroKun 的**官方设计文档**，涵盖机械设计、仿真与实机部署的完整内容。

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
| `*_hip_roll_link` | 24.72 × 45.22 × 36.3 | 48 g | LX-16A 舵机；长轴沿 Y（绕 Z 旋转 90°） |
| `*_hip_pitch_link` | 45.22 × 24.72 × 36.3 | 48 g | LX-16A 舵机；长轴沿 X |
| `*_thigh_link` | 37 × 25 × 35 | 10 g | 3D 打印大腿连接件 |
| `*_knee_link` | 45.22 × 24.72 × 36.3 | 48 g | LX-16A 舵机；长轴沿 X |
| `*_shank_link` | 37 × 25 × 35 | 10 g | 3D 打印小腿连接件 |
| `*_ankle_link` | 45.22 × 24.72 × 36.3 | 48 g | LX-16A 舵机；长轴沿 X |
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
     │   ┌────────────────┐
     │   │   hip_pitch    │   ← 转动关节，Y 轴；长轴沿 X
     │   └────────────────┘
     │             ┌──────────────────────┐
     └─────────────┤      hip_roll        │   ← 转动关节，X 轴；长轴沿 Y
                   └──────────────────────┘
                   ↑ 两电机外侧面对齐（L 形开口朝向机器人内侧）
```

- **hip_pitch**（前侧）：长轴（45.22 mm）沿 X 方向
- **hip_roll**（后侧）：绕 Z 轴旋转 90°，长轴（45.22 mm）沿 Y 方向
- 两电机沿 X 方向**紧贴无间隙**；外侧 Y 面**对齐平整**
- L 形开口**朝内**，hip_roll 朝机器人中心延伸

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
