"""
Script untuk menganalisis hasil evaluasi SPICE
Memberikan statistik lengkap dan insight tentang kualitas caption
"""

import json
import os
from typing import Dict, List, Tuple


def load_results(results_file: str) -> Dict:
    """Load hasil evaluasi dari JSON file"""
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_captions(predictions_file: str, ground_truth_file: str) -> Tuple[Dict, Dict]:
    """Load predictions dan ground truth captions"""
    with open(predictions_file, 'r', encoding='utf-8') as f:
        pred_data = json.load(f)
    
    with open(ground_truth_file, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    
    pred_key = "predictions" if "predictions" in pred_data else "annotations"
    
    predictions = {
        str(item['image_id']): item['captions'][0] 
        for item in pred_data[pred_key]
    }
    
    ground_truths = {
        str(item['image_id']): item['captions'] 
        for item in gt_data['annotations']
    }
    
    return predictions, ground_truths


def categorize_scores(scores: Dict[str, float]) -> Dict[str, List[str]]:
    """Kategorikan scores berdasarkan kualitas"""
    categories = {
        'Sangat Buruk (0.0-0.3)': [],
        'Buruk (0.3-0.5)': [],
        'Cukup (0.5-0.7)': [],
        'Baik (0.7-0.9)': [],
        'Sangat Baik (0.9-1.0)': []
    }
    
    for image_id, score in scores.items():
        if score < 0.3:
            categories['Sangat Buruk (0.0-0.3)'].append(image_id)
        elif score < 0.5:
            categories['Buruk (0.3-0.5)'].append(image_id)
        elif score < 0.7:
            categories['Cukup (0.5-0.7)'].append(image_id)
        elif score < 0.9:
            categories['Baik (0.7-0.9)'].append(image_id)
        else:
            categories['Sangat Baik (0.9-1.0)'].append(image_id)
    
    return categories


def print_statistics(results: Dict):
    """Print statistik lengkap"""
    scores = list(results['per_image'].values())
    
    print("\n" + "=" * 60)
    print("STATISTIK EVALUASI SPICE")
    print("=" * 60)
    
    print(f"\n📊 Overall Score: {results['overall']:.4f}")
    print(f"📈 Jumlah Gambar: {results['num_images']}")
    
    print(f"\n📉 Statistik Deskriptif:")
    print(f"  - Mean:   {sum(scores) / len(scores):.4f}")
    print(f"  - Min:    {min(scores):.4f}")
    print(f"  - Max:    {max(scores):.4f}")
    print(f"  - Median: {sorted(scores)[len(scores)//2]:.4f}")
    
    # Standar deviasi
    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    std_dev = variance ** 0.5
    print(f"  - Std Dev: {std_dev:.4f}")


def print_categories(categories: Dict[str, List[str]]):
    """Print kategorisasi kualitas"""
    print("\n" + "=" * 60)
    print("KATEGORISASI KUALITAS")
    print("=" * 60)
    
    for category, image_ids in categories.items():
        percentage = (len(image_ids) / sum(len(v) for v in categories.values())) * 100
        print(f"\n{category}")
        print(f"  Jumlah: {len(image_ids)} ({percentage:.1f}%)")
        if image_ids:
            print(f"  Image IDs: {', '.join(sorted(image_ids, key=int)[:10])}")
            if len(image_ids) > 10:
                print(f"             ... dan {len(image_ids) - 10} lainnya")


def print_best_worst(results: Dict, predictions: Dict, ground_truths: Dict, n: int = 5):
    """Print caption terbaik dan terburuk"""
    sorted_scores = sorted(results['per_image'].items(), key=lambda x: x[1], reverse=True)
    
    print("\n" + "=" * 60)
    print(f"TOP {n} CAPTION TERBAIK")
    print("=" * 60)
    
    for i, (image_id, score) in enumerate(sorted_scores[:n], 1):
        print(f"\n#{i} - Image {image_id} (Score: {score:.4f})")
        print(f"  Prediction:")
        print(f"    {predictions[image_id][:150]}...")
        print(f"  Ground Truth (1st):")
        print(f"    {ground_truths[image_id][0][:150]}...")
    
    print("\n" + "=" * 60)
    print(f"TOP {n} CAPTION TERBURUK")
    print("=" * 60)
    
    for i, (image_id, score) in enumerate(sorted_scores[-n:], 1):
        print(f"\n#{i} - Image {image_id} (Score: {score:.4f})")
        print(f"  Prediction:")
        print(f"    {predictions[image_id][:150]}...")
        print(f"  Ground Truth (1st):")
        print(f"    {ground_truths[image_id][0][:150]}...")


def save_detailed_report(results: Dict, predictions: Dict, ground_truths: Dict, 
                        categories: Dict, output_file: str):
    """Simpan laporan detail ke file"""
    report = {
        'overall_score': results['overall'],
        'num_images': results['num_images'],
        'statistics': {
            'mean': sum(results['per_image'].values()) / len(results['per_image']),
            'min': min(results['per_image'].values()),
            'max': max(results['per_image'].values()),
            'median': sorted(results['per_image'].values())[len(results['per_image'])//2]
        },
        'categories': {k: len(v) for k, v in categories.items()},
        'detailed_results': []
    }
    
    for image_id, score in sorted(results['per_image'].items(), key=lambda x: int(x[0])):
        report['detailed_results'].append({
            'image_id': int(image_id),
            'score': score,
            'prediction': predictions[image_id],
            'ground_truths': ground_truths[image_id]
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] Laporan detail disimpan ke: {output_file}")


def main():
    """Main function"""
    TEST_DIR = os.path.dirname(__file__)
    RESULTS_FILE = os.path.join(TEST_DIR, "spice_results.json")
    PREDICTIONS_FILE = os.path.join(TEST_DIR, "resultText.json")
    GROUND_TRUTH_FILE = os.path.join(TEST_DIR, "GroundTruth.json")
    DETAILED_REPORT_FILE = os.path.join(TEST_DIR, "detailed_report.json")
    
    # Load data
    print("[INFO] Loading data...")
    results = load_results(RESULTS_FILE)
    predictions, ground_truths = load_captions(PREDICTIONS_FILE, GROUND_TRUTH_FILE)
    
    # Analisis
    categories = categorize_scores(results['per_image'])
    
    # Print hasil
    print_statistics(results)
    print_categories(categories)
    print_best_worst(results, predictions, ground_truths, n=5)
    
    # Simpan laporan detail
    save_detailed_report(results, predictions, ground_truths, categories, DETAILED_REPORT_FILE)
    
    print("\n" + "=" * 60)
    print("ANALISIS SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
