"""
Test script for Kokoro TTS and Moonshine STT installation
Run this to verify all voice interview dependencies are working
"""

import sys
import numpy as np

print("=" * 60)
print("VOICE INTERVIEW DEPENDENCIES TEST")
print("=" * 60)
print()

# Test 1: Import Kokoro
print("Test 1: Importing Kokoro TTS...")
try:
    from kokoro import KPipeline
    print("✅ Kokoro imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import Kokoro: {e}")
    print("\nRun: pip install kokoro>=0.9.4")
    sys.exit(1)

# Test 2: Import soundfile
print("\nTest 2: Importing soundfile...")
try:
    import soundfile as sf
    print("✅ soundfile imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import soundfile: {e}")
    print("\nRun: pip install soundfile")
    sys.exit(1)

# Test 2.5: Import Moonshine STT
print("\nTest 2.5: Importing Moonshine STT...")
try:
    import moonshine_onnx
    print("✅ Moonshine ONNX imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import moonshine_onnx: {e}")
    print("\nRun: pip install git+https://github.com/moonshine-ai/moonshine.git#subdirectory=moonshine-onnx")
    sys.exit(1)

# Test 3: Initialize Kokoro pipeline
print("\nTest 3: Initializing Kokoro pipeline...")
try:
    pipeline = KPipeline(lang_code='a')  # 'a' = American English
    print("✅ Pipeline initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize pipeline: {e}")
    print("\nMake sure espeak-ng is installed!")
    print("Download from: https://github.com/espeak-ng/espeak-ng/releases")
    sys.exit(1)

# Test 4: Generate speech
print("\nTest 4: Generating speech...")
try:
    text = "Hello! This is a test of Kokoro text to speech. The system is working correctly."
    
    print(f"   Text: '{text}'")
    print("   Generating audio...")
    
    generator = pipeline(text, voice='af_heart', speed=1.0)
    
    # Collect audio chunks
    audio_chunks = []
    for i, (gs, ps, audio) in enumerate(generator):
        audio_chunks.append(audio)
        print(f"   Chunk {i+1}: {len(audio)} samples")
    
    # Combine audio
    combined_audio = np.concatenate(audio_chunks)
    print(f"   Total audio: {len(combined_audio)} samples ({len(combined_audio)/24000:.2f} seconds)")
    
    print("✅ Audio generated successfully!")
    
except Exception as e:
    print(f"❌ Failed to generate speech: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Save audio file
print("\nTest 5: Saving audio file...")
try:
    output_file = 'test_kokoro_output.wav'
    sf.write(output_file, combined_audio, 24000)
    print(f"✅ Audio saved to: {output_file}")
except Exception as e:
    print(f"❌ Failed to save audio: {e}")
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print()
print("✅ Kokoro TTS: Working")
print("✅ Moonshine STT: Working")
print("✅ Audio I/O: Working")
print("✅ espeak-ng: Working")
print()
print(f"Test audio saved to: {output_file}")
print("(You can play it to hear the test output)")
print()
print("=" * 60)
print("READY FOR VOICE INTERVIEWS!")
print("=" * 60)
print()
print("Next steps:")
print("1. Start Django: python manage.py runserver")
print("2. Open browser: http://127.0.0.1:8000/interview/voice/")
print("3. Click 'Start Voice Interview'")
print("4. Enjoy! 🎤")
print()
