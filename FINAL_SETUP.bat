@echo off
echo ========================================
echo VOICE INTERVIEW - FINAL SETUP
echo ========================================
echo.
echo This will install ALL dependencies automatically.
echo.
pause

REM Change to project root
cd /d "%~dp0"

REM Activate virtual environment
echo [1/7] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Could not activate venv
    echo Make sure you have a venv folder in: %CD%
    pause
    exit /b 1
)

REM Update pip
echo.
echo [2/7] Updating pip...
python -m pip install --upgrade pip --quiet

REM Remove conflicting packages
echo.
echo [3/7] Removing old/conflicting packages...
pip uninstall -y moonshine moonshine-speech tensorflow keras useful-moonshine 2>nul
echo Done!

REM Install Kokoro TTS
echo.
echo [4/7] Installing Kokoro TTS + Audio Libraries...
pip install --quiet kokoro>=0.9.4 soundfile numpy
if errorlevel 1 (
    echo ERROR: Failed to install Kokoro
    pause
    exit /b 1
)
echo Done!

REM Install PyTorch (CPU version)
echo.
echo [5/7] Installing PyTorch (this may take a minute)...
pip install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo WARNING: PyTorch installation had issues, but continuing...
)
echo Done!

REM Install Moonshine from GitHub - THE CRITICAL COMMAND!
echo.
echo [6/7] Installing Moonshine STT from GitHub...
echo Command: pip install git+https://github.com/moonshine-ai/moonshine.git#subdirectory=moonshine-onnx
echo This will download and compile, please wait...
pip install git+https://github.com/moonshine-ai/moonshine.git#subdirectory=moonshine-onnx
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Moonshine from GitHub
    echo.
    echo This might be due to:
    echo 1. No internet connection
    echo 2. Git not installed
    echo 3. GitHub connection issues
    echo.
    echo Try installing Git for Windows from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo Done!

REM Verify installations
echo.
echo [7/7] Verifying installations...
python -c "import kokoro; import moonshine_onnx; import torch; print('✅ All packages installed successfully!')"
if errorlevel 1 (
    echo WARNING: Some packages may not have installed correctly
    echo But continuing anyway...
)

echo.
echo ========================================
echo Python Packages: INSTALLED ✅
echo ========================================
echo.
echo CRITICAL: One more manual step!
echo.
echo You MUST install espeak-ng:
echo.
echo 1. I will open the download page in your browser
echo 2. Download: espeak-ng-X64.msi (for 64-bit Windows)
echo 3. Run the installer (double-click the .msi file)
echo 4. Use default settings
echo 5. After installation, RESTART this terminal
echo.
pause

REM Open espeak-ng download page
start https://github.com/espeak-ng/espeak-ng/releases

echo.
echo ========================================
echo After installing espeak-ng:
echo ========================================
echo.
echo 1. CLOSE this terminal
echo 2. Open a NEW terminal
echo 3. cd to project folder
echo 4. Run: venv\Scripts\activate
echo 5. Run: python test_kokoro.py
echo 6. If test passes, run: python manage.py runserver
echo 7. Open: http://127.0.0.1:8000/interview/voice/
echo.
echo ========================================
pause
