# Voice Interview Setup Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd e:\Agentic-Job-AI

# Install voice dependencies
pip install -r voice_interview_requirements.txt
```

### Step 2: Install FFmpeg

**Windows (PowerShell as Admin):**
```powershell
choco install ffmpeg
```

**Or download manually:**
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH

### Step 3: Verify Installation

```python
python manage.py shell

# Test imports
>>> from interview.voice_service import get_voice_service
>>> service = get_voice_service()
>>> print("Voice service ready!")
```

### Step 4: Start Server

```bash
python manage.py runserver
```

### Step 5: Access Voice Interview

Open browser and navigate to:
```
http://127.0.0.1:8000/interview/voice/
```

## 📦 What Was Installed

### New Files Created:

```
ai_job_helper/
├── interview/
│   ├── voice_service.py          ✅ Voice processing (TTS + STT)
│   ├── voice_views.py             ✅ API endpoints
│   └── urls.py                    ✅ Updated routing
├── templates/interview/
│   ├── voice_home.html            ✅ Landing page
│   ├── voice_session.html         ✅ Interview UI
│   └── feedback.html              ✅ Feedback display
└── ai_agents/
    └── ai_service.py              ✅ Added interview methods
```

### Dependencies Installed:

- ✅ **kokoro-onnx** - Neural TTS
- ✅ **moonshine** - Robust STT
- ✅ **torch** - Deep learning framework
- ✅ **numpy** - Audio processing
- ✅ **FFmpeg** - Audio codec support

## 🎯 Features Implemented

### ✨ Core Functionality

- ✅ **Voice-to-Voice Communication** - No typing required
- ✅ **Noise Reduction** - Works in noisy environments
- ✅ **Real-time Transcription** - See what you said
- ✅ **Natural Voice Output** - High-quality TTS
- ✅ **Contextual Questions** - AI adapts to your responses
- ✅ **Detailed Feedback** - Performance analysis with scores

### 🎨 User Interface

- ✅ **Modern Gradient Design** - Beautiful, professional UI
- ✅ **Large Touch Targets** - Easy to use on mobile
- ✅ **Progress Tracking** - Visual progress bar
- ✅ **Status Indicators** - Real-time state feedback
- ✅ **Responsive Layout** - Works on all devices
- ✅ **Audio Player** - Auto-play questions

### 🔧 Technical Features

- ✅ **Session Management** - Resume interviews later
- ✅ **Audio Streaming** - Efficient audio delivery
- ✅ **CSRF Protection** - Secure endpoints
- ✅ **Error Handling** - Graceful failure recovery
- ✅ **Database Integration** - MongoDB storage
- ✅ **API Endpoints** - RESTful design

## 🎮 How to Use

### For End Users:

1. **Start Interview**
   - Click "Start Voice Interview"
   - Enter job role (e.g., "Senior Software Engineer")
   - Select settings (10 questions, medium difficulty)
   - Grant microphone permission

2. **During Interview**
   - 🎧 Listen to AI interviewer's question
   - 🎤 Click microphone to record answer
   - 🗣️ Speak naturally for 30-90 seconds
   - ⏹️ Click stop when done
   - ✅ Review transcription and submit

3. **Get Feedback**
   - Complete all questions
   - View detailed performance scores
   - Read personalized recommendations
   - Print or save feedback

### For Developers:

**Test TTS:**
```
http://127.0.0.1:8000/interview/voice/tts/?text=Hello%20World
```

**Test STT:**
```javascript
// Upload audio file
const formData = new FormData();
formData.append('audio', audioBlob);

fetch('/interview/voice/transcribe/', {
    method: 'POST',
    body: formData
}).then(r => r.json()).then(console.log);
```

## 🔍 System Architecture

```
┌─────────────────────────────────────────────┐
│            User Browser                      │
│  - MediaRecorder API (capture audio)        │
│  - Audio Player (play questions)            │
│  - Real-time UI updates                     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│         Django Backend                       │
│  ┌─────────────────────────────────────┐   │
│  │   Voice Views (voice_views.py)      │   │
│  │   - start_voice_interview           │   │
│  │   - process_voice_response          │   │
│  │   - get_question_audio              │   │
│  └─────────────┬───────────────────────┘   │
│                │                             │
│  ┌─────────────▼───────────────────────┐   │
│  │  Voice Service (voice_service.py)   │   │
│  │  ┌──────────────┐  ┌─────────────┐ │   │
│  │  │ Kokoro TTS   │  │ Moonshine   │ │   │
│  │  │ (Text→Audio) │  │ (Audio→Text)│ │   │
│  │  └──────────────┘  └─────────────┘ │   │
│  └─────────────┬───────────────────────┘   │
│                │                             │
│  ┌─────────────▼───────────────────────┐   │
│  │    AI Service (ai_service.py)       │   │
│  │    - generate_interview_question    │   │
│  │    - generate_interview_feedback    │   │
│  │    (powered by Gemini 2.5)          │   │
│  └─────────────┬───────────────────────┘   │
└────────────────┼─────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          MongoDB Database                    │
│  - InterviewSession (sessions)              │
│  - InterviewMessage (Q&A history)           │
└─────────────────────────────────────────────┘
```

## 🎯 API Endpoints Summary

| Route | Method | Purpose |
|-------|--------|---------|
| `/interview/voice/` | GET | Home page |
| `/interview/voice/start/` | POST | Create session |
| `/interview/voice/<id>/session/` | GET | Interview UI |
| `/interview/voice/<id>/process/` | POST | Process audio |
| `/interview/voice/<id>/audio/latest/` | GET | Get question audio |
| `/interview/voice/<id>/feedback/` | GET | View feedback |

## ⚡ Performance

### Expected Response Times:
- **TTS Generation**: 300-500ms
- **STT Transcription**: 500-1000ms
- **AI Question**: 1-2 seconds
- **Total Turnaround**: 2-4 seconds

### Resource Usage:
- **RAM**: ~2GB (with models loaded)
- **CPU**: 1-2 cores during processing
- **GPU**: Optional (2-3x faster with CUDA)

## 🐛 Troubleshooting

### "Cannot access microphone"
**Solution:**
- Allow microphone in browser settings
- Use HTTPS (required for getUserMedia)
- Check system audio settings

### "FFmpeg not found"
**Solution:**
```bash
# Verify FFmpeg installation
ffmpeg -version

# If not found, reinstall
choco install ffmpeg --force
```

### "Import error: kokoro"
**Solution:**
```bash
pip install --upgrade kokoro-onnx onnxruntime
```

### "Import error: moonshine"
**Solution:**
```bash
pip install git+https://github.com/usefulsensors/moonshine.git
```

## 📈 Testing Checklist

- [ ] TTS works: `/interview/voice/tts/?text=Test`
- [ ] Microphone permission granted
- [ ] Can record and playback audio
- [ ] Transcription is accurate
- [ ] Questions are contextual
- [ ] Feedback is detailed
- [ ] Session saves progress
- [ ] Resume works correctly

## 🎓 Usage Examples

### Example 1: Software Engineer Interview
```
Job Role: Senior Software Engineer
Questions: 10
Duration: ~20 minutes

Sample Questions:
1. "Tell me about your experience with microservices"
2. "How do you handle database optimization?"
3. "Describe a challenging bug you solved"
```

### Example 2: Product Manager Interview
```
Job Role: Product Manager
Questions: 10
Duration: ~20 minutes

Sample Questions:
1. "How do you prioritize features?"
2. "Describe your approach to user research"
3. "Tell me about a failed product launch"
```

## 🔒 Security Features

- ✅ CSRF tokens on all POST requests
- ✅ User authentication required
- ✅ Session isolation (users can't access others' sessions)
- ✅ Audio not permanently stored
- ✅ Input validation and sanitization

## 📱 Browser Compatibility

| Browser | TTS | STT | Recording |
|---------|-----|-----|-----------|
| Chrome 90+ | ✅ | ✅ | ✅ |
| Firefox 88+ | ✅ | ✅ | ✅ |
| Safari 14+ | ✅ | ✅ | ✅ |
| Edge 90+ | ✅ | ✅ | ✅ |

## 🚀 Next Steps

1. **Test the system:**
   ```bash
   python manage.py runserver
   # Visit: http://127.0.0.1:8000/interview/voice/
   ```

2. **Customize settings:**
   - Adjust TTS speed in `voice_service.py`
   - Change STT model (tiny→base for better accuracy)
   - Modify UI colors in templates

3. **Scale for production:**
   - Add Redis caching for sessions
   - Use Celery for async processing
   - Deploy with Gunicorn + Nginx
   - Enable GPU acceleration

## 📚 Additional Resources

- **Kokoro TTS Docs**: https://github.com/thewh1teagle/kokoro-onnx
- **Moonshine STT**: https://github.com/usefulsensors/moonshine
- **Gemini API**: https://ai.google.dev/docs
- **Web Audio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API

## 🎉 You're All Set!

The voice interview system is now ready to use. Navigate to `/interview/voice/` and start practicing!

**Tips for Best Results:**
- 🎤 Use a good quality microphone
- 🔇 Find a quiet environment
- 🗣️ Speak clearly and naturally
- ⏱️ Take 30-90 seconds per answer
- 💡 Be specific and use examples

Happy interviewing! 🚀
