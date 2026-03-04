# KuroKun Deploy

Sim2real deployment code for KuroKun biped robot.

## Files

| File | Purpose |
|---|---|
| `lx16a.py` | LX-16A serial driver |
| `config.py` | Hardware config (IDs, directions, gains) |
| `test_one_leg.py` | Single-leg calibration and direction test |

## Step-by-step

### 1. Install dependencies (on Raspberry Pi)
```bash
pip install pyserial
```

### 2. Enable UART on RPi (disable Bluetooth to free ttyAMA0)
```bash
# Add to /boot/config.txt:
#   dtoverlay=disable-bt
# Then reboot.
sudo raspi-config  # → Interface Options → Serial Port → disable login shell, enable hardware serial
sudo reboot
```

### 3. Run single-leg test
```bash
cd ~/KuroKun_Biped_Robot/deploy
python test_one_leg.py
```
Use the interactive menu:
1. Scan → confirm servo IDs
2. Default pose → confirm robot moves to standing position
3. Direction test → fill `DIRECTION` in `config.py`

### 4. Copy policy to RPi
```bash
# From dev machine:
scp logs/rsl_rl/kurokun_flat/flat_corrected_shaft/exported/policy.pt pi@<IP>:~/KuroKun_Biped_Robot/deploy/
```
