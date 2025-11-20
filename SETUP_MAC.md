# macOS Setup & Troubleshooting Guide (Apple Silicon)

This project relies on `pyannote.audio` and `torch`, which can have compatibility issues with the latest Python versions and macOS architecture (M1/M2/M3).

Follow this specific guide to ensure a stable environment.

## 🛑 Prerequisites

Do not skip these steps. The default Python version on Mac (usually 3.13 or 3.9) might cause issues. We explicitly need **Python 3.10**.

### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install System Dependencies
We need ffmpeg for audio processing and python@3.10 for stability.

```bash
brew update
brew install ffmpeg
brew install python@3.10
```

## 🛠️ Installation Steps

### 1. Clone and Navigate

```bash
git clone https://github.com/your-username/ai-podcast-producer.git
cd ai-podcast-producer
```

### 2. Create the Virtual Environment (Python 3.10)

It is crucial to use the specific 3.10 binary we just installed.

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

We use specific versions to avoid conflicts with torchcodec and numpy 2.0.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a .env file in the root directory:

```bash
touch .env
```

Add your Hugging Face token inside:

```ini
HF_TOKEN=hf_your_token_starts_with_hf...
```

## 🐛 Common Troubleshooting

### Error: Library not loaded: @rpath/libavutil.59.dylib

This means PyTorch cannot find the FFmpeg libraries installed by Homebrew.

**Solution**: Reinstall FFmpeg to refresh the links.

```bash
brew uninstall ffmpeg
brew install ffmpeg
```

### Error: AttributeError: np.NaN was removed in the NumPy 2.0 release

This happens if numpy auto-updates to version 2.x.

**Solution**: Downgrade NumPy.

```bash
pip install "numpy<2.0"
```

### Warning Flood: UserWarning: torchaudio._backend...

If you see hundreds of warnings but the script is running, ignore them. The script includes a filter to silence these, but they might appear during the loading phase. They are harmless deprecation warnings caused by using the stable 3.1.1 version of pyannote on Mac.

### Archivo 2: Actualización del `requirements.txt`

Para que el paso 3 del manual de arriba funcione perfecto, debes actualizar tu `requirements.txt` con las versiones exactas que logramos estabilizar.

Actualiza tu archivo `requirements.txt` con esto:

```text
# Core AI & Audio (Versions pinned for Mac Silicon stability)
pyannote.audio==3.1.1
torch
torchaudio
huggingface_hub<0.25.0
numpy<2.0

# Media Processing
pydub
moviepy<2.0
imageio-ffmpeg

# Utilities
python-dotenv
```