import os
import cv2
from datetime import datetime

# === FOLDER ===
CAPTURE_DIR = os.path.join(os.getcwd(), "captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

def capture_image():
    """
    Ambil satu frame dari kamera index 0 dan simpan ke CAPTURE_DIR.
    Return: path gambar atau None jika gagal.
    """
    print("[STEP] Menangkap gambar dari kamera (index 0)...")
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
    image_path = os.path.join(CAPTURE_DIR, f"capture_{ts}.png")
    try:
        cv2.imwrite(image_path, frame)
        print(f"[INFO] Gambar disimpan: {image_path}")
        return image_path
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan gambar: {e}")
        return None

if __name__ == "__main__":
    img_path = capture_image()
    if img_path:
        print(f"Image captured successfully: {img_path}")
    else:
        print("Failed to capture image.")
