# Evaluasi METEOR untuk Bahasa Indonesia

Panduan lengkap untuk mengevaluasi caption generation model menggunakan METEOR (Metric for Evaluation of Translation with Explicit ORdering) untuk bahasa Indonesia.

## 📋 Daftar Isi

1. [Tentang METEOR](#tentang-meteor)
2. [Instalasi](#instalasi)
3. [Persiapan Data](#persiapan-data)
4. [Cara Penggunaan](#cara-penggunaan)
5. [Penjelasan Metrik](#penjelasan-metrik)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Tentang METEOR

**METEOR** (Metric for Evaluation of Translation with Explicit ORdering) adalah metrik evaluasi yang dirancang untuk mengatasi kelemahan BLEU dengan mempertimbangkan:

✅ **Stemming** - Mengenali kata dengan akar yang sama  
✅ **Synonyms** - Mempertimbangkan sinonim  
✅ **Word Order** - Menghitung penalty untuk perbedaan urutan kata  
✅ **Recall** - Lebih fokus pada recall dibanding precision  

### Keunggulan METEOR untuk Bahasa Indonesia:

- Lebih robust terhadap variasi bahasa
- Mempertimbangkan morfologi kata
- Cocok untuk bahasa dengan struktur fleksibel
- Korelasi tinggi dengan human judgment

---

## 🔧 Instalasi

### 1. Install Dependencies

```bash
pip install nltk
```

### 2. Download NLTK Data

Script akan otomatis download data yang diperlukan saat pertama kali dijalankan:
- `punkt` - Tokenizer
- `wordnet` - Untuk synonym matching
- `omw-1.4` - Open Multilingual Wordnet

Atau download manual:

```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
```

---

## 📁 Persiapan Data

### Format File yang Dibutuhkan

Anda memerlukan 2 file JSON:

#### 1. **resultText.json** (Predictions dari Model)

Format:
```json
{
  "predictions": [
    {
      "image_id": 1,
      "captions": [
        "Deskripsi gambar dari model Anda..."
      ]
    }
  ]
}
```

**Catatan:** 
- Key bisa `"predictions"` atau `"annotations"`
- Setiap image hanya perlu 1 caption (caption pertama yang akan digunakan)

#### 2. **GroundTruthTesting.json** (Reference Captions)

Format:
```json
{
  "annotations": [
    {
      "image_id": 1,
      "captions": [
        "Caption referensi 1 untuk gambar 1",
        "Caption referensi 2 untuk gambar 1",
        "Caption referensi 3 untuk gambar 1"
      ]
    }
  ]
}
```

**Catatan:**
- Setiap image sebaiknya punya 3-5 caption referensi
- METEOR akan menggunakan semua referensi untuk evaluasi

---

## 🚀 Cara Penggunaan

### Langkah 1: Jalankan Evaluasi METEOR

```bash
python evaluate_meteor.py
```

Script ini akan:
1. Download NLTK data jika belum ada
2. Load predictions dan ground truth
3. Preprocess semua captions (lowercase, tokenize)
4. Hitung METEOR score untuk setiap gambar
5. Hitung overall METEOR score
6. Simpan hasil ke `meteor_results_testing.json`

### Langkah 2: Lihat Hasil

Hasil evaluasi akan disimpan di `meteor_results_testing.json`:

```json
{
  "overall": 0.7543,
  "per_image": {
    "1": 0.7234,
    "2": 0.7852
  },
  "num_images": 2
}
```

---

## 📊 Penjelasan Metrik

### Apa itu METEOR?

**METEOR** menghitung similarity antara candidate caption dan reference captions dengan mempertimbangkan:

1. **Exact Match** - Kata yang sama persis
2. **Stem Match** - Kata dengan akar yang sama (e.g., "berjalan" vs "jalan")
3. **Synonym Match** - Kata dengan makna serupa
4. **Word Order** - Penalty untuk perbedaan urutan kata

### Cara Kerja METEOR

1. **Alignment**: Align kata-kata antara candidate dan references
2. **Matching**: Hitung jumlah matches (exact, stem, synonym)
3. **Precision & Recall**: 
   - Precision = matches / words in candidate
   - Recall = matches / words in reference
4. **F-mean**: Hitung harmonic mean dengan bobot lebih ke recall
5. **Penalty**: Kurangi score berdasarkan perbedaan word order
6. **Final Score**: F-mean × (1 - penalty)

### Formula METEOR

```
F-mean = (P × R) / (α × P + (1-α) × R)
Penalty = γ × (chunks / matches)^β
METEOR = F-mean × (1 - Penalty)
```

Dimana:
- P = Precision
- R = Recall
- α = 0.9 (bobot untuk recall)
- β = 3.0 (parameter penalty)
- γ = 0.5 (weight penalty)

### Interpretasi Score

- **0.8 - 1.0**: Excellent - Caption sangat mirip dengan referensi
- **0.6 - 0.8**: Good - Caption baik dan relevan
- **0.4 - 0.6**: Fair - Caption cukup relevan
- **0.2 - 0.4**: Poor - Caption kurang relevan
- **0.0 - 0.2**: Very Poor - Caption sangat berbeda

### Keunggulan METEOR

✅ Lebih robust terhadap variasi bahasa  
✅ Mempertimbangkan sinonim dan stemming  
✅ Fokus pada recall (menangkap konten penting)  
✅ Penalty untuk word order yang berbeda  
✅ Korelasi tinggi dengan human judgment  

### Perbandingan dengan SPICE

| Aspek | METEOR | SPICE |
|-------|--------|-------|
| **Fokus** | Lexical similarity + word order | Semantic similarity |
| **Kompleksitas** | Sedang | Tinggi (butuh parser) |
| **Kecepatan** | Cepat | Lambat |
| **Bahasa** | Universal | Butuh parser per bahasa |
| **Sinonim** | ✅ Ya | ❌ Tidak langsung |
| **Word Order** | ✅ Ya (dengan penalty) | ❌ Tidak |

---

## 🔍 Troubleshooting

### Error: "NLTK data not found"

**Solusi:**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

### Error: "Image IDs tidak cocok"

**Penyebab:** Image IDs di predictions dan ground truth tidak sama

**Solusi:**
1. Pastikan image_id konsisten di kedua file
2. Periksa format JSON dengan `fix_json_format.py`

### Score terlalu rendah (<0.3)

**Kemungkinan penyebab:**
1. Caption terlalu berbeda dari ground truth
2. Banyak kata yang tidak match
3. Word order sangat berbeda

**Solusi:**
1. Periksa sample predictions vs ground truth
2. Pastikan preprocessing konsisten
3. Cek apakah model menghasilkan caption yang relevan

### Score selalu 1.0

**Penyebab:** Caption candidate sama persis dengan salah satu reference

**Ini normal!** Artinya model Anda menghasilkan caption yang sempurna.

---

## 📝 Contoh Workflow Lengkap

```bash
# 1. Install dependencies
pip install nltk

# 2. Generate predictions (jika belum)
cd ..
python test/testMain.py

# 3. Kembali ke folder test
cd test

# 4. Jalankan evaluasi METEOR
python evaluate_meteor.py

# 5. Lihat hasil
cat meteor_results_testing.json
```

---

## 📚 Referensi

- **METEOR Paper**: Banerjee & Lavie (2005) - "METEOR: An Automatic Metric for MT Evaluation with Improved Correlation with Human Judgments"
- **NLTK METEOR**: https://www.nltk.org/api/nltk.translate.meteor_score.html
- **Original METEOR**: https://www.cs.cmu.edu/~alavie/METEOR/

---

## 🤝 Kontribusi

Jika menemukan bug atau punya saran, silakan buat issue atau pull request!

---

**Dibuat untuk:** Evaluasi Skripsi - Image Captioning untuk Bahasa Indonesia  
**Terakhir diupdate:** 2025-12-03
