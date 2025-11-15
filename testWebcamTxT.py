import os
import cv2
import base64
import requests
from datetime import datetime

MODEL_NAME = "customGemma3:latest"
OLLAMA_URL = "http://localhost:11434/api/chat"  # endpoint chat Ollama

CAPTURE_DIR = os.path.join(os.getcwd(), "captures")
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")

os.makedirs(CAPTURE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_image():
    # Tetap gunakan kamera index 0 (seperti di kode kamu)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Kamera (index 0) tidak ditemukan atau tidak bisa dibuka.")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("[ERROR] Tidak dapat menangkap gambar dari kamera.")
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(CAPTURE_DIR, f"test_{ts}.png")
    try:
        cv2.imwrite(image_path, frame)
        print(f"[INFO] Gambar disimpan: {image_path}")
        return image_path
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan gambar: {e}")
        return None

def run_ollama_with_image(image_path):
    if not os.path.exists(image_path):
        print(f"[ERROR] File gambar tidak ada: {image_path}")
        return None

    # Encode gambar ke base64 (sesuai format multimodal Ollama)
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
                "content": "apa yang kamu liat dari gambar ini",
                "images": [img_b64],
            }
        ],
        "stream": False  # supaya respons langsung sekali, bukan streaming
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Gagal memanggil Ollama. Pastikan `ollama serve` aktif dan model '{MODEL_NAME}' tersedia. Detail: {e}")
        return None

    try:
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] Gagal parse JSON dari Ollama: {e}\nRespons mentah: {resp.text}")
        return None

    # Ambil konten jawaban dari field message.content
    try:
        content = data.get("message", {}).get("content", "")
        if not content:
            print(f"[ERROR] Konten kosong atau struktur respons tak terduga.\nRespons: {data}")
            return None
    except Exception as e:
        print(f"[ERROR] Struktur respons tak terduga. Detail: {e}\nRespons: {data}")
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

def clean_files():
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
    print("Perintah: test | clean | q (quit)")
    try:
        while True:
            cmd = input("Masukkan perintah: ").strip().lower()
            if cmd == "test":
                img = capture_image()
                if img:
                    run_ollama_with_image(img)
            elif cmd == "clean":
                clean_files()
            elif cmd in ("q", "quit", "exit"):
                print("Keluar.")
                break
            elif cmd == "":
                continue
            else:
                print("Perintah tidak dikenali. Gunakan: test | clean | q")
    except KeyboardInterrupt:
        print("\n[DONE] Dihentikan oleh pengguna.")

if __name__ == "__main__":
    main()
