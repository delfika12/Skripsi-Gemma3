"""
METEOR Evaluation untuk Bahasa Indonesia
Menggunakan NLTK METEOR dengan preprocessing untuk bahasa Indonesia

Requirements:
- pip install nltk
- Download NLTK data: nltk.download('wordnet')
"""

import os
import sys
import json
import nltk
from typing import Dict, List
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize

# Tambahkan parent directory ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class IndonesianMETEOREvaluator:
    """
    Evaluator METEOR untuk bahasa Indonesia
    """
    
    def __init__(self):
        """
        Initialize evaluator
        """
        print("[INFO] Initializing Indonesian METEOR Evaluator...")
        self._download_nltk_data()
        
    def _download_nltk_data(self):
        """Download NLTK data yang diperlukan"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("[INFO] Downloading NLTK punkt tokenizer...")
            nltk.download('punkt')
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            print("[INFO] Downloading NLTK punkt_tab tokenizer...")
            nltk.download('punkt_tab')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("[INFO] Downloading NLTK wordnet...")
            nltk.download('wordnet')
        
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            print("[INFO] Downloading NLTK omw...")
            nltk.download('omw-1.4')
        
        print("[INFO] NLTK data ready!")
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text untuk bahasa Indonesia
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Lowercase
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        return tokens
    
    def compute_meteor_score(self, 
                             candidates: Dict[int, List[str]], 
                             references: Dict[int, List[str]]) -> Dict:
        """
        Hitung METEOR score antara candidates dan references
        
        Args:
            candidates: Dict {image_id: [caption1, ...]}
            references: Dict {image_id: [[ref1, ref2, ref3], ...]}
            
        Returns:
            Dict berisi scores per image dan overall score
        """
        print("\n[INFO] Computing METEOR scores...")
        
        scores = {}
        all_scores = []
        
        for image_id in candidates.keys():
            if image_id not in references:
                print(f"[WARNING] Image ID {image_id} tidak ada di references. Skip.")
                continue
            
            candidate_caption = candidates[image_id][0]  # Ambil caption pertama
            reference_captions = references[image_id]
            
            # Preprocess candidate
            candidate_tokens = self.preprocess_text(candidate_caption)
            
            # Preprocess references
            references_tokens = [self.preprocess_text(ref) for ref in reference_captions]
            
            # Hitung METEOR score
            # METEOR menggunakan multiple references
            try:
                score = meteor_score(references_tokens, candidate_tokens)
            except Exception as e:
                print(f"[WARNING] Error computing METEOR for image {image_id}: {e}")
                score = 0.0
            
            scores[image_id] = score
            all_scores.append(score)
            
            print(f"[INFO] Image {image_id}: METEOR = {score:.4f}")
        
        # Hitung overall score
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        return {
            'overall': overall_score,
            'per_image': scores,
            'num_images': len(all_scores)
        }
    
    def evaluate_from_files(self, 
                           predictions_file: str, 
                           ground_truth_file: str,
                           output_file: str = None) -> Dict:
        """
        Evaluasi dari file JSON
        
        Args:
            predictions_file: Path ke resultText.json
            ground_truth_file: Path ke GroundTruth.json
            output_file: Path untuk menyimpan hasil evaluasi (optional)
            
        Returns:
            Dict berisi hasil evaluasi
        """
        print("\n" + "=" * 60)
        print("METEOR EVALUATION - Bahasa Indonesia")
        print("=" * 60)
        
        # Load predictions
        print(f"\n[INFO] Loading predictions from: {predictions_file}")
        with open(predictions_file, 'r', encoding='utf-8') as f:
            predictions_data = json.load(f)
        
        # Load ground truth
        print(f"[INFO] Loading ground truth from: {ground_truth_file}")
        with open(ground_truth_file, 'r', encoding='utf-8') as f:
            ground_truth_data = json.load(f)
        
        # Convert ke format yang dibutuhkan
        # Predictions bisa punya key "predictions" atau "annotations"
        pred_key = "predictions" if "predictions" in predictions_data else "annotations"
        candidates = {
            item['image_id']: item['captions'] 
            for item in predictions_data[pred_key]
        }
        
        references = {
            item['image_id']: item['captions'] 
            for item in ground_truth_data['annotations']
        }
        
        print(f"[INFO] Loaded {len(candidates)} predictions")
        print(f"[INFO] Loaded {len(references)} ground truth annotations")
        
        # Compute scores
        results = self.compute_meteor_score(candidates, references)
        
        # Print results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Overall METEOR Score: {results['overall']:.4f}")
        print(f"Number of images evaluated: {results['num_images']}")
        
        # Interpretasi score
        print("\n" + "=" * 60)
        print("INTERPRETATION")
        print("=" * 60)
        score = results['overall']
        if score >= 0.8:
            interpretation = "Excellent - Caption sangat mirip dengan referensi"
        elif score >= 0.6:
            interpretation = "Good - Caption baik dan relevan"
        elif score >= 0.4:
            interpretation = "Fair - Caption cukup relevan"
        elif score >= 0.2:
            interpretation = "Poor - Caption kurang relevan"
        else:
            interpretation = "Very Poor - Caption sangat berbeda dari referensi"
        
        print(f"Score Range: {score:.4f}")
        print(f"Quality: {interpretation}")
        
        # Save results if output file specified
        if output_file:
            print(f"\n[INFO] Saving results to: {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print("[INFO] Results saved successfully!")
        
        return results


def main():
    """Main function untuk menjalankan evaluasi"""
    
    # Konfigurasi paths
    TEST_DIR = os.path.dirname(__file__)
    PREDICTIONS_FILE = os.path.join(TEST_DIR, "resultText.json")
    GROUND_TRUTH_FILE = os.path.join(TEST_DIR, "GroundTruthAsli.json")
    OUTPUT_FILE = os.path.join(TEST_DIR, "meteor_results.json")
    
    # Cek apakah file ada
    if not os.path.exists(PREDICTIONS_FILE):
        print(f"[ERROR] File predictions tidak ditemukan: {PREDICTIONS_FILE}")
        return
    
    if not os.path.exists(GROUND_TRUTH_FILE):
        print(f"[ERROR] File ground truth tidak ditemukan: {GROUND_TRUTH_FILE}")
        return
    
    # Inisialisasi evaluator
    try:
        evaluator = IndonesianMETEOREvaluator()
    except Exception as e:
        print(f"[ERROR] Gagal inisialisasi evaluator: {e}")
        return
    
    # Jalankan evaluasi
    try:
        results = evaluator.evaluate_from_files(
            PREDICTIONS_FILE,
            GROUND_TRUTH_FILE,
            OUTPUT_FILE
        )
        
        print("\n" + "=" * 60)
        print("EVALUATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Evaluasi gagal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
