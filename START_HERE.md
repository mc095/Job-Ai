# 🎤 VOICE INTERVIEW SETUP - START HERE

## ⚡ Quick Setup (Recommended)

**Just run this file:**
```bash
FINAL_SETUP.bat
```

It will:
1. ✅ Install all Python packages automatically
2. ✅ Download Moonshine from GitHub
3. ✅ Open espeak-ng download page for you
4. ✅ Verify installation

---

## 📋 Manual Setup (If batch file doesn't work)

Copy-paste commands from: **`COPY_PASTE_COMMANDS.txt`**

Or follow these steps:

### 1. Activate Virtual Environment
```bash
venv\Scripts\activate
```

### 2. Update pip
```bash
python -m pip install --upgrade pip
```

### 3. Remove Old Packages
```bash
pip uninstall -y moonshine moonshine-speech tensorflow keras
```

### 4. Install Kokoro TTS
```bash
pip install kokoro>=0.9.4 soundfile numpy
```

### 5. Install PyTorch
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 6. Install Moonshine from GitHub (CRITICAL!)
```bash
pip install git+https://github.com/moonshine-ai/moonshine.git#subdirectory=moonshine-onnx
```

**Note**: This command downloads from GitHub and may take 1-2 minutes. It's the CORRECT way to install Moonshine!

### 7. Install espeak-ng
1. Go to: https://github.com/espeak-ng/espeak-ng/releases
2. Download: `espeak-ng-X64.msi` (for 64-bit Windows)
3. Run the installer
4. **Restart your terminal**

### 8. Test Installation
```bash
python test_kokoro.py
```

If all tests pass, you're ready! 🎉

### 9. Start Django
```bash
python manage.py runserver
```

### 10. Open Browser
```
http://127.0.0.1:8000/interview/voice/
```

---

## ❌ Why You Got the Error

You tried:
```bash
pip install useful-moonshine-onnx  # ❌ NOT on PyPI!
```

The correct command is:
```bash
pip install git+https://github.com/moonshine-ai/moonshine.git#subdirectory=moonshine-onnx
```

**Why?** Because `useful-moonshine-onnx` is **NOT published to PyPI**. It only exists as a subdirectory in the GitHub repository, so you MUST install it directly from GitHub.

---

## 📦 What Gets Installed

| Package | Purpose | Install Method |
|---------|---------|----------------|
| **kokoro** | Text-to-Speech | PyPI: `pip install kokoro>=0.9.4` |
| **soundfile** | Audio I/O | PyPI: `pip install soundfile` |
| **numpy** | Array processing | PyPI: `pip install numpy` |
| **torch** | Neural networks | PyPI with special URL |
| **moonshine_onnx** | Speech-to-Text | **GitHub only!** |
| **espeak-ng** | Text phonetics | Manual installer (.msi) |

---

## 🔧 Troubleshooting

### "Git not installed" error
Install Git for Windows: https://git-scm.com/download/win

### "espeak-ng not found" error
1. Download installer from: https://github.com/espeak-ng/espeak-ng/releases
2. Run the .msi file
3. **Restart terminal** (important!)

### "No module named 'tensorflow'" error
This means you installed the WRONG moonshine package. Run:
```bash
pip uninstall moonshine moonshine-speech tensorflow
pip install git+https://github.com/moonshine-ai/moonshine.git#subdirectory=moonshine-onnx
```

### "Question generation failed" error
Check your `GEMINI_API_KEY` in the `.env` file.

---

## ✅ Verification Checklist

After running setup, verify:

- [ ] Run `python test_kokoro.py` → All tests pass
- [ ] Run `espeak-ng --version` → Shows version number
- [ ] Run `pip show moonshine-onnx` → Shows package info
- [ ] Run `pip show kokoro` → Shows version 0.9.4+
- [ ] Django starts: `python manage.py runserver`
- [ ] Page loads: http://127.0.0.1:8000/interview/voice/

---

## 🎯 What Each File Does

| File | Purpose |
|------|---------|
| **`FINAL_SETUP.bat`** | 🔥 **RUN THIS!** Automated setup |
| **`COPY_PASTE_COMMANDS.txt`** | Manual commands if batch fails |
| **`test_kokoro.py`** | Test if installation worked |
| **`MISSING_DEPENDENCIES.md`** | Detailed error explanations |
| **`START_HERE.md`** | This file - overview |

---

## 🚀 Ready to Go!

Once `test_kokoro.py` passes:

1. **Start server**: `python manage.py runserver`
2. **Open browser**: http://127.0.0.1:8000/interview/voice/
3. **Fill in job role**
4. **Click "Start Voice Interview"**
5. **Speak naturally** - the AI will interview you! 🎤✨

---

## 💡 Pro Tips

- Use a **quiet environment** (though noise reduction helps)
- Speak **clearly at moderate pace**
- Take **30-90 seconds** per answer
- System works with **background noise** too!

---

## 📞 Still Having Issues?

1. Check you're in the project root: `E:\Agentic-Job-AI`
2. Virtual environment activated: `(venv)` in prompt
3. Run: `pip list | findstr "moonshine kokoro"`
4. Run: `espeak-ng --version`
5. Share the exact error message

---

**That's it! Run `FINAL_SETUP.bat` and you're good to go! 🎉**
