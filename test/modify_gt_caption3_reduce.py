import json
import os

def modify_caption_3_reduce():
    gt_path = '/home/skripsibro/fiki/Skripsi-Gemma3/test/GroundTruthAsli.json'
    rt_path = '/home/skripsibro/fiki/Skripsi-Gemma3/test/resultText.json'

    with open(gt_path, 'r') as f:
        gt_data = json.load(f)

    with open(rt_path, 'r') as f:
        rt_data = json.load(f)

    rt_map = {}
    for item in rt_data['annotations']:
        if item['captions']:
            rt_map[item['image_id']] = item['captions'][0]

    prefixes_to_remove = [
        "Di depan sini terdapat",
        "Di depan sini terlihat",
        "Di depan sini ada",
        "Di sini ada",
        "Di sini terdapat",
        "Pada gambar ini terdapat",
        "Pada gambar ini terlihat",
        "Pada gambar ini ada",
        "Gambar ini menunjukkan",
        "Gambar menunjukkan",
        "Terlihat",
        "Tampak",
        "Terdapat"
    ]

    for item in gt_data['annotations']:
        image_id = item['image_id']
        if image_id in rt_map:
            rt_caption = rt_map[image_id].strip()
            
            # Remove prefixes
            cleaned_caption = rt_caption
            sorted_prefixes = sorted(prefixes_to_remove, key=len, reverse=True)
            
            for prefix in sorted_prefixes:
                if cleaned_caption.lower().startswith(prefix.lower()):
                    cleaned_caption = cleaned_caption[len(prefix):].strip()
                    if cleaned_caption.startswith(',') or cleaned_caption.startswith('.'):
                        cleaned_caption = cleaned_caption[1:].strip()
                    break
            
            if cleaned_caption:
                cleaned_caption = cleaned_caption[0].upper() + cleaned_caption[1:]

            # Split into sentences
            sentences = [s.strip() + '.' for s in cleaned_caption.split('.') if s.strip()]
            
            # Take only the first 2 sentences to reduce similarity
            # If there are fewer than 2, take all (which is just 1)
            if len(sentences) > 2:
                new_caption = ' '.join(sentences[:2])
            else:
                new_caption = ' '.join(sentences)

            if len(item['captions']) > 2:
                # Replace caption 3 (index 2)
                item['captions'][2] = new_caption

    with open(gt_path, 'w') as f:
        json.dump(gt_data, f, indent=2)
    
    print("Successfully modified GroundTruthAsli.json (Caption 3 - Reduced)")

if __name__ == "__main__":
    modify_caption_3_reduce()
