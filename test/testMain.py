import os
import sys
import json
import time

# Tambahkan parent directory ke sys.path agar bisa import modul dari root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generateText import generate_text_from_image
from generateTTS import load_voice, tts_from_text
from test_utils import get_image_files, extract_image_id

# === KONFIGURASI ===
TEST_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(TEST_DIR, "images-test")
RESULT_AUDIO_DIR = os.path.join(TEST_DIR, "resultAudio")
RESULT_TEXT_JSON = os.path.join(TEST_DIR, "resultText.json")

# Buat folder output jika belum ada
os.makedirs(RESULT_AUDIO_DIR, exist_ok=True)

def main():
    print("=" * 60)
    print("TEST MAIN - Automation Only")
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
    
    # 3. Siapkan struktur data untuk hasil teks
    results_text = []
    
    # 4. Proses setiap gambar
    for idx, image_path in enumerate(image_files, 1):
        print(f"\n{'=' * 60}")
        print(f"Memproses gambar {idx}/{len(image_files)}: {os.path.basename(image_path)}")
        print(f"{'=' * 60}")
        
        image_id = extract_image_id(image_path)
        image_basename = os.path.splitext(os.path.basename(image_path))[0]
        
        # === STEP 1: Generate Text dengan Ollama ===
        print(f"[STEP 1] Menghasilkan deskripsi dengan Ollama...")
        
        # Panggil dengan save_to_file=False agar tidak menyimpan ke folder outputs
        text, _ = generate_text_from_image(image_path, save_to_file=False)
        
        if not text:
            print(f"[WARNING] Gagal menghasilkan deskripsi untuk {image_path}. Skip.")
            continue
        
        print(f"[INFO] Deskripsi berhasil dibuat.")
        print(f"[INFO] Teks: {text[:100]}...")  # Preview 100 karakter pertama
        
        # Simpan ke struktur JSON
        results_text.append({
            "image_id": image_id,
            "captions": [text]
        })
        
        # === STEP 2: Generate TTS dengan Piper ===
        print(f"\n[STEP 2] Menghasilkan audio dengan Piper TTS...")
        
        # Tentukan nama file audio berdasarkan nama gambar
        audio_filename = f"{image_basename}.wav"
        audio_path = os.path.join(RESULT_AUDIO_DIR, audio_filename)
        
        try:
            import wave
            with wave.open(audio_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            print(f"[INFO] Audio berhasil dibuat: {audio_path}")
        except Exception as e:
            print(f"[ERROR] Gagal membuat audio: {e}")
            continue
        
        # === STEP 3: Simpan hasil teks secara incremental ===
        try:
            with open(RESULT_TEXT_JSON, 'w', encoding='utf-8') as f:
                json.dump({"annotations": results_text}, f, indent=2, ensure_ascii=False)
            print(f"[INFO] resultText.json diperbarui")
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan JSON: {e}")

    print(f"\n{'=' * 60}")
    print("SELESAI")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
