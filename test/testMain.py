import os
import sys
import json
import csv
import time
import glob
from pathlib import Path

# Tambahkan parent directory ke sys.path agar bisa import modul dari root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generateText import generate_text_from_image
from generateTTS import load_voice, tts_from_text

# === KONFIGURASI ===
TEST_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(TEST_DIR, "images-test")
RESULT_AUDIO_DIR = os.path.join(TEST_DIR, "resultAudio")
RESULT_TEXT_JSON = os.path.join(TEST_DIR, "resultText.json")
RESULT_TIME_CSV = os.path.join(TEST_DIR, "resultTime.csv")

# Buat folder output jika belum ada
os.makedirs(RESULT_AUDIO_DIR, exist_ok=True)


def get_image_files(directory):
    """
    Ambil semua file gambar dari directory.
    Return: list of image paths sorted by numeric value in filename
    """
    extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    # Sort berdasarkan angka dalam nama file
    import re
    def extract_number(filepath):
        filename = os.path.basename(filepath)
        numbers = re.findall(r'\d+', filename)
        return int(numbers[0]) if numbers else 0
    
    return sorted(image_files, key=extract_number)


def extract_image_id(image_path):
    """
    Ekstrak image_id dari nama file.
    Contoh: '1.png' -> 1, 'image_5.jpg' -> 5
    """
    filename = os.path.basename(image_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Coba ekstrak angka dari nama file
    import re
    numbers = re.findall(r'\d+', name_without_ext)
    if numbers:
        return int(numbers[0])
    else:
        # Jika tidak ada angka, gunakan hash dari nama file
        return hash(name_without_ext) % 10000


def main():
    print("=" * 60)
    print("TEST MAIN - Batch Processing")
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
    
    # 3. Siapkan struktur data untuk hasil
    results_text = []
    results_time = []
    
    # 4. Proses setiap gambar
    for idx, image_path in enumerate(image_files, 1):
        print(f"\n{'=' * 60}")
        print(f"Memproses gambar {idx}/{len(image_files)}: {os.path.basename(image_path)}")
        print(f"{'=' * 60}")
        
        image_id = extract_image_id(image_path)
        image_basename = os.path.splitext(os.path.basename(image_path))[0]
        
        # === STEP 1: Generate Text dengan Ollama ===
        print(f"[STEP 1] Menghasilkan deskripsi dengan Ollama...")
        start_ollama = time.time()
        
        # Panggil dengan save_to_file=False agar tidak menyimpan ke folder outputs
        text, _ = generate_text_from_image(image_path, save_to_file=False)
        
        end_ollama = time.time()
        time_ollama = end_ollama - start_ollama
        
        if not text:
            print(f"[WARNING] Gagal menghasilkan deskripsi untuk {image_path}. Skip.")
            results_time.append({
                'image_id': image_id,
                'image_name': os.path.basename(image_path),
                'T_Ollama': 0,
                'T_Piper': 0,
                'status': 'failed_ollama'
            })
            continue
        
        print(f"[INFO] Deskripsi berhasil dibuat (waktu: {time_ollama:.2f}s)")
        print(f"[INFO] Teks: {text[:100]}...")  # Preview 100 karakter pertama
        
        # Simpan ke struktur JSON
        results_text.append({
            "image_id": image_id,
            "captions": [text]  # Dalam format list seperti GroundTruth.json
        })
        
        # === STEP 2: Generate TTS dengan Piper ===
        print(f"\n[STEP 2] Menghasilkan audio dengan Piper TTS...")
        start_piper = time.time()
        
        # Tentukan nama file audio berdasarkan nama gambar
        audio_filename = f"{image_basename}.wav"
        audio_path = os.path.join(RESULT_AUDIO_DIR, audio_filename)
        
        # Gunakan fungsi tts_from_text dengan custom output path
        try:
            import wave
            with wave.open(audio_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            print(f"[INFO] Audio berhasil dibuat: {audio_path}")
        except Exception as e:
            print(f"[ERROR] Gagal membuat audio: {e}")
            end_piper = time.time()
            time_piper = end_piper - start_piper
            results_time.append({
                'image_id': image_id,
                'image_name': os.path.basename(image_path),
                'T_Ollama': time_ollama,
                'T_Piper': 0,
                'status': 'failed_piper'
            })
            continue
        
        end_piper = time.time()
        time_piper = end_piper - start_piper
        
        print(f"[INFO] Audio berhasil dibuat (waktu: {time_piper:.2f}s)")
        
        # === STEP 3: Catat waktu inferensi ===
        results_time.append({
            'image_id': image_id,
            'image_name': os.path.basename(image_path),
            'T_Ollama': round(time_ollama, 4),
            'T_Piper': round(time_piper, 4),
            'status': 'success'
        })
        
        print(f"[SUMMARY] Ollama: {time_ollama:.2f}s | Piper: {time_piper:.2f}s")
        
        # === STEP 4: Simpan hasil setelah setiap gambar selesai ===
        print(f"\n[STEP 3] Menyimpan hasil ke file...")
        
        # Simpan resultText.json
        try:
            with open(RESULT_TEXT_JSON, 'w', encoding='utf-8') as f:
                json.dump({"annotations": results_text}, f, indent=2, ensure_ascii=False)
            print(f"[INFO] resultText.json diperbarui ({len(results_text)} anotasi)")
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan JSON: {e}")
        
        # Simpan resultTime.csv
        try:
            with open(RESULT_TIME_CSV, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['image_id', 'image_name', 'T_Ollama', 'T_Piper', 'status']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_time)
            print(f"[INFO] resultTime.csv diperbarui ({len(results_time)} entri)")
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan CSV: {e}")

    
    # 5. Simpan hasil ke file
    print(f"\n{'=' * 60}")
    print("Menyimpan hasil...")
    print(f"{'=' * 60}")
    
    # Simpan resultText.json
    try:
        with open(RESULT_TEXT_JSON, 'w', encoding='utf-8') as f:
            json.dump({"annotations": results_text}, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Hasil teks disimpan ke: {RESULT_TEXT_JSON}")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan JSON: {e}")
    
    # Simpan resultTime.csv
    try:
        with open(RESULT_TIME_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['image_id', 'image_name', 'T_Ollama', 'T_Piper', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results_time)
        print(f"[INFO] Waktu inferensi disimpan ke: {RESULT_TIME_CSV}")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan CSV: {e}")
    
    # 6. Tampilkan ringkasan
    print(f"\n{'=' * 60}")
    print("RINGKASAN")
    print(f"{'=' * 60}")
    print(f"Total gambar diproses: {len(image_files)}")
    print(f"Berhasil: {sum(1 for r in results_time if r['status'] == 'success')}")
    print(f"Gagal: {sum(1 for r in results_time if r['status'] != 'success')}")
    
    if results_time:
        avg_ollama = sum(r['T_Ollama'] for r in results_time if r['T_Ollama'] > 0) / max(1, sum(1 for r in results_time if r['T_Ollama'] > 0))
        avg_piper = sum(r['T_Piper'] for r in results_time if r['T_Piper'] > 0) / max(1, sum(1 for r in results_time if r['T_Piper'] > 0))
        print(f"\nRata-rata waktu Ollama: {avg_ollama:.2f}s")
        print(f"Rata-rata waktu Piper: {avg_piper:.2f}s")
    
    print(f"\n{'=' * 60}")
    print("SELESAI")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
