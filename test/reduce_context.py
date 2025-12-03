"""
Script untuk mengurangi konteks caption di GroundTruthAsli.json
(Menghapus 1-2 poin pembahasan seperti Suasana atau Bahaya)
"""

import json
import re

def reduce_caption(text):
    """
    Mengurangi konteks caption dengan menghapus kalimat tertentu
    """
    # Pisahkan kalimat berdasarkan titik
    # Split by '. ' but keep the delimiter to reconstruct later if needed, 
    # or just split and rejoin.
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) <= 1:
        return text
    
    new_sentences = []
    removed_count = 0
    
    for s in sentences:
        # Cek apakah kalimat ini membahas Suasana atau Bahaya
        is_atmosphere = any(x in s.lower() for x in ['suasana', 'nuansa', 'lingkungan tampak', 'kondisi terlihat'])
        is_hazard = any(x in s.lower() for x in ['bahaya', 'risiko', 'potensi', 'hati-hati', 'waspada', 'aman', 'tergelincir', 'licin'])
        
        # Hapus jika itu kalimat suasana atau bahaya (maksimal hapus 2 kalimat per caption)
        if (is_atmosphere or is_hazard) and removed_count < 2:
            removed_count += 1
            continue
            
        new_sentences.append(s)
    
    # Jika tidak ada yang dihapus (karena tidak match keyword), hapus kalimat terakhir jika kalimatnya banyak
    if removed_count == 0 and len(sentences) > 2:
        new_sentences = new_sentences[:-1]
    
    # Gabungkan kembali
    reduced_text = '. '.join(new_sentences)
    if reduced_text and not reduced_text.endswith('.'):
        reduced_text += '.'
        
    return reduced_text

def process_file():
    input_file = 'GroundTruthAsli.json'
    
    print(f"Membaca {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count_modified = 0
    for item in data['annotations']:
        new_captions = []
        for cap in item['captions']:
            reduced_cap = reduce_caption(cap)
            new_captions.append(reduced_cap)
            
        item['captions'] = new_captions
        count_modified += 1
            
    print(f"Selesai. {count_modified} gambar diproses.")
    
    # Simpan kembali
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("File berhasil disimpan.")

if __name__ == "__main__":
    process_file()
