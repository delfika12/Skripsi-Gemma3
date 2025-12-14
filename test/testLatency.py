import os
import sys
import csv
import time
import json

# Tambahkan parent directory ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generateText import generate_text_from_image
from generateTTS import load_voice, tts_from_text
from test_utils import get_image_files, extract_image_id

# === KONFIGURASI ===
TEST_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(TEST_DIR, "images-test")
RESULT_TIME_CSV = os.path.join(TEST_DIR, "resultTime.csv")

def main():
    print("=" * 60)
    print("TEST LATENCY - Measuring Processing Time")
    print("=" * 60)
    
    image_files = get_image_files(IMAGES_DIR)
    if not image_files:
        print(f"[ERROR] Tidak ada gambar di folder: {IMAGES_DIR}")
        return
    
    print(f"[INFO] Ditemukan {len(image_files)} gambar.\n")
    
    print("[INFO] Memuat model Piper...")
    voice = load_voice()
    print()
    
    results_time = []
    
    # Dummy file for audio output
    dummy_audio_path = os.path.join(TEST_DIR, "temp_latency_test.wav")
    
    for idx, image_path in enumerate(image_files, 1):
        print(f"Processing {idx}/{len(image_files)}: {os.path.basename(image_path)}")
        
        image_id = extract_image_id(image_path)
        
        # === Measure Ollama ===
        start_ollama = time.time()
        text, _ = generate_text_from_image(image_path, save_to_file=False)
        end_ollama = time.time()
        time_ollama = end_ollama - start_ollama
        
        if not text:
            print(f"  [Failed] Ollama generation failed.")
            results_time.append({
                'image_id': image_id,
                'image_name': os.path.basename(image_path),
                'T_Ollama': 0,
                'T_Piper': 0,
                'status': 'failed_ollama'
            })
            continue
            
        # === Measure Piper ===
        start_piper = time.time()
        try:
            import wave
            with wave.open(dummy_audio_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            status = 'success'
        except Exception as e:
            print(f"  [Failed] Piper generation failed: {e}")
            status = 'failed_piper'
        
        end_piper = time.time()
        time_piper = end_piper - start_piper
        
        if status == 'success':
            print(f"  Ollama: {time_ollama:.4f}s | Piper: {time_piper:.4f}s")
        
        results_time.append({
            'image_id': image_id,
            'image_name': os.path.basename(image_path),
            'T_Ollama': round(time_ollama, 4),
            'T_Piper': round(time_piper, 4),
            'status': status
        })
        
        # Save incrementally
        try:
            with open(RESULT_TIME_CSV, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['image_id', 'image_name', 'T_Ollama', 'T_Piper', 'status']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_time)
        except Exception as e:
            print(f"[ERROR] Saving CSV: {e}")

    # Cleanup dummy file
    if os.path.exists(dummy_audio_path):
        os.remove(dummy_audio_path)

    # Summary
    print(f"\n{'=' * 60}")
    print("LATENCY SUMMARY")
    print(f"{'=' * 60}")
    success_results = [r for r in results_time if r['status'] == 'success']
    if success_results:
        avg_ollama = sum(r['T_Ollama'] for r in success_results) / len(success_results)
        avg_piper = sum(r['T_Piper'] for r in success_results) / len(success_results)
        print(f"Average Ollama Latency: {avg_ollama:.4f} s")
        print(f"Average Piper Latency : {avg_piper:.4f} s")
        print(f"Total Average Latency : {avg_ollama + avg_piper:.4f} s")
    else:
        print("No successful runs to calculate average.")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
