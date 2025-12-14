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
RESULT_RESOURCE_CSV = os.path.join(TEST_DIR, "resultResource.csv")
RESULT_RESOURCE_TIMELINE_CSV = os.path.join(TEST_DIR, "resultResourceTimeline.csv")

def main():
    print("=" * 60)
    print("TEST RESOURCE - Monitoring CPU, RAM, GPU")
    print("=" * 60)
    
    image_files = get_image_files(IMAGES_DIR)
    if not image_files:
        print(f"[ERROR] Tidak ada gambar di folder: {IMAGES_DIR}")
        return
    
    print("[INFO] Memuat model Piper...")
    voice = load_voice()
    print()
    
    results_resource = []
    # Initialize timeline CSV
    with open(RESULT_RESOURCE_TIMELINE_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['timestamp', 'relative_time', 'image_id', 'image_name', 'cpu_clock_khz', 'cpu_util_pct', 'ram_usage_mb', 'gpu_util_pct', 'vram_gpu_mb']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    dummy_audio_path = os.path.join(TEST_DIR, "temp_resource_test.wav")
    
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
        
        # Save Summary
        results_resource.append({
            'image_id': image_id,
            'image_name': image_name,
            'cpu_clock_khz': round(avgs['cpu_clock'], 2),
            'cpu_util_pct': round(avgs['cpu_util'], 2),
            'ram_usage_mb': round(avgs['ram_usage'], 2),
            'gpu_util_pct': round(avgs['gpu_util'], 2),
            'vram_gpu_mb': round(avgs['vram_gpu'], 2)
        })
        
        # Save Timeline
        try:
            with open(RESULT_RESOURCE_TIMELINE_CSV, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'relative_time', 'image_id', 'image_name', 'cpu_clock_khz', 'cpu_util_pct', 'ram_usage_mb', 'gpu_util_pct', 'vram_gpu_mb']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                for s in stats_list:
                    writer.writerow({
                        'timestamp': s['timestamp'],
                        'relative_time': s['relative_time'],
                        'image_id': image_id,
                        'image_name': image_name,
                        'cpu_clock_khz': s['cpu_clock'],
                        'cpu_util_pct': s['cpu_util'],
                        'ram_usage_mb': s['ram_usage'],
                        'gpu_util_pct': s['gpu_util'],
                        'vram_gpu_mb': s['vram_gpu']
                    })
        except Exception as e:
            print(f"[ERROR] Saving Timeline: {e}")
            
        # Save Summary CSV Incrementally
        try:
            with open(RESULT_RESOURCE_CSV, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['image_id', 'image_name', 'cpu_clock_khz', 'cpu_util_pct', 'ram_usage_mb', 'gpu_util_pct', 'vram_gpu_mb']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_resource)
        except Exception as e:
            print(f"[ERROR] Saving Summary CSV: {e}")

    if os.path.exists(dummy_audio_path):
        os.remove(dummy_audio_path)

    print(f"\n{'=' * 60}")
    print("RESOURCE TEST COMPLETED")
    print(f"Summary saved to: {RESULT_RESOURCE_CSV}")
    print(f"Timeline saved to: {RESULT_RESOURCE_TIMELINE_CSV}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
