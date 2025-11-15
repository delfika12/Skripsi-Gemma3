import os
import cv2
from datetime import datetime
from ollama import chat  # tetap pakai ini; parsing tidak diubah (sesuai permintaan)

MODEL_NAME = "customGemma3"
CAPTURE_DIR = os.path.join(os.getcwd(), "captures")
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")

os.makedirs(CAPTURE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_image():
    # Tetap gunakan kamera index 2 (tanpa warm-up & tanpa set resolusi)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Kamera (index 2) tidak ditemukan atau tidak bisa dibuka.")
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

    try:
        # Kirim gambar ke model (content dikosongkan sesuai kode asli)
        response = chat(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": "",
                "images": [image_path]
            }]
        )
    except Exception as e:
        print(f"[ERROR] Gagal memanggil Ollama. Pastikan `ollama serve` aktif dan model '{MODEL_NAME}' tersedia. Detail: {e}")
        return None

    # NOTE: saran #1 TIDAK diterapkan -> tetap akses seperti kode asli
    try:
        content = response['message'].content  # sesuai permintaan: tidak diubah
    except Exception as e:
        print(f"[ERROR] Struktur respons tak terduga. (Saran #1 tidak diterapkan) Detail: {e}\nRespons mentah: {response}")
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
