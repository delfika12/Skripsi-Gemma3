"""
Script untuk mengisi caption kosong di GroundTruthAsli.json
dengan menyalin caption lain dari gambar yang sama.
"""

import json

def fix_all_empty():
    input_file = 'GroundTruthAsli.json'
    print(f"Membaca {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed_count = 0
    for item in data['annotations']:
        # Kumpulkan caption yang TIDAK kosong
        valid_captions = [c for c in item['captions'] if c.strip()]
        
        if not valid_captions:
            print(f"Warning: Image {item['image_id']} tidak punya caption valid sama sekali!")
            continue
            
        new_captions = []
        for cap in item['captions']:
            if not cap.strip():
                # Jika kosong, ambil caption valid pertama sebagai pengganti
                # (atau random, tapi pertama cukup konsisten)
                replacement = valid_captions[0]
                new_captions.append(replacement)
                fixed_count += 1
            else:
                new_captions.append(cap)
        
        item['captions'] = new_captions

    print(f"Selesai. {fixed_count} caption kosong telah diisi ulang.")
    
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("File berhasil disimpan.")

if __name__ == "__main__":
    fix_all_empty()
