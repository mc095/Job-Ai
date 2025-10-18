# Kokoro TTS Installation Guide

## Prerequisites
- Python 3.9+ (you have 3.12.1 ✅)
- pip

## Step 1: Install Python Packages

Open your terminal in the project directory and run:

```bash
# Activate your virtual environment first
venv\Scripts\activate

# Install Kokoro and dependencies
pip install kokoro>=0.9.4 soundfile
```

## Step 2: Install espeak-ng (Required for Kokoro)

### For Windows:

1. Go to [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases)
2. Click on **Latest release**
3. Download the appropriate `.msi` file for your system:
   - For 64-bit Windows: `espeak-ng-X64.msi` (most common)
   - For 32-bit Windows: `espeak-ng-X86.msi`
4. Run the downloaded `.msi` installer
5. Follow the installation wizard (use default settings)
6. **Important**: Add espeak-ng to your system PATH if not done automatically

### Verify espeak-ng Installation:

Open a new terminal and run:
```bash
espeak-ng --version
```

If you see version information, espeak-ng is installed correctly!

## Step 3: Install Moonshine STT (Optional - for voice interviews)

```bash
pip install moonshine-speech
```

## Step 4: Test Installation

Create a test file `test_kokoro.py`:

```python
from kokoro import KPipeline
import soundfile as sf

# Initialize pipeline
pipeline = KPipeline(lang_code='a')  # 'a' = American English

# Generate speech
text = "Hello! This is a test of Kokoro TTS."
generator = pipeline(text, voice='af_heart', speed=1.0)

# Save audio
audio_chunks = []
for _, _, audio in generator:
    audio_chunks.append(audio)

import numpy as np
combined_audio = np.concatenate(audio_chunks)
sf.write('test_output.wav', combined_audio, 24000)

print("✅ Kokoro TTS is working! Check test_output.wav")
```

Run the test:
```bash
python test_kokoro.py
```

## Available Voices

Kokoro supports multiple voices. Try different ones:
- `af_heart` - Female, warm
- `af_sarah` - Female, professional
- `am_adam` - Male, deep
- `am_michael` - Male, casual

## Troubleshooting

### Error: "No module named 'kokoro'"
- Make sure you activated your virtual environment
- Run `pip install kokoro>=0.9.4` again

### Error: "espeak-ng not found"
- Reinstall espeak-ng from the link above
- Make sure to restart your terminal after installation
- Check if espeak-ng is in your PATH

### Error: "RuntimeError: Failed to initialize TTS"
- Verify espeak-ng installation: `espeak-ng --version`
- Check if you have enough disk space (~200MB for Kokoro models)
- Try reinstalling: `pip uninstall kokoro && pip install kokoro>=0.9.4`

### For GPU Acceleration (Optional)
If you have CUDA-compatible GPU:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Next Steps

Once Kokoro is installed, restart your Django server:
```bash
python manage.py runserver
```

Then navigate to: `http://127.0.0.1:8000/interview/voice/`

## Resources
- [Kokoro GitHub](https://github.com/hexgrad/kokoro)
- [Kokoro PyPI](https://pypi.org/project/kokoro/)
- [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases)
