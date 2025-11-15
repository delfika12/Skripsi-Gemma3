import os
import glob
import wave
import datetime

from piper import PiperVoice  # <- penting

# === PATH FOLDER ===
OUTPUT_FOLDER = "outputs"
AUDIO_FOLDER = "audios"
MODEL_PATH = "id_ID-news_tts-medium.onnx"  # atau path lengkap ke modelmu

os.makedirs(AUDIO_FOLDER, exist_ok=True)

print("[INFO] Memuat model Piper...")
voice = PiperVoice.load(MODEL_PATH)
print("[INFO] Model siap, sample rate:", voice.config.sample_rate)

def get_latest_txt(folder):
    files = glob.glob(os.path.join(folder, "*.txt"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

# Ambil file txt terbaru
latest_file = get_latest_txt(OUTPUT_FOLDER)

if latest_file is None:
    print("[ERROR] Tidak ada file .txt di folder outputs/")
    raise SystemExit(1)

print(f"[INFO] Membaca file terbaru: {latest_file}")

with open(latest_file, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("[ERROR] File txt kosong.")
    raise SystemExit(1)

print("[INFO] Mengubah teks menjadi audio...")

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(AUDIO_FOLDER, f"output_{timestamp}.wav")

# Buka file WAV dan set parameter sesuai config Piper
with wave.open(output_path, "wb") as wav_file:
    wav_file.setframerate(voice.config.sample_rate)
    wav_file.setsampwidth(2)   # 16-bit
    wav_file.setnchannels(1)   # mono

    # Piper akan stream audio langsung ke wav_file
    voice.synthesize(text, wav_file)

print(f"[INFO] Audio berhasil dibuat: {output_path}")
