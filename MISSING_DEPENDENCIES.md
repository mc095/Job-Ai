# Missing Dependencies Report

## 🔴 Critical Issues Found

Based on your error logs, here are ALL the missing dependencies:

---

## 1. ❌ Kokoro TTS - INSTALLED BUT NEEDS espeak-ng

**Status**: Package installed, but missing system dependency

**Error**: `espeak-ng not found`

**Fix**:
```bash
# Install espeak-ng on Windows:
# 1. Download from: https://github.com/espeak-ng/espeak-ng/releases
# 2. Get: espeak-ng-X64.msi (for 64-bit) or espeak-ng-X86.msi (for 32-bit)
# 3. Run the installer
# 4. Restart terminal
```

---

## 2. ❌ Moonshine STT - WRONG PACKAGE INSTALLED

**Status**: Not installed OR using wrong package

**Error**: `No module named 'tensorflow'` (caused by old moonshine package)

**Issue**: You may have installed `moonshine-speech` which requires TensorFlow (deprecated)

**Fix**:
```bash
# IMPORTANT: Uninstall old moonshine packages first
pip uninstall moonshine moonshine-speech useful-moonshine -y

# Install the correct ONNX version (NO TensorFlow needed!)
pip install useful-moonshine-onnx
```

---

## 3. ❌ TensorFlow - NOT ACTUALLY NEEDED

**Status**: NOT REQUIRED (false dependency from wrong moonshine package)

**Error**: `No module named 'tensorflow'`

**Why it appeared**: Old `moonshine` or `moonshine-speech` packages depend on TensorFlow

**Fix**: Don't install TensorFlow! Just use the correct moonshine package above

---

## 4. ⚠️ Question Generation Issue

**Error**: `Question generation failed: 'NoneType' object has no attribute 'strip'`

**Cause**: API response is None (possibly API key or rate limit issue)

**Check**:
- Verify `GEMINI_API_KEY` in your `.env` file
- Check if you hit Gemini API rate limits
- Ensure API key has proper permissions

---

## 📦 Complete Installation Commands

### Step 1: Clean Install (Remove Conflicting Packages)
```bash
# Activate virtual environment
venv\Scripts\activate

# Remove old/conflicting packages
pip uninstall moonshine moonshine-speech useful-moonshine tensorflow keras -y
```

### Step 2: Install Correct Voice Dependencies
```bash
# Install Kokoro TTS
pip install kokoro>=0.9.4 soundfile

# Install Moonshine STT (ONNX version - NO TensorFlow!)
pip install useful-moonshine-onnx

# Install audio processing
pip install numpy torch torchaudio
```

### Step 3: Install espeak-ng System Dependency
**Windows**: Download and run installer from https://github.com/espeak-ng/espeak-ng/releases

### Step 4: Verify Installation
```bash
# Test Kokoro
python test_kokoro.py

# Check espeak-ng
espeak-ng --version

# Restart Django
python manage.py runserver
```

---

## 📋 Summary: What You Need to Install

| Package | Command | Required For |
|---------|---------|--------------|
| **kokoro** | `pip install kokoro>=0.9.4 soundfile` | Text-to-Speech |
| **useful-moonshine-onnx** | `pip install useful-moonshine-onnx` | Speech-to-Text |
| **espeak-ng** | Download .msi installer | Kokoro dependency |
| **numpy** | `pip install numpy` | Audio processing |
| **torch** | `pip install torch` | Neural networks |

---

## ⚡ Quick Fix Script

Create a file `fix_dependencies.bat`:

```batch
@echo off
echo Fixing Voice Interview Dependencies...
echo.

echo Step 1: Removing old packages...
call venv\Scripts\activate
pip uninstall -y moonshine moonshine-speech useful-moonshine tensorflow keras

echo.
echo Step 2: Installing correct packages...
pip install kokoro>=0.9.4 soundfile numpy torch
pip install useful-moonshine-onnx

echo.
echo Step 3: Manual action required!
echo ========================================
echo INSTALL espeak-ng manually:
echo 1. Go to: https://github.com/espeak-ng/espeak-ng/releases
echo 2. Download: espeak-ng-X64.msi
echo 3. Run the installer
echo 4. Restart your terminal
echo ========================================
echo.

echo Step 4: Testing installation...
python test_kokoro.py

pause
```

Run it:
```bash
fix_dependencies.bat
```

---

## 🚨 Common Errors & Solutions

### Error: "No module named 'tensorflow'"
**Solution**: Uninstall old moonshine, install `useful-moonshine-onnx` instead

### Error: "espeak-ng not found"
**Solution**: Install espeak-ng system package (download .msi from GitHub)

### Error: "Question generation failed"
**Solution**: Check GEMINI_API_KEY in .env file

### Error: "ModuleNotFoundError: No module named 'moonshine'"
**Solution**: You removed the wrong package. Install: `pip install useful-moonshine-onnx`

---

## ✅ After Installation Checklist

- [ ] Removed old moonshine packages
- [ ] Installed `useful-moonshine-onnx`
- [ ] Installed `kokoro>=0.9.4`
- [ ] Installed espeak-ng system package
- [ ] Restarted terminal
- [ ] Verified with `python test_kokoro.py`
- [ ] Checked GEMINI_API_KEY in .env
- [ ] Restarted Django server

---

## 📞 Still Having Issues?

If you still get errors after following all steps:
1. Share the complete error traceback
2. Run: `pip list | findstr "moonshine kokoro torch"`
3. Check: `espeak-ng --version`
4. Verify: API key in .env file
