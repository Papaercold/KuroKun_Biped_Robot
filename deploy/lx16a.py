"""
LX-16A servo driver (half-duplex UART).
Handles low-level serial protocol for Hiwonder LX-16A servos.
"""

import serial
import time


# LX-16A position range: 0~1000 = 0~240 degrees
RAD_TO_UNIT = 1000.0 / (240.0 * 3.14159265358979 / 180.0)  # ≈ 238.87 units/rad


def _checksum(data: bytes) -> int:
    return (~sum(data)) & 0xFF


def _packet(servo_id: int, cmd: int, params: bytes = b"") -> bytes:
    length = 3 + len(params)
    body = bytes([servo_id, length, cmd]) + params
    return bytes([0x55, 0x55]) + body + bytes([_checksum(body)])


class LX16ABus:
    """
    Manages a single half-duplex UART bus with one or more LX-16A servos.

    Usage:
        bus = LX16ABus('/dev/ttyAMA0')
        bus.move(1, 500, time_ms=1000)   # servo ID=1, position=500, 1 second
        pos = bus.read_pos(1)
    """

    CMD_MOVE_TIME_WRITE = 0x01
    CMD_POS_READ = 0x1C
    CMD_SERVO_MODE_WRITE = 0x1D
    CMD_LOAD_OR_UNLOAD_WRITE = 0x1F

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.05):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(0.1)

    def close(self):
        self.ser.close()

    def _send(self, packet: bytes):
        self.ser.reset_input_buffer()
        self.ser.write(packet)

    def move(self, servo_id: int, position: int, time_ms: int = 500):
        """Move servo to position (0~1000) over time_ms milliseconds."""
        position = max(0, min(1000, int(position)))
        time_ms = max(0, min(30000, int(time_ms)))
        params = bytes([
            position & 0xFF, (position >> 8) & 0xFF,
            time_ms & 0xFF, (time_ms >> 8) & 0xFF,
        ])
        self._send(_packet(servo_id, self.CMD_MOVE_TIME_WRITE, params))

    def read_pos(self, servo_id: int) -> int | None:
        """Read current position (0~1000). Returns None on timeout."""
        self._send(_packet(servo_id, self.CMD_POS_READ))
        time.sleep(0.008)
        data = self.ser.read(8)
        if len(data) >= 8 and data[0] == 0x55 and data[1] == 0x55:
            return data[5] | (data[6] << 8)
        return None

    def torque_off(self, servo_id: int):
        """Disable torque (servo goes limp)."""
        self._send(_packet(servo_id, self.CMD_LOAD_OR_UNLOAD_WRITE, bytes([0])))

    def torque_on(self, servo_id: int):
        """Enable torque."""
        self._send(_packet(servo_id, self.CMD_LOAD_OR_UNLOAD_WRITE, bytes([1])))

    # ── Convenience: rad ↔ unit conversion ──────────────────────────────────

    def move_rad(self, servo_id: int, rad: float, time_ms: int = 500, direction: int = 1):
        """
        Move to angle in radians (0 rad = position 500).
        direction: +1 or -1 to flip the axis if physical direction is reversed.
        """
        unit = int(500 + direction * rad * RAD_TO_UNIT)
        self.move(servo_id, unit, time_ms)

    def read_rad(self, servo_id: int, direction: int = 1) -> float | None:
        """Read position in radians."""
        unit = self.read_pos(servo_id)
        if unit is None:
            return None
        return direction * (unit - 500) / RAD_TO_UNIT
