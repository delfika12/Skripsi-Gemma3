import os
import sys
import json
import time
import csv

# Tambahkan parent directory ke sys.path agar bisa import modul dari root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generateText import generate_text_from_image
from generateTTS import load_voice, tts_from_text
from test_utils import get_image_files, extract_image_id, ResourceMonitor

# === KONFIGURASI ===
TEST_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(TEST_DIR, "images-test")

# Folder Output Baru
TEST_RESULT_DIR = os.path.join(TEST_DIR, "Test Result")
RESULT_TEXT_JSON = os.path.join(TEST_RESULT_DIR, "resultText.json")
RESULT_METRICS_CSV = os.path.join(TEST_RESULT_DIR, "resultMetrics.csv")
RESULT_TIMELINE_CSV = os.path.join(TEST_RESULT_DIR, "resultTimeline.csv")

# Buat folder output jika belum ada
os.makedirs(TEST_RESULT_DIR, exist_ok=True)

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
    print("TEST MAIN - Automation with Full Monitoring")
    print("=" * 60)
    
    # 1. Ambil semua gambar dari folder images-test
    image_files = get_image_files(IMAGES_DIR)
    
    if not image_files:
        print(f"[ERROR] Tidak ada gambar di folder: {IMAGES_DIR}")
        return
    
    print(f"[INFO] Ditemukan {len(image_files)} gambar untuk diproses\n")
    
    # 2. Load model Piper sekali saja (untuk efisiensi)
    print("[INFO] Memuat model Piper...")
    voice = load_voice()
    print()
    
    # 3. Siapkan struktur data
    results_text = []
    
    # Initialize CSVs
    with open(RESULT_METRICS_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'image_id', 'image_name', 
            'latency_ollama_s', 'latency_piper_s', 'latency_total_s',
            'avg_power_mw', 'energy_mwh',
            'avg_cpu_util_pct', 'avg_gpu_util_pct', 'avg_ram_usage_mb', 'avg_vram_gpu_mb',
            'status'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    with open(RESULT_TIMELINE_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['timestamp', 'relative_time', 'image_id', 'image_name', 'power_mw', 'cpu_util_pct', 'gpu_util_pct', 'ram_usage_mb', 'vram_gpu_mb']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    # Dummy file untuk proses TTS (agar tidak menyimpan banyak file audio)
    dummy_audio_path = os.path.join(TEST_RESULT_DIR, "temp_audio_proc.wav")

    # 4. Proses setiap gambar
    for idx, image_path in enumerate(image_files, 1):
        print(f"\n{'=' * 60}")
        print(f"Memproses gambar {idx}/{len(image_files)}: {os.path.basename(image_path)}")
        print(f"{'=' * 60}")
        
        image_id = extract_image_id(image_path)
        image_basename = os.path.splitext(os.path.basename(image_path))[0]
        image_name = os.path.basename(image_path)
        
        # Start Monitor Resource
        monitor = ResourceMonitor(interval=0.1)
        monitor.start()
        
        # === STEP 1: Generate Text dengan Ollama ===
        print(f"[STEP 1] Menghasilkan deskripsi dengan Ollama...")
        start_ollama = time.time()
        
        # Panggil dengan save_to_file=False agar tidak menyimpan ke folder outputs
        text, _ = generate_text_from_image(image_path, save_to_file=False)
        
        end_ollama = time.time()
        time_ollama = end_ollama - start_ollama
        
        if not text:
            print(f"[WARNING] Gagal menghasilkan deskripsi untuk {image_path}. Skip.")
            monitor.stop()
            continue
        
        print(f"[INFO] Deskripsi berhasil dibuat (Latency: {time_ollama:.4f}s)")
        print(f"[INFO] Teks: {text[:100]}...")  # Preview 100 karakter pertama
        
        # Simpan ke struktur JSON
        results_text.append({
            "image_id": image_id,
            "captions": [text]
        })
        
        # === STEP 2: Generate TTS dengan Piper ===
        print(f"\n[STEP 2] Menghasilkan audio dengan Piper TTS...")
        start_piper = time.time()
        
        status = 'failed'
        try:
            import wave
            # Gunakan dummy file yang akan di-overwrite setiap kali
            with wave.open(dummy_audio_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            # print(f"[INFO] Audio berhasil diproses (tidak disimpan).")
            status = 'success'
        except Exception as e:
            print(f"[ERROR] Gagal membuat audio: {e}")
            
        end_piper = time.time()
        time_piper = end_piper - start_piper
        print(f"[INFO] TTS selesai (Latency: {time_piper:.4f}s)")
        
        # Stop Monitor
        monitor.stop()
        
        # === STEP 3: Hitung & Simpan Metrik ===
        avgs = monitor.get_averages()
        stats_list = monitor.get_stats()
        energy_mwh = calculate_energy(stats_list)
        
        print(f"\n[METRICS]")
        print(f"  Total Latency: {time_ollama + time_piper:.4f} s")
        print(f"  Avg Power    : {avgs['power']:.2f} mW")
        print(f"  Energy       : {energy_mwh:.4f} mWh")
        print(f"  Avg CPU Util : {avgs['cpu_util']:.2f} %")
        print(f"  Avg GPU Util : {avgs['gpu_util']:.2f} %")
        
        # Save Metrics to CSV
        try:
            with open(RESULT_METRICS_CSV, 'a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'image_id', 'image_name', 
                    'latency_ollama_s', 'latency_piper_s', 'latency_total_s',
                    'avg_power_mw', 'energy_mwh',
                    'avg_cpu_util_pct', 'avg_gpu_util_pct', 'avg_ram_usage_mb', 'avg_vram_gpu_mb',
                    'status'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow({
                    'image_id': image_id,
                    'image_name': image_name,
                    'latency_ollama_s': round(time_ollama, 4),
                    'latency_piper_s': round(time_piper, 4),
                    'latency_total_s': round(time_ollama + time_piper, 4),
                    'avg_power_mw': round(avgs['power'], 2),
                    'energy_mwh': round(energy_mwh, 4),
                    'avg_cpu_util_pct': round(avgs['cpu_util'], 2),
                    'avg_gpu_util_pct': round(avgs['gpu_util'], 2),
                    'avg_ram_usage_mb': round(avgs['ram_usage'], 2),
                    'avg_vram_gpu_mb': round(avgs['vram_gpu'], 2),
                    'status': status
                })
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan Metrics CSV: {e}")

        # Save Timeline to CSV
        try:
            with open(RESULT_TIMELINE_CSV, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'relative_time', 'image_id', 'image_name', 'power_mw', 'cpu_util_pct', 'gpu_util_pct', 'ram_usage_mb', 'vram_gpu_mb']
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
                        'ram_usage_mb': s['ram_usage'],
                        'vram_gpu_mb': s['vram_gpu']
                    })
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan Timeline CSV: {e}")

        # === STEP 4: Simpan hasil teks secara incremental ===
        try:
            with open(RESULT_TEXT_JSON, 'w', encoding='utf-8') as f:
                json.dump({"annotations": results_text}, f, indent=2, ensure_ascii=False)
            print(f"[INFO] resultText.json diperbarui")
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan JSON: {e}")

    # Cleanup dummy file
    if os.path.exists(dummy_audio_path):
        os.remove(dummy_audio_path)

    print(f"\n{'=' * 60}")
    print("SELESAI")
    print(f"All results saved in: {TEST_RESULT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
