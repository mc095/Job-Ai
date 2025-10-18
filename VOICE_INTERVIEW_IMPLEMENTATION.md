# Voice-to-Voice Mock Interview System

## 🎯 Overview

A complete voice-based mock interview system using **Kokoro TTS** (Text-to-Speech) and **Moonshine STT** (Speech-to-Text) for a seamless, ChatGPT-voice-like experience. No keyboard typing required - just speak naturally!

## ✨ Key Features

### 🎤 **Advanced Speech Recognition**
- **Moonshine STT**: State-of-the-art speech recognition optimized for noisy environments
- **Noise Suppression**: Works great even with background noise
- **Echo Cancellation**: Built-in audio processing for clear transcription
- **Auto Gain Control**: Automatic volume adjustment

### 🔊 **Natural Voice Output**
- **Kokoro TTS**: High-quality neural text-to-speech
- **Natural Prosody**: Realistic interviewer voice with proper intonation
- **Low Latency**: Fast audio generation using ONNX runtime
- **Customizable Speed**: Adjustable speaking rate

### 🤖 **AI-Powered Interviews**
- **Contextual Questions**: AI generates relevant questions based on job role and resume
- **Conversational Flow**: Questions adapt based on previous responses
- **Comprehensive Feedback**: Detailed analysis with scores and recommendations
- **Progress Tracking**: Visual progress indicators and session management

### 🎨 **Modern UI/UX**
- **Voice-First Interface**: Large, clear buttons optimized for voice interaction
- **Real-time Status**: Visual feedback for recording, processing, and playback states
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **Accessibility**: Keyboard navigation and screen reader support

## 📁 File Structure

```
ai_job_helper/
├── interview/
│   ├── voice_service.py         # Voice processing (TTS + STT)
│   ├── voice_views.py            # Voice interview endpoints
│   ├── models.py                 # Interview session models
│   └── urls.py                   # URL routing
├── templates/interview/
│   ├── voice_home.html           # Landing page
│   ├── voice_session.html        # Interview session UI
│   └── feedback.html             # Feedback display
└── ai_agents/
    └── ai_service.py             # AI question generation & feedback
```

## 🚀 Installation

### 1. Install Dependencies

```bash
# Install voice dependencies
pip install -r voice_interview_requirements.txt

# Install FFmpeg (required for audio processing)
# Windows
choco install ffmpeg

# Mac
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### 2. Verify Installation

```python
# Test TTS
from interview.voice_service import get_voice_service
service = get_voice_service()
audio = service.generate_interviewer_speech("Hello, welcome to the interview!")

# Test STT
# Record audio and pass to service.process_user_speech(audio_bytes)
```

### 3. Environment Setup

Ensure your `.env` has:
```
GEMINI_API_KEY=your_api_key_here
DJANGO_DEBUG=True
```

## 🎮 Usage

### For Users

1. **Start Interview**
   - Navigate to `/interview/voice/`
   - Enter job role/position
   - Select number of questions and difficulty
   - Click "Start Voice Interview"

2. **During Interview**
   - Listen to the AI interviewer's question
   - Click the microphone button to record your answer
   - Speak clearly and naturally (30-90 seconds)
   - Click stop when finished
   - Review transcription and submit

3. **Get Feedback**
   - Complete all questions
   - View detailed performance analysis
   - See scores for technical, communication, and problem-solving skills
   - Get actionable recommendations

### For Developers

#### Create a Voice Interview Session

```python
from interview.models import InterviewSession
from interview.voice_service import get_voice_service

# Create session
session = InterviewSession.objects.create(
    user=request.user,
    job_description="Senior Software Engineer",
    resume_text="...",
    total_questions=10
)

# Generate first question audio
voice_service = get_voice_service()
audio = voice_service.generate_interviewer_speech("Tell me about yourself")
```

#### Process Voice Response

```python
# Transcribe user's audio
transcription = voice_service.process_user_speech(audio_bytes)

# Generate AI response
from ai_agents.ai_service import AIService
ai = AIService()
next_question = ai.generate_interview_question(
    job_description=session.job_description,
    resume=session.resume_text,
    conversation_history=[...]
)

# Convert to audio
audio = voice_service.generate_interviewer_speech(next_question)
```

## 🔧 Technical Details

### Voice Service Architecture

```python
VoiceInterviewService
├── KokoroTTS
│   ├── Model: kokoro-onnx
│   ├── Output: 24kHz WAV
│   └── Device: CUDA/CPU
└── MoonshineSTT
    ├── Model: moonshine-tiny/base
    ├── Input: WAV audio
    └── Noise: Robust to background noise
```

### Data Flow

```
User Speech → Browser MediaRecorder → Backend API
              ↓
         Moonshine STT
              ↓
         Transcription → AI Service (Gemini)
              ↓
         Next Question → Kokoro TTS
              ↓
         Audio WAV → Browser Audio Player
```

### Models Used

| Component | Model | Size | Speed | Quality |
|-----------|-------|------|-------|---------|
| **TTS** | Kokoro (ONNX) | ~100MB | Fast | High |
| **STT** | Moonshine-tiny | ~250MB | Very Fast | Good |
| **STT** | Moonshine-base | ~500MB | Fast | Excellent |
| **AI** | Gemini 2.5 Flash | Cloud | Fast | Excellent |

### Performance Optimizations

1. **ONNX Runtime**: Optimized TTS inference
2. **Batch Processing**: Efficient audio generation
3. **Streaming**: Progressive audio playback
4. **Caching**: Session data cached in database
5. **Async Operations**: Non-blocking audio processing

## 🌐 API Endpoints

### Voice Interview Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/interview/voice/` | GET | Voice interview home page |
| `/interview/voice/start/` | POST | Start new interview session |
| `/interview/voice/<id>/session/` | GET | Interview session page |
| `/interview/voice/<id>/process/` | POST | Process voice response |
| `/interview/voice/<id>/audio/latest/` | GET | Get latest question audio |
| `/interview/voice/<id>/feedback/` | GET | Get session feedback |
| `/interview/voice/tts/` | GET | Convert text to speech (test) |
| `/interview/voice/transcribe/` | POST | Transcribe audio (test) |

### Request/Response Examples

**Start Interview:**
```javascript
POST /interview/voice/start/
{
  "job_description": "Senior Software Engineer",
  "num_questions": 10,
  "difficulty": "medium"
}

Response:
{
  "session_id": "507f1f77bcf86cd799439011",
  "question": "Tell me about your experience...",
  "audio_url": "/interview/voice/.../audio/latest/",
  "question_number": 1,
  "total_questions": 10
}
```

**Process Response:**
```javascript
POST /interview/voice/<id>/process/
FormData: { audio: <audio blob> }

Response:
{
  "transcription": "I have 5 years of experience...",
  "next_question": "Can you describe a challenging project?",
  "question_number": 2,
  "completed": false,
  "audio_url": "/interview/voice/.../audio/latest/"
}
```

## 🎨 UI Components

### Voice Session Interface

- **Question Display**: Large, readable text area
- **Audio Player**: Auto-plays interviewer questions
- **Record Button**: Large circular button (32x32 touch target)
- **Status Indicator**: Real-time visual feedback
- **Transcription View**: Shows what you said
- **Progress Bar**: Visual completion tracking
- **Timer**: Recording duration display

### Status States

1. **Listening** (Blue): AI is speaking
2. **Ready** (Green): Ready to record
3. **Recording** (Red): Actively recording
4. **Processing** (Yellow): Transcribing/generating

## 🔒 Security & Privacy

- **CSRF Protection**: All POST endpoints protected
- **User Authentication**: Login required for all routes
- **Audio Data**: Not permanently stored (processed in memory)
- **Session Isolation**: Users can only access their own sessions
- **API Rate Limiting**: Prevents abuse

## 🧪 Testing

### Unit Tests

```python
# Test voice service
def test_tts():
    service = get_voice_service()
    audio = service.generate_interviewer_speech("Hello")
    assert len(audio) > 0
    assert audio[:4] == b'RIFF'  # WAV header

def test_stt():
    service = get_voice_service()
    # Load test audio file
    with open('test.wav', 'rb') as f:
        audio = f.read()
    text = service.process_user_speech(audio)
    assert len(text) > 0
```

### Integration Tests

```python
def test_interview_flow():
    # Start session
    response = client.post('/interview/voice/start/', {
        'job_description': 'Developer'
    })
    assert response.status_code == 200
    data = response.json()
    
    # Process response
    response = client.post(
        f'/interview/voice/{data["session_id"]}/process/',
        {'audio': audio_file}
    )
    assert response.status_code == 200
```

## 📊 Performance Metrics

### Latency Targets

- **TTS Generation**: <500ms for 10-second audio
- **STT Transcription**: <1s for 60-second recording
- **AI Question**: <2s for contextual question
- **Total Turnaround**: <4s from submit to next question

### Resource Usage

- **CPU**: 1-2 cores during processing
- **RAM**: ~2GB with models loaded
- **GPU**: Optional, 2-3x faster with CUDA
- **Bandwidth**: ~50KB per audio response

## 🐛 Troubleshooting

### Common Issues

**1. "Microphone not accessible"**
- Grant browser microphone permissions
- Check system microphone settings
- Try HTTPS (required for getUserMedia)

**2. "Audio playback failed"**
- Check browser audio permissions
- Verify FFmpeg is installed
- Test with different browser

**3. "Transcription is inaccurate"**
- Speak clearly and slowly
- Reduce background noise
- Use better microphone
- Try moonshine-base model (more accurate)

**4. "TTS sounds robotic"**
- Normal for Kokoro (neural but not perfect)
- Adjust speed parameter
- Consider upgrading to Kokoro-v2 when available

**5. "Session not found"**
- Check session ID in URL
- Session may have expired
- Start new interview

## 🚀 Future Enhancements

### Planned Features

- [ ] Real-time transcription during recording
- [ ] Multi-language support (Spanish, French, etc.)
- [ ] Video support (visual cues)
- [ ] Mock panel interviews (multiple AI interviewers)
- [ ] Industry-specific question banks
- [ ] Voice emotion analysis
- [ ] Pause/resume functionality
- [ ] Export transcript as PDF
- [ ] Practice mode (instant feedback)
- [ ] Interview coaching tips

### Model Upgrades

- [ ] Kokoro v2 (better prosody)
- [ ] Moonshine XL (highest accuracy)
- [ ] Whisper integration (alternative STT)
- [ ] GPT-4 for advanced feedback

## 📝 License & Credits

### Dependencies

- **Kokoro TTS**: MIT License
- **Moonshine STT**: Apache 2.0 License
- **Gemini API**: Google Terms of Service

### Contributors

Built with ❤️ for better interview preparation

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review error logs in Django admin
3. Test individual components (TTS/STT)
4. Verify all dependencies installed

---

## Quick Start Checklist

- [ ] Install `voice_interview_requirements.txt`
- [ ] Install FFmpeg on system
- [ ] Set `GEMINI_API_KEY` in `.env`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test TTS: `/interview/voice/tts/?text=Hello`
- [ ] Navigate to `/interview/voice/`
- [ ] Start your first voice interview!

**Happy Interviewing! 🎤✨**
