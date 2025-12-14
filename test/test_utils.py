import os
import glob
import re
import time
import threading

try:
    from jtop import jtop
    JTOP_AVAILABLE = True
except ImportError:
    JTOP_AVAILABLE = False
    print("[WARNING] 'jtop' module not found. Resource monitoring will be disabled.")

class ResourceMonitor(threading.Thread):
    def __init__(self, interval=0.5):
        super().__init__()
        self.interval = interval
        self.running = False
        self.stats_list = []
        self.start_time = 0

    def run(self):
        if not JTOP_AVAILABLE:
            return
        
        self.running = True
        self.start_time = time.time()
        try:
            with jtop(interval=self.interval) as jetson:
                while self.running and jetson.ok():
                    try:
                        current_time = time.time()
                        # CPU Clock (Avg of all cores) - kHz
                        cpu_freqs = [c['freq']['cur'] for c in jetson.cpu['cpu']]
                        avg_cpu_freq = sum(cpu_freqs) / len(cpu_freqs) if cpu_freqs else 0
                        
                        # CPU Util (Avg of all cores) - %
                        cpu_utils = [val for key, val in jetson.stats.items() if key.startswith('CPU') and key[3:].isdigit()]
                        avg_cpu_util = sum(cpu_utils) / len(cpu_utils) if cpu_utils else 0
                        
                        # RAM (MB)
                        ram_used = jetson.memory['RAM']['used'] / 1024
                        
                        # GPU Util - %
                        gpu_util = jetson.stats.get('GPU', 0)
                        
                        # VRAM (Shared RAM in MB)
                        vram_used = jetson.memory['RAM'].get('shared', 0) / 1024
                        
                        # Power (mW)
                        power = jetson.stats.get('Power TOT', 0)
                        
                        self.stats_list.append({
                            'timestamp': current_time,
                            'relative_time': current_time - self.start_time,
                            'cpu_clock': avg_cpu_freq,
                            'cpu_util': avg_cpu_util,
                            'ram_usage': ram_used,
                            'gpu_util': gpu_util,
                            'vram_gpu': vram_used,
                            'power': power
                        })
                    except Exception:
                        pass
                    time.sleep(self.interval)
        except Exception as e:
            print(f"[ERROR] Monitor: {e}")

    def stop(self):
        self.running = False
        self.join()

    def get_averages(self):
        if not self.stats_list:
            return {
                'cpu_clock': 0, 'cpu_util': 0, 'ram_usage': 0,
                'gpu_util': 0, 'vram_gpu': 0, 'power': 0
            }
        
        keys = ['cpu_clock', 'cpu_util', 'ram_usage', 'gpu_util', 'vram_gpu', 'power']
        avgs = {}
        for k in keys:
            avgs[k] = sum(s[k] for s in self.stats_list) / len(self.stats_list)
        return avgs

    def get_stats(self):
        return self.stats_list

def get_image_files(directory):
    """
    Ambil semua file gambar dari directory.
    Return: list of image paths sorted by numeric value in filename
    """
    extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    # Sort berdasarkan angka dalam nama file
    def extract_number(filepath):
        filename = os.path.basename(filepath)
        numbers = re.findall(r'\d+', filename)
        return int(numbers[0]) if numbers else 0
    
    return sorted(image_files, key=extract_number)

def extract_image_id(image_path):
    """
    Ekstrak image_id dari nama file.
    Contoh: '1.png' -> 1, 'image_5.jpg' -> 5
    """
    filename = os.path.basename(image_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Coba ekstrak angka dari nama file
    numbers = re.findall(r'\d+', name_without_ext)
    if numbers:
        return int(numbers[0])
    else:
        # Jika tidak ada angka, gunakan hash dari nama file
        return hash(name_without_ext) % 10000
