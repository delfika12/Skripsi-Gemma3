"""
Script untuk menyesuaikan format JSON antara resultText.json dan GroundTruth.json
agar kompatibel untuk evaluasi SPICE
"""

import json
import os


def convert_predictions_to_standard_format(input_file, output_file=None):
    """
    Konversi format predictions ke format standar
    
    Args:
        input_file: Path ke file JSON input
        output_file: Path ke file JSON output (jika None, akan overwrite input)
    """
    print(f"[INFO] Loading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Cek apakah sudah dalam format yang benar
    if "predictions" in data:
        print("[INFO] File sudah menggunakan key 'predictions'")
        predictions = data["predictions"]
    elif "annotations" in data:
        print("[INFO] File menggunakan key 'annotations', akan diubah ke 'predictions'")
        predictions = data["annotations"]
    else:
        print("[ERROR] Format file tidak dikenali!")
        return False
    
    # Buat format standar
    standard_format = {
        "predictions": predictions
    }
    
    # Simpan
    output_path = output_file or input_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(standard_format, f, indent=2, ensure_ascii=False)
    
    print(f"[INFO] File berhasil disimpan ke: {output_path}")
    print(f"[INFO] Total predictions: {len(predictions)}")
    
    return True


def verify_json_compatibility(predictions_file, ground_truth_file):
    """
    Verifikasi kompatibilitas antara predictions dan ground truth
    
    Args:
        predictions_file: Path ke resultText.json
        ground_truth_file: Path ke GroundTruth.json
    """
    print("\n" + "=" * 60)
    print("VERIFIKASI KOMPATIBILITAS JSON")
    print("=" * 60)
    
    # Load files
    with open(predictions_file, 'r', encoding='utf-8') as f:
        pred_data = json.load(f)
    
    with open(ground_truth_file, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    
    # Get data
    pred_key = "predictions" if "predictions" in pred_data else "annotations"
    predictions = pred_data[pred_key]
    ground_truths = gt_data["annotations"]
    
    # Ekstrak image IDs
    pred_ids = set(item['image_id'] for item in predictions)
    gt_ids = set(item['image_id'] for item in ground_truths)
    
    # Analisis
    print(f"\n[INFO] Predictions:")
    print(f"  - Total: {len(predictions)}")
    print(f"  - Image IDs: {sorted(pred_ids)[:10]}{'...' if len(pred_ids) > 10 else ''}")
    
    print(f"\n[INFO] Ground Truth:")
    print(f"  - Total: {len(ground_truths)}")
    print(f"  - Image IDs: {sorted(gt_ids)[:10]}{'...' if len(gt_ids) > 10 else ''}")
    
    # Cek matching
    matching_ids = pred_ids.intersection(gt_ids)
    missing_in_pred = gt_ids - pred_ids
    extra_in_pred = pred_ids - gt_ids
    
    print(f"\n[INFO] Matching:")
    print(f"  - Matching IDs: {len(matching_ids)}")
    print(f"  - Missing in predictions: {len(missing_in_pred)}")
    if missing_in_pred:
        print(f"    IDs: {sorted(missing_in_pred)}")
    print(f"  - Extra in predictions: {len(extra_in_pred)}")
    if extra_in_pred:
        print(f"    IDs: {sorted(extra_in_pred)}")
    
    # Cek format captions
    print(f"\n[INFO] Format Captions:")
    
    # Sample dari predictions
    sample_pred = predictions[0]
    print(f"  - Predictions sample (image_id={sample_pred['image_id']}):")
    print(f"    Jumlah captions: {len(sample_pred['captions'])}")
    print(f"    Caption 1: {sample_pred['captions'][0][:80]}...")
    
    # Sample dari ground truth
    sample_gt = ground_truths[0]
    print(f"  - Ground Truth sample (image_id={sample_gt['image_id']}):")
    print(f"    Jumlah captions: {len(sample_gt['captions'])}")
    print(f"    Caption 1: {sample_gt['captions'][0][:80]}...")
    
    # Kesimpulan
    print("\n" + "=" * 60)
    if len(matching_ids) == len(gt_ids) and len(extra_in_pred) == 0:
        print("✓ KOMPATIBEL - Semua image IDs cocok!")
    elif len(matching_ids) > 0:
        print(f"⚠ SEBAGIAN KOMPATIBEL - {len(matching_ids)}/{len(gt_ids)} IDs cocok")
    else:
        print("✗ TIDAK KOMPATIBEL - Tidak ada image IDs yang cocok!")
    print("=" * 60)
    
    return len(matching_ids) > 0


def main():
    """Main function"""
    TEST_DIR = os.path.dirname(__file__)
    PREDICTIONS_FILE = os.path.join(TEST_DIR, "resultText.json")
    GROUND_TRUTH_FILE = os.path.join(TEST_DIR, "GroundTruth.json")
    
    # Cek file existence
    if not os.path.exists(PREDICTIONS_FILE):
        print(f"[ERROR] File tidak ditemukan: {PREDICTIONS_FILE}")
        return
    
    if not os.path.exists(GROUND_TRUTH_FILE):
        print(f"[ERROR] File tidak ditemukan: {GROUND_TRUTH_FILE}")
        return
    
    # Verifikasi kompatibilitas
    is_compatible = verify_json_compatibility(PREDICTIONS_FILE, GROUND_TRUTH_FILE)
    
    if not is_compatible:
        print("\n[WARNING] File tidak kompatibel. Perbaiki terlebih dahulu!")
    else:
        print("\n[INFO] File siap untuk evaluasi!")


if __name__ == "__main__":
    main()
