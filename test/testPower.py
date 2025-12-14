import os
import sys
import csv
import time
import json

# Tambahkan parent directory ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generateText import generate_text_from_image
from generateTTS import load_voice, tts_from_text
from test_utils import get_image_files, extract_image_id, ResourceMonitor

# === KONFIGURASI ===
TEST_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(TEST_DIR, "images-test")
RESULT_POWER_CSV = os.path.join(TEST_DIR, "resultPower.csv")
RESULT_POWER_TIMELINE_CSV = os.path.join(TEST_DIR, "resultPowerTimeline.csv")

def calculate_energy(stats_list):
    """
    Calculate energy in mWh from stats list containing 'power' (mW) and 'timestamp' (s).
    Energy = Integral(Power * dt)
    """
    if len(stats_list) < 2:
        return 0.0
    
    total_energy_mws = 0.0 # milliWatt-seconds (mJ)
    
    for i in range(len(stats_list) - 1):
        t1 = stats_list[i]['timestamp']
        p1 = stats_list[i]['power']
        t2 = stats_list[i+1]['timestamp']
        p2 = stats_list[i+1]['power']
        
        dt = t2 - t1
        avg_p = (p1 + p2) / 2
        total_energy_mws += avg_p * dt
        
    # Convert mWs to mWh
    total_energy_mwh = total_energy_mws / 3600.0
    return total_energy_mwh

def main():
    print("=" * 60)
    print("TEST POWER - Monitoring Power & Energy")
    print("=" * 60)
    
    image_files = get_image_files(IMAGES_DIR)
    if not image_files:
        print(f"[ERROR] Tidak ada gambar di folder: {IMAGES_DIR}")
        return
    
    print("[INFO] Memuat model Piper...")
    voice = load_voice()
    print()
    
    results_power = []
    # Initialize timeline CSV
    with open(RESULT_POWER_TIMELINE_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['timestamp', 'relative_time', 'image_id', 'image_name', 'power_mw', 'cpu_util_pct', 'gpu_util_pct', 'ram_usage_mb']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    dummy_audio_path = os.path.join(TEST_DIR, "temp_power_test.wav")
    
    for idx, image_path in enumerate(image_files, 1):
        print(f"Processing {idx}/{len(image_files)}: {os.path.basename(image_path)}")
        
        image_id = extract_image_id(image_path)
        image_name = os.path.basename(image_path)
        
        # Start Monitor
        monitor = ResourceMonitor(interval=0.1)
        monitor.start()
        
        # Run Pipeline
        try:
            text, _ = generate_text_from_image(image_path, save_to_file=False)
            if text:
                import wave
                with wave.open(dummy_audio_path, "wb") as wav_file:
                    voice.synthesize_wav(text, wav_file)
        except Exception as e:
            print(f"  [Error] Processing failed: {e}")
        
        # Stop Monitor
        monitor.stop()
        
        # Process Stats
        avgs = monitor.get_averages()
        stats_list = monitor.get_stats()
        energy_mwh = calculate_energy(stats_list)
        
        print(f"  Avg Power: {avgs['power']:.2f} mW | Energy: {energy_mwh:.4f} mWh")
        
        # Save Summary
        results_power.append({
            'image_id': image_id,
            'image_name': image_name,
            'avg_power_mw': round(avgs['power'], 2),
            'energy_mwh': round(energy_mwh, 4),
            'avg_cpu_util_pct': round(avgs['cpu_util'], 2),
            'avg_gpu_util_pct': round(avgs['gpu_util'], 2),
            'avg_ram_usage_mb': round(avgs['ram_usage'], 2)
        })
        
        # Save Timeline
        try:
            with open(RESULT_POWER_TIMELINE_CSV, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'relative_time', 'image_id', 'image_name', 'power_mw', 'cpu_util_pct', 'gpu_util_pct', 'ram_usage_mb']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                for s in stats_list:
                    writer.writerow({
                        'timestamp': s['timestamp'],
                        'relative_time': s['relative_time'],
                        'image_id': image_id,
                        'image_name': image_name,
                        'power_mw': s['power'],
                        'cpu_util_pct': s['cpu_util'],
                        'gpu_util_pct': s['gpu_util'],
                        'ram_usage_mb': s['ram_usage']
                    })
        except Exception as e:
            print(f"[ERROR] Saving Timeline: {e}")
            
        # Save Summary CSV Incrementally
        try:
            with open(RESULT_POWER_CSV, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['image_id', 'image_name', 'avg_power_mw', 'energy_mwh', 'avg_cpu_util_pct', 'avg_gpu_util_pct', 'avg_ram_usage_mb']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_power)
        except Exception as e:
            print(f"[ERROR] Saving Summary CSV: {e}")

    if os.path.exists(dummy_audio_path):
        os.remove(dummy_audio_path)

    print(f"\n{'=' * 60}")
    print("POWER TEST COMPLETED")
    print(f"Summary saved to: {RESULT_POWER_CSV}")
    print(f"Timeline saved to: {RESULT_POWER_TIMELINE_CSV}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
