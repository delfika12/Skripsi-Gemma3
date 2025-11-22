#!/bin/bash

# ====== CONFIG ======
WAV_FILE="suara.wav"   # ganti dengan file WAV kamu

# ====== CHECK FILE ======
if [ ! -f "$WAV_FILE" ]; then
    echo "[ERROR] File WAV tidak ditemukan: $WAV_FILE"
    exit 1
fi

echo "====================================================="
echo "   BRUTE-FORCE I2S / APE DEVICES (card 1, device 0-19)"
echo "====================================================="

for d in {0..19}; do
    echo
    echo "=============== TESTING DEVICE hw:1,$d ==============="
    aplay -D hw:1,$d -c 1 -f S16_LE -r 44100 "$WAV_FILE"
    echo "====================================================="
    sleep 1
done

echo
echo "[DONE] Jika salah satu device berbunyi, catat nomor device-nya."
