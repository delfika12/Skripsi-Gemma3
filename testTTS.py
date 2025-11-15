import time
import os
from pathlib import Path
# Mengubah import agar menggunakan fungsi dari library Piper
from piper import PiperSession, load_voices, synthesize_to_file

# --- 1. Konfigurasi File dan Path ---
# Input file teks yang akan dibaca
INPUT_FILE_PATH = Path("outputs/output_20251111_140142.txt")
# Direktori tempat menyimpan file audio
OUTPUT_DIR = Path("audios")
# Nama model suara yang digunakan (sesuai dengan nama file .onnx)
VOICE_NAME = "id_ID-news_tts-medium"

# Karena file .onnx dan .json berada di folder yang sama dengan skrip,
# kita dapat menggunakan Path(".") yang berarti "direktori saat ini".
VOICES_DIRECTORY = Path(".") 

# --- 2. Fungsi Utama ---
def generate_audio_from_text():
    """
    Membaca file teks dan menghasilkan file audio WAV menggunakan Piper TTS.
    """
    
    # Pastikan direktori output ada
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Buat nama file output dengan timestamp saat ini
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILENAME = f"{timestamp}.wav"
    OUTPUT_FILE_PATH = OUTPUT_DIR / OUTPUT_FILENAME

    print(f"**Memproses file:** {INPUT_FILE_PATH.resolve()}")

    # 1. Baca teks dari file
    try:
        with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
            text_to_speak = f.read()
    except FileNotFoundError:
        print(f"❌ ERROR: File input tidak ditemukan di {INPUT_FILE_PATH.resolve()}")
        return
    
    # 2. Muat model suara Piper
    try:
        print(f"**Mencari model suara di:** {VOICES_DIRECTORY.resolve()}")
        # Load semua suara dari direktori saat ini
        # load_voices akan secara otomatis menemukan pasangan .onnx dan .json
        voices = load_voices(VOICES_DIRECTORY) 
        
        if VOICE_NAME not in voices:
            print(f"❌ ERROR: Model suara '{VOICE_NAME}' tidak ditemukan.")
            print(f"Suara yang berhasil dimuat: {list(voices.keys())}")
            return
            
        voice = voices[VOICE_NAME]
        session = PiperSession(voice) 

    except Exception as e:
        print(f"❌ ERROR saat memuat model suara. Pastikan file '{VOICE_NAME}.onnx' dan '{VOICE_NAME}.onnx.json' ada di folder saat ini.")
        print(f"Detail error: {e}")
        return
        
    print(f"**Menggunakan suara:** {voice.name}")

    # 3. Sintesis teks menjadi file audio
    try:
        print("Sedang membuat audio... mohon tunggu.")
        synthesize_to_file(
            session,
            text_to_speak,
            OUTPUT_FILE_PATH
        )
        print("---")
        print(f"✅ **Berhasil!**")
        print(f"File audio disimpan sebagai: **{OUTPUT_FILE_PATH.resolve()}**")

    except Exception as e:
        print(f"❌ ERROR saat sintesis audio: {e}")

# Jalankan fungsi
if __name__ == "__main__":
    generate_audio_from_text()