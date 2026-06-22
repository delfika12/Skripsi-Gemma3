import os
import glob
import wave
import datetime

from piper import PiperVoice  # pastikan ini yang dipakai

# === PATH FOLDER ===
OUTPUT_FOLDER = "outputs"   # tempat file .txt
AUDIO_FOLDER = "audios"     # tempat simpan file .wav
MODEL_PATH = "id_ID-news_tts-medium.onnx"  # sesuaikan kalau beda lokasi

os.makedirs(AUDIO_FOLDER, exist_ok=True)


def get_latest_txt(folder=OUTPUT_FOLDER):
    
    files = glob.glob(os.path.join(folder, "*.txt"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_voice(model_path=MODEL_PATH):
    
    print("[INFO] Memuat model Piper...")
    voice = PiperVoice.load(model_path)
    print("[INFO] Model Piper siap.")
    return voice


def tts_from_text(text, voice=None, audio_folder=AUDIO_FOLDER):
    
    if not text or not text.strip():
        print("[ERROR] Teks kosong, batal TTS.")
        return None

    if voice is None:
        voice = load_voice()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(audio_folder, f"output_{timestamp}.wav")

    print("[INFO] Mengubah teks menjadi audio (Piper TTS)...")
    try:
        with wave.open(output_path, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
    except Exception as e:
        print(f"[ERROR] Gagal membuat file audio: {e}")
        return None

    print(f"[INFO] Audio berhasil dibuat: {output_path}")
    return output_path


def tts_from_latest_txt(voice=None, output_folder=OUTPUT_FOLDER):
    
    latest_file = get_latest_txt(output_folder)
    if latest_file is None:
        print("[ERROR] Tidak ada file .txt di folder outputs/")
        return None

    print(f"[INFO] Membaca file terbaru: {latest_file}")
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except Exception as e:
        print(f"[ERROR] Gagal membaca file teks: {e}")
        return None

    print(f"[DEBUG] Panjang teks: {len(text)} karakter")

    return tts_from_text(text, voice=voice)


def main():
    
    voice = load_voice()
    wav_path = tts_from_latest_txt(voice=voice)
    if wav_path:
        print(f"[DEBUG] File WAV dihasilkan: {wav_path}")


if __name__ == "__main__":
    main()
