@echo off
echo ====================================
echo Voice Interview Setup Script
echo ====================================
echo.

echo Step 1: Installing Python packages...
echo.
call venv\Scripts\activate
pip install kokoro>=0.9.4 soundfile numpy torch torchaudio

echo.
echo ====================================
echo Step 2: espeak-ng Installation Required
echo ====================================
echo.
echo IMPORTANT: You need to install espeak-ng manually!
echo.
echo 1. Go to: https://github.com/espeak-ng/espeak-ng/releases
echo 2. Download the latest .msi file (e.g., espeak-ng-X64.msi)
echo 3. Run the installer
echo 4. Restart your terminal after installation
echo.
echo After installing espeak-ng, you can test Kokoro with:
echo    python test_kokoro.py
echo.
pause

echo.
echo Testing if espeak-ng is installed...
espeak-ng --version
if errorlevel 1 (
    echo.
    echo [WARNING] espeak-ng not found! Please install it manually.
    echo Download from: https://github.com/espeak-ng/espeak-ng/releases
) else (
    echo.
    echo [SUCCESS] espeak-ng is installed!
)

echo.
echo ====================================
echo Installation Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Make sure espeak-ng is installed (see above)
echo 2. Restart your terminal
echo 3. Run: python manage.py runserver
echo 4. Navigate to: http://127.0.0.1:8000/interview/voice/
echo.
pause
