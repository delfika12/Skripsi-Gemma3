import os
import base64
import requests
from datetime import datetime
import glob

# === KONFIGURASI OLLAMA ===
MODEL_NAME = "customGemma3"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"  # endpoint chat Ollama

# === FOLDER ===
CAPTURE_DIR = os.path.join(os.getcwd(), "captures")
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")

os.makedirs(CAPTURE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_ollama_with_image(image_path):
    """
    Kirim gambar ke model Gemma3 (Ollama multimodal).
    Hasil teks disimpan ke OUTPUT_DIR sebagai .txt.
    Return: path file .txt atau None.
    """
    if not os.path.exists(image_path):
        print(f"[ERROR] File gambar tidak ada: {image_path}")
        return None

    # Encode ke base64 (format multimodal Ollama)
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"[ERROR] Gagal membaca/encode gambar: {e}")
        return None

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": "Apa yang kamu lihat dari gambar ini? Jelaskan singkat dalam bahasa Indonesia.",
                "images": [img_b64],
            }
        ],
        "stream": False  # supaya respons langsung sekali, bukan streaming
    }

    print(f"[STEP] Mengirim gambar {os.path.basename(image_path)} ke Ollama (Gemma3)...")
    try:
        resp = requests.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Gagal memanggil Ollama. "
              f"Pastikan `ollama serve` aktif dan model '{MODEL_NAME}' tersedia. Detail: {e}")
        return None

    try:
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] Gagal parse JSON dari Ollama: {e}\nRespons mentah: {resp.text}")
        return None

    # Ambil konten jawaban dari field message.content
    content = data.get("message", {}).get("content", "")
    if not content:
        print(f"[ERROR] Konten kosong atau struktur respons tak terduga.\nRespons: {data}")
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"output_{ts}.txt")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] Hasil interpretasi disimpan: {output_path}")
        return output_path
    except Exception as e:
        print(f"[ERROR] Gagal menulis file output: {e}")
        return None


def generate_text_from_image(image_path):
    """
    Fungsi utama yang akan dipanggil modul lain:
    1. Terima path gambar
    2. Kirim ke Ollama
    3. Baca teks dari file .txt

    Return: (text, txt_path) atau (None, None) jika gagal.
    """
    txt_path = run_ollama_with_image(image_path)
    if not txt_path:
        return None, None

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except Exception as e:
        print(f"[ERROR] Gagal membaca file teks: {e}")
        return None, txt_path

    print("[INFO] Teks hasil interpretasi berhasil dibaca.")
    return text, txt_path


def get_latest_capture():
    """
    Mencari file gambar terbaru di folder captures.
    """
    list_of_files = glob.glob(os.path.join(CAPTURE_DIR, '*'))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def clean_files():
    """
    Menghapus semua file dalam captures/ dan outputs/
    """
    removed = 0
    for folder in (CAPTURE_DIR, OUTPUT_DIR):
        for name in os.listdir(folder):
            fpath = os.path.join(folder, name)
            try:
                os.remove(fpath)
                removed += 1
            except Exception:
                pass
    print(f"[INFO] Bersih-bersih selesai. File terhapus: {removed}")


def main():
    """
    Mode debug mandiri:
    - Ambil gambar terbaru dari captures/
    - Kirim ke Gemma3
    - Tampilkan hasil
    """
    print("=== Generate Text Otomatis ===")
    latest_img = get_latest_capture()
    
    if latest_img:
        print(f"[INFO] Menggunakan gambar terbaru: {latest_img}")
        text, txt_path = generate_text_from_image(latest_img)
        if text:
            print("\n=== HASIL TEKS ===")
            print(text)
            print("==================\n")
    else:
        print("[WARNING] Tidak ada gambar di folder captures. Jalankan captureImage.py terlebih dahulu.")


if __name__ == "__main__":
    main()
