@echo off
echo ====================================
echo Voice Interview Setup - One-Click Install
echo ====================================
echo.

REM Activate virtual environment
echo [1/6] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Could not activate venv. Make sure you're in the project root directory.
    pause
    exit /b 1
)

REM Update pip
echo.
echo [2/6] Updating pip...
python -m pip install --upgrade pip

REM Remove old packages
echo.
echo [3/6] Removing old/conflicting packages...
pip uninstall -y moonshine moonshine-speech tensorflow keras useful-moonshine 2>nul

REM Install Kokoro TTS
echo.
echo [4/6] Installing Kokoro TTS...
pip install kokoro>=0.9.4 soundfile numpy

REM Install PyTorch (CPU version)
echo.
echo [5/6] Installing PyTorch...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

REM Install Moonshine from GitHub
echo.
echo [6/6] Installing Moonshine STT from GitHub...
echo This may take a few minutes...
pip install git+https://github.com/moonshine-ai/moonshine.git#subdirectory=moonshine-onnx

echo.
echo ====================================
echo Python Packages Installed!
echo ====================================
echo.
echo CRITICAL: Manual step required!
echo.
echo You MUST install espeak-ng:
echo 1. Open: https://github.com/espeak-ng/espeak-ng/releases
echo 2. Download: espeak-ng-X64.msi
echo 3. Run the installer
echo 4. Restart your terminal
echo.
echo Press any key to open the download page in your browser...
pause
start https://github.com/espeak-ng/espeak-ng/releases

echo.
echo ====================================
echo Testing Installation
echo ====================================
echo.
echo After installing espeak-ng, run:
echo   python test_kokoro.py
echo.
echo Then start Django:
echo   python manage.py runserver
echo.
pause
