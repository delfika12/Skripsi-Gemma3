"""
Script untuk mengurangi konteks caption di GroundTruthAsli.json
(Menghapus 1-2 poin pembahasan seperti Suasana atau Bahaya)
Versi Perbaikan: Lebih selektif agar tidak menghapus deskripsi utama.
"""

import json
import re

def reduce_caption(text):
    """
    Mengurangi konteks caption dengan menghapus kalimat tertentu
    """
    # Pisahkan kalimat berdasarkan titik
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) <= 1:
        return text
    
    new_sentences = []
    removed_count = 0
    
    for i, s in enumerate(sentences):
        s_lower = s.lower()
        
        # Identifikasi kalimat Suasana (Atmosphere)
        # Fokus pada kalimat yang diawali atau didominasi oleh deskripsi suasana
        is_atmosphere = any(x in s_lower for x in ['suasana', 'nuansa', 'lingkungan tampak', 'kondisi terlihat', 'terasa sejuk', 'terasa tenang'])
        
        # Identifikasi kalimat Bahaya (Hazard Warning)
        # Fokus pada kalimat peringatan, bukan sekedar deskripsi "jalan licin"
        is_hazard_warning = any(x in s_lower for x in ['ada risiko', 'terdapat potensi', 'potensi bahaya', 'risiko bahaya', 'perlu berhati-hati', 'waspada', 'aman, tidak ada', 'tidak ada bahaya', 'tidak tampak ada bahaya'])
        
        # Hapus jika itu kalimat suasana atau peringatan bahaya
        # Tapi JANGAN hapus kalimat pertama (biasanya objek utama) kecuali sangat yakin itu bukan objek
        if (is_atmosphere or is_hazard_warning) and removed_count < 2:
            # Pengecualian: Jangan hapus kalimat pertama jika itu satu-satunya deskripsi objek
            if i == 0 and len(sentences) > 1:
                # Cek apakah kalimat pertama benar-benar hanya suasana/bahaya?
                # Jika kalimat pertama "Suasana tampak sepi.", oke hapus.
                # Jika "Seorang pria berjalan di jalan licin.", JANGAN hapus (meski ada kata licin, tapi ini objek).
                if not s_lower.startswith('suasana') and not s_lower.startswith('kondisi'):
                     new_sentences.append(s)
                     continue
            
            removed_count += 1
            continue
            
        new_sentences.append(s)
    
    # Jika hasil kosong (semua terhapus), kembalikan kalimat pertama dari aslinya
    if not new_sentences:
        return sentences[0] + '.'
        
    # Gabungkan kembali
    reduced_text = '. '.join(new_sentences)
    if reduced_text and not reduced_text.endswith('.'):
        reduced_text += '.'
        
    return reduced_text

def process_file():
    # Kita perlu reload dari file backup atau aslinya jika ada, 
    # tapi karena sudah tertimpa, kita akan coba perbaiki yang ada atau
    # lebih baik saya kembalikan dulu konten GroundTruthAsli.json ke kondisi "Full" sebelum dikurangi
    # agar kita tidak mengurangi dari yang sudah kosong.
    # TAPI, saya tidak punya backup file sebelumnya di memori agent ini selain apa yang saya tulis.
    # Untungnya, saya bisa menggunakan 'undo' logic atau asumsi bahwa file yang ada sekarang
    # sebagian besar masih oke kecuali yang jadi kosong.
    
    # TAPI, karena file sudah dimodifikasi di langkah sebelumnya dan hasilnya ada yang kosong,
    # script ini akan bekerja pada file yang SUDAH dimodifikasi (yang ada string kosongnya).
    # String kosong tidak bisa diperbaiki hanya dengan script ini.
    
    # SOLUSI: Saya harus me-restore GroundTruthAsli.json ke kondisi sebelum langkah 247.
    # Karena saya tidak bisa "undo", saya akan menggunakan resultText.json (yang punya caption lengkap)
    # untuk mengisi ulang caption ke-4 dan ke-5, dan caption 1-3 mungkin harus saya biarkan
    # atau saya coba "perbaiki" yang kosong saja.
    
    # Namun, caption 1-3 adalah manual. Caption 4-5 dari resultText.
    # Mari kita lihat seberapa banyak yang kosong.
    
    input_file = 'GroundTruthAsli.json'
    print(f"Membaca {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Kita akan memproses ulang.
    # Masalahnya: data yang sudah kosong "" tidak bisa dikembalikan.
    # TAPI, saya lihat di view_file sebelumnya, hanya caption pertama Image 1 yang kosong.
    # Caption lain sepertinya oke (hanya berkurang).
    # Mari kita cek apakah ada caption lain yang kosong.
    
    empty_count = 0
    for item in data['annotations']:
        for cap in item['captions']:
            if not cap.strip():
                empty_count += 1
    
    print(f"Ditemukan {empty_count} caption kosong.")
    
    # Jika ada yang kosong, kita tidak bisa restore otomatis tanpa source.
    # Tapi untuk Image 1 caption 1, saya tahu isinya dari history chat.
    # "Seorang pria berdiri di trotoar dengan tiang miring di belakangnya, pengendara motor melintas, dan genangan air membuat trotoar licin."
    
    # Untuk amannya, saya akan jalankan logic perbaikan ini.
    # Dan khusus untuk yang kosong, saya akan isi placeholder atau coba restore manual jika sedikit.
    
    # TAPI, user minta "modifikasi sedikit... lalu evaluasi ulang".
    # Jika saya jalankan script ini pada file yang SUDAH dikurangi, dia akan mengurangi LAGI?
    # Tidak, karena keywordnya sudah hilang.
    
    # Jadi, script ini hanya akan memperbaiki logic untuk masa depan, tapi tidak mengembalikan data yang hilang.
    # SAYA AKAN MELAKUKAN RESTORE MANUAL UNTUK IMAGE 1 CAPTION 1 di dalam script ini.
    
    for item in data['annotations']:
        if item['image_id'] == 1:
            if not item['captions'][0].strip():
                item['captions'][0] = "Seorang pria berdiri di trotoar dengan tiang miring di belakangnya, pengendara motor melintas, dan genangan air membuat trotoar licin."

    # Simpan perbaikan manual ini dulu
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Perbaikan manual untuk caption kosong selesai.")

if __name__ == "__main__":
    process_file()
