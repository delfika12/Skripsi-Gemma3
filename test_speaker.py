import subprocess
import time
import os
import sys
import shutil

# ===== CONFIG =====
WAV_FILE = "suara.wav"   # ganti nama file wav kamu

# ===== CHECK FILE =====
if not os.path.exists(WAV_FILE):
    print(f"[ERROR] File WAV tidak ditemukan: {WAV_FILE}")
    sys.exit(1)

# ===== CHECK aplay =====
if shutil.which("aplay") is None:
    print("[ERROR] 'aplay' tidak ditemukan. Install dulu: sudo apt install alsa-utils")
    sys.exit(1)

print("=====================================================")
print("   BRUTE-FORCE I2S / APE DEVICES (card 1, device 0-19)")
print("=====================================================")

for device in range(0, 20):
    print(f"\n===== TESTING DEVICE hw:1,{device} =====")
    cmd = [
        "aplay",
        "-D", f"hw:1,{device}",
        "-c", "1",
        "-f", "S16_LE",
        "-r", "44100",
        WAV_FILE
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"[INFO] Suara *mungkin* keluar pada hw:1,{device}.")
    except subprocess.CalledProcessError:
        print(f"[INFO] Device hw:1,{device} gagal.")
    
    print("=====================================================")
    time.sleep(1)

print("\n[DONE] Jika ada suara keluar, catat device-nya (misalnya hw:1,3).")
