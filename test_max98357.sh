#!/bin/bash

CARD=1

echo "=== Stop PulseAudio user service (supaya hw:1,0 tidak busy) ==="
systemctl --user stop pulseaudio.service pulseaudio.socket 2>/dev/null || true

echo "=== Set routing ADMAIF1 -> I2S2 ==="
amixer -c $CARD cset name='I2S2 Mux' 'ADMAIF1'

echo "=== Set format I2S2 ==="
amixer -c $CARD cset name='I2S2 Playback Audio Bit Format' 1       # 16-bit
amixer -c $CARD cset name='I2S2 codec frame mode' 1                # i2s mode
amixer -c $CARD cset name='I2S2 Sample Rate' 44100                 # 44.1 kHz
amixer -c $CARD cset name='I2S2 Playback Audio Channels' 2         # stereo

echo
echo "=== Cek ringkas I2S2 ==="
amixer -c $CARD cget name='I2S2 Mux' | tail -n 1
amixer -c $CARD cget name='I2S2 Playback Audio Bit Format' | tail -n 1
amixer -c $CARD cget name='I2S2 codec frame mode' | tail -n 1
amixer -c $CARD cget name='I2S2 Sample Rate' | tail -n 1

echo
echo "=== Jalankan speaker-test 440 Hz ke hw:1,0 ==="
echo "Tekan Ctrl+C kalau sudah bosan dengar bunyinya :)"
speaker-test -D hw:1,0 -c 2 -t sine -f 440

