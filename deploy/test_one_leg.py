"""
Single-leg calibration and direction test.
Run this on the Raspberry Pi with one leg connected.

Steps:
  1. Scan to confirm servo IDs
  2. Move each joint to simulation default pose
  3. Test +0.2 rad on each joint to confirm direction convention
  4. Print a direction table to paste into config.py
"""

import time
import sys
from lx16a import LX16ABus

# ── Configuration ────────────────────────────────────────────────────────────

SERIAL_PORT = "/dev/ttyAMA0"   # change to /dev/ttyUSB0 if using USB adapter

# Servo ID → (joint name, default_rad from simulation)
# Edit IDs to match how you assigned them to your servos.
LEG_JOINTS = {
    1: ("left_hip_roll",   0.0),
    2: ("left_hip_pitch",  0.3),
    3: ("left_knee",      -0.6),
    4: ("left_ankle",      0.3),
}

# Assumed all +1 until you verify below
DIRECTION = {
    1: +1,
    2: +1,
    3: +1,
    4: +1,
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def scan(bus: LX16ABus, id_range=range(1, 20)):
    print("\n=== Scanning for servos ===")
    found = []
    for sid in id_range:
        pos = bus.read_pos(sid)
        if pos is not None:
            print(f"  Found ID={sid}  pos={pos}")
            found.append(sid)
    if not found:
        print("  No servos found. Check wiring and port.")
    return found


def go_default(bus: LX16ABus, time_ms: int = 2000):
    print(f"\n=== Moving to default pose (over {time_ms}ms) ===")
    for sid, (name, default_rad) in LEG_JOINTS.items():
        bus.move_rad(sid, default_rad, time_ms=time_ms, direction=DIRECTION[sid])
        print(f"  {name} (ID={sid}): {default_rad:.2f} rad")
    time.sleep(time_ms / 1000.0 + 0.3)


def read_all(bus: LX16ABus):
    print("\n=== Current positions ===")
    for sid, (name, default_rad) in LEG_JOINTS.items():
        raw = bus.read_pos(sid)
        rad = bus.read_rad(sid, DIRECTION[sid])
        err = (rad - default_rad) if rad is not None else None
        print(f"  {name} (ID={sid}): raw={raw}  {rad:.3f} rad  err={err:+.3f}" if rad is not None
              else f"  {name} (ID={sid}): NO RESPONSE")


def direction_test(bus: LX16ABus, delta_rad: float = 0.2):
    print(f"\n=== Direction test: each joint +{delta_rad:.1f} rad ===")
    print("Watch the robot. Answer 'y' if the sim-positive direction matches reality.")
    print("(sim convention: X=fwd, Y=left, Z=up)")
    print()

    results = {}
    for sid, (name, default_rad) in LEG_JOINTS.items():
        input(f"  [{name}] Press Enter to move +{delta_rad} rad from default...")
        bus.move_rad(sid, default_rad + delta_rad, time_ms=800, direction=DIRECTION[sid])
        time.sleep(1.0)
        ans = input("    Direction correct? (y/n): ").strip().lower()
        bus.move_rad(sid, default_rad, time_ms=800, direction=DIRECTION[sid])
        time.sleep(1.0)
        results[sid] = (ans == "y")

    print("\n=== Results ===")
    print("# Paste into config.py:")
    print("DIRECTION = {")
    for sid, (name, _) in LEG_JOINTS.items():
        d = DIRECTION[sid] if results[sid] else -DIRECTION[sid]
        print(f"    {sid}: {d:+d},  # {name}")
    print("}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    bus = LX16ABus(SERIAL_PORT)

    while True:
        print("\n--- KuroKun single-leg test ---")
        print("  1. Scan servos")
        print("  2. Go to default pose")
        print("  3. Read positions")
        print("  4. Direction test (+0.2 rad each)")
        print("  5. Torque OFF all")
        print("  q. Quit")
        cmd = input("Choice: ").strip().lower()

        if cmd == "1":
            scan(bus)
        elif cmd == "2":
            go_default(bus)
        elif cmd == "3":
            read_all(bus)
        elif cmd == "4":
            go_default(bus, time_ms=2000)
            direction_test(bus)
        elif cmd == "5":
            for sid in LEG_JOINTS:
                bus.torque_off(sid)
            print("  Torque disabled.")
        elif cmd == "q":
            for sid in LEG_JOINTS:
                bus.torque_off(sid)
            bus.close()
            sys.exit(0)
        else:
            print("  Unknown command.")


if __name__ == "__main__":
    main()
