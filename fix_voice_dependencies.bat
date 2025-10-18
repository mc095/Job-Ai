@echo off
echo ====================================
echo Voice Dependencies Fix Script
echo ====================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo ====================================
echo Step 1: Removing Conflicting Packages
echo ====================================
echo.
echo Uninstalling old moonshine packages...
pip uninstall -y moonshine moonshine-speech useful-moonshine 2>nul
echo Uninstalling tensorflow (not needed)...
pip uninstall -y tensorflow keras 2>nul
echo Old packages removed!

echo.
echo ====================================
echo Step 2: Installing Correct Packages
echo ====================================
echo.

echo Installing Kokoro TTS...
pip install kokoro>=0.9.4 soundfile
echo.

echo Installing Moonshine STT (ONNX - NO TensorFlow!)...
pip install useful-moonshine-onnx
echo.

echo Installing audio dependencies...
pip install numpy torch torchaudio
echo.

echo [SUCCESS] Python packages installed!

echo.
echo ====================================
echo Step 3: espeak-ng Installation
echo ====================================
echo.
echo CRITICAL: You must install espeak-ng manually!
echo.
echo 1. Go to: https://github.com/espeak-ng/espeak-ng/releases
echo 2. Download: espeak-ng-X64.msi (for 64-bit Windows)
echo    OR: espeak-ng-X86.msi (for 32-bit Windows)
echo 3. Run the downloaded .msi installer
echo 4. Follow the installation wizard
echo 5. Restart your terminal after installation
echo.
echo Press any key to continue after you've installed espeak-ng...
pause

echo.
echo ====================================
echo Step 4: Verifying Installation
echo ====================================
echo.

echo Checking espeak-ng...
espeak-ng --version
if errorlevel 1 (
    echo.
    echo [WARNING] espeak-ng NOT detected!
    echo Please install it from: https://github.com/espeak-ng/espeak-ng/releases
    echo Then restart your terminal and run this script again.
) else (
    echo [SUCCESS] espeak-ng is installed!
)

echo.
echo Checking installed packages...
echo.
echo Kokoro:
pip show kokoro | findstr "Name Version"
echo.
echo Moonshine ONNX:
pip show useful-moonshine-onnx | findstr "Name Version"
echo.
echo NumPy:
pip show numpy | findstr "Name Version"
echo.
echo PyTorch:
pip show torch | findstr "Name Version"

echo.
echo ====================================
echo Step 5: Testing Kokoro TTS
echo ====================================
echo.
echo Running test script...
python test_kokoro.py

echo.
echo ====================================
echo Installation Complete!
echo ====================================
echo.
echo Next steps:
echo 1. If espeak-ng test failed, install it and restart terminal
echo 2. Check your .env file for GEMINI_API_KEY
echo 3. Start Django: python manage.py runserver
echo 4. Go to: http://127.0.0.1:8000/interview/voice/
echo.
pause
