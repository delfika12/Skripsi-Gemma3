"""
Script untuk membersihkan simbol-simbol tidak natural dari caption
di GroundTruthAsli.json (tanda kutip, backslash, dll)
"""

import json
import re

def clean_text(text):
    """
    Membersihkan simbol aneh dari teks
    """
    cleaned = text
    
    # 1. Hapus tanda kutip ganda di dalam teks (escaped quote \")
    # Karena json.load sudah handle escape, kita cari karakter " itu sendiri
    # Tapi di dalam string JSON, " biasanya tidak ada kecuali escaped.
    # Kita akan replace " dengan string kosong atau spasi jika itu mengapit kata
    
    # Hapus tanda kutip (misal: "EXIT" -> EXIT)
    cleaned = cleaned.replace('"', '')
    
    # 2. Hapus backslash
    cleaned = cleaned.replace('\\', '')
    
    # 3. Hapus tanda bintang (markdown bold/italic)
    cleaned = cleaned.replace('*', '')
    
    # 4. Hapus tanda kurung siku atau kurawal jika ada (sisa format)
    cleaned = cleaned.replace('[', '').replace(']', '')
    cleaned = cleaned.replace('{', '').replace('}', '')
    
    # 5. Rapikan spasi yang mungkin ganda akibat penghapusan
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def process_file():
    input_file = 'GroundTruthAsli.json'
    
    print(f"Membaca {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count_modified = 0
    for item in data['annotations']:
        new_captions = []
        modified_in_image = False
        
        for cap in item['captions']:
            cleaned_cap = clean_text(cap)
            new_captions.append(cleaned_cap)
            
            if cleaned_cap != cap:
                modified_in_image = True
                # Print contoh perubahan
                # print(f"Before: {cap}")
                # print(f"After : {cleaned_cap}")
        
        item['captions'] = new_captions
        if modified_in_image:
            count_modified += 1
            
    print(f"Selesai. {count_modified} gambar mengalami pembersihan caption.")
    
    # Simpan kembali
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("File berhasil disimpan.")

if __name__ == "__main__":
    process_file()
