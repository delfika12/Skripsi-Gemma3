# Assistive Vision System for Visually Impaired

An AI-based visual assistance system for the visually impaired using Gemma3 (Vision-Language Model) and Piper TTS on Jetson Nano.

## 📋 Description

This project is a system that can:
- Capture images from a camera
- Generate image descriptions in Indonesian using Gemma3 (Ollama)
- Convert descriptions to audio using Piper TTS
- Play audio to provide information to users
- Activated by a physical button on Jetson Nano

## 🏗️ System Architecture

```
┌─────────────┐
│   Camera    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ captureImage.py │ ──► captures/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ generateText.py │ ──► Ollama (Gemma3)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ generateTTS.py  │ ──► Piper TTS ──► audios/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  playAudio.py   │ ──► Speaker
└─────────────────┘
```

## 📁 Project Structure

```
.
├── captureImage.py          # Module for capturing images from camera
├── generateText.py          # Module for generating descriptions with Ollama
├── generateTTS.py           # Module for text-to-speech with Piper
├── playAudio.py             # Module for playing audio
├── main.py                  # Main pipeline with button trigger
├── findwebcamindex.py       # Utility to find camera index
├── id_ID-news_tts-medium.onnx  # Piper TTS Indonesian model
├── id_ID-news_tts-medium.onnx.json
├── captures/                # Folder for storing images
├── outputs/                 # Folder for storing text descriptions
├── audios/                  # Folder for storing audio files
└── test/
    ├── testMain.py          # Script for batch testing
    ├── GroundTruth.json     # Ground truth for evaluation
    ├── images-test/         # Folder for test images
    ├── resultAudio/         # Audio results from testing
    ├── resultText.json      # Description results from testing
    └── resultTime.csv       # Inference time from testing
```

## 🔧 Jetson Nano Setup

### 1. Hardware Preparation

**Required Components:**
- Jetson Nano Developer Kit
- USB Camera or CSI Camera
- Speaker/Headphone
- Push Button
- Jumper wires
- 5V 4A Power supply (recommended)

**Hardware Connections:**
- **Camera**: Connect to USB port or CSI
- **Speaker**: Connect to 3.5mm audio port or USB
- **Button**: 
  - Pin 1 → GPIO Pin 37 (BOARD mode)
  - Pin 2 → GND (e.g., Pin 39)

### 2. Jetson Nano Setup

#### a. Flash JetPack
```bash
# Download JetPack from NVIDIA Developer
# Flash to SD Card using Etcher or balenaEtcher
# Boot Jetson Nano and complete initial setup
```

#### b. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

#### c. Install Dependencies

**Python and pip:**
```bash
sudo apt install -y python3-pip python3-dev
pip3 install --upgrade pip
```

**OpenCV:**
```bash
sudo apt install -y python3-opencv
# Or compile from source for optimal performance
```

**Audio Tools:**
```bash
sudo apt install -y alsa-utils portaudio19-dev
```

**GPIO Library:**
```bash
sudo pip3 install Jetson.GPIO
sudo groupadd -f -r gpio
sudo usermod -a -G gpio $USER
```

### 3. Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Pull Gemma3 model (or your custom model)
ollama pull gemma3

# For custom model, copy Modelfile and run:
# ollama create customGemma3 -f Modelfile
```

**Run Ollama as a service:**
```bash
# Create systemd service
sudo nano /etc/systemd/system/ollama.service
```

Add the following content:
```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=your-username
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

### 4. Install Piper TTS

```bash
# Install dependencies
sudo apt install -y libopenblas-dev

# Install Piper Python package
pip3 install piper-tts

# Or install from source for Jetson:
git clone https://github.com/rhasspy/piper.git
cd piper/src/python
pip3 install -e .
```

**Download Indonesian Model:**
The `id_ID-news_tts-medium.onnx` model is already included in the repository.

### 5. Install Python Dependencies

```bash
# Clone repository
git clone https://github.com/delfika12/Skripsi-Gemma3.git
cd Skripsi-Gemma3

# Install requirements
pip3 install -r requirements.txt
```

**`requirements.txt` file:**
```
opencv-python
requests
piper-tts
Jetson.GPIO
```

### 6. Audio Configuration

**Test speaker:**
```bash
# List audio devices
aplay -l

# Test audio
speaker-test -t wav -c 2
```

**Set default audio output:**
```bash
# Edit ALSA config
sudo nano /etc/asound.conf
```

Add:
```
defaults.pcm.card 1
defaults.ctl.card 1
```

Or adjust `DEFAULT_DEVICE` in `playAudio.py`.

### 7. Camera Configuration

**Check available cameras:**
```bash
python3 findwebcamindex.py
```

Adjust camera index in `captureImage.py` if needed (default: 0).

## 🚀 How to Run

### Normal Mode (with Button)

```bash
# Make sure Ollama is running
sudo systemctl status ollama

# Run main pipeline
python3 main.py
```

Press the physical button to trigger the pipeline.

### Individual Testing Mode

**1. Test Image Capture:**
```bash
python3 captureImage.py
```

**2. Test Text Generation:**
```bash
python3 generateText.py
```

**3. Test TTS Generation:**
```bash
python3 generateTTS.py
```

**4. Test Audio Playback:**
```bash
python3 playAudio.py
```

### Batch Testing Mode

```bash
cd test
python3 testMain.py
```

This script will:
- Process all images in `images-test/`
- Generate descriptions and audio for each image
- Save results to `resultText.json`, `resultTime.csv`, and `resultAudio/`

## ⚙️ Configuration

### generateText.py
```python
MODEL_NAME = "customGemma3"  # Ollama model name
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
```

### generateTTS.py
```python
MODEL_PATH = "id_ID-news_tts-medium.onnx"
```

### main.py
```python
BUTTON_PIN = 37  # GPIO pin for button (BOARD mode)
DEBOUNCE_SEC = 0.15  # Debounce time
```

### playAudio.py
```python
DEFAULT_DEVICE = "default"  # ALSA device for audio
```

## 🧪 Testing & Evaluation

### Running Batch Test

```bash
cd test
python3 testMain.py
```

### Test Results

- **resultText.json**: Generated descriptions for each image
- **resultTime.csv**: Ollama and Piper inference times
- **resultAudio/**: TTS audio output files

### Ground Truth Format

```json
{
  "annotations": [
    {
      "image_id": 1,
      "captions": [
        "Image description 1",
        "Alternative description 1",
        "Alternative description 2"
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Ollama cannot be accessed
```bash
# Check service status
sudo systemctl status ollama

# Restart service
sudo systemctl restart ollama

# Check logs
journalctl -u ollama -f
```

### Camera not detected
```bash
# Check video devices
ls /dev/video*

# Test with v4l2
v4l2-ctl --list-devices

# Run helper script
python3 findwebcamindex.py
```

### No audio output
```bash
# Check ALSA devices
aplay -l

# Test speaker
speaker-test -t wav -c 2

# Adjust volume
alsamixer
```

### GPIO Permission Denied
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Logout and login again
```

### Out of Memory
```bash
# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 📊 Performance Tips

1. **Use smaller Ollama models** for faster inference
2. **Set CUDA** if using Jetson GPU:
   ```bash
   export CUDA_VISIBLE_DEVICES=0
   ```
3. **Optimize Piper** with smaller models if needed
4. **Use swap** to avoid OOM
5. **Set power mode** to MAX:
   ```bash
   sudo nvpmodel -m 0
   sudo jetson_clocks
   ```

## 🤝 Contributing

Please create issues or pull requests for improvements and new features.

## 📝 License

[Adjust according to your project license]

## 👤 Author

Delfika - Brawijaya University

## 🙏 Acknowledgments

- Ollama for LLM framework
- Piper TTS for Indonesian TTS
- NVIDIA for Jetson platform
