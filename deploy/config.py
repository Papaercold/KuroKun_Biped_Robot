"""
Hardware configuration for KuroKun sim2real deployment.
Fill in DIRECTION after running test_one_leg.py.
"""

# Serial port for LX-16A bus
SERIAL_PORT = "/dev/ttyAMA0"   # or "/dev/ttyUSB0"
BAUD_RATE = 115200

# Control frequency (must match simulation: 50 Hz)
CONTROL_HZ = 50
DT = 1.0 / CONTROL_HZ  # 0.02 s

# ── Joint mapping ─────────────────────────────────────────────────────────────
# Maps policy output index → servo ID
# Policy order: L_hip_roll, L_hip_pitch, L_knee, L_ankle,
#               R_hip_roll, R_hip_pitch, R_knee, R_ankle
SERVO_IDS = [1, 2, 3, 4, 5, 6, 7, 8]

# Simulation default joint positions (rad) — must match kurokun.py in IsaacLab
DEFAULT_POS = [
    0.0,   # left_hip_roll
    0.3,   # left_hip_pitch
   -0.6,   # left_knee
    0.3,   # left_ankle
    0.0,   # right_hip_roll
    0.3,   # right_hip_pitch
   -0.6,   # right_knee
    0.3,   # right_ankle
]

# Physical direction vs simulation convention.
# +1 = same direction, -1 = reversed.
# Fill these in after running test_one_leg.py direction test.
DIRECTION = [
    +1,   # left_hip_roll
    +1,   # left_hip_pitch
    +1,   # left_knee
    +1,   # left_ankle
    +1,   # right_hip_roll
    +1,   # right_hip_pitch
    +1,   # right_knee
    +1,   # right_ankle
]

# Policy action scale (must match training config)
ACTION_SCALE = 0.25

# Velocity command sent to policy [vx, vy, wz, heading] (m/s, m/s, rad/s, rad)
COMMAND = [0.4, 0.0, 0.0, 0.0]   # forward 0.4 m/s
