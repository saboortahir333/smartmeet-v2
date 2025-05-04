# 🎧 SmartMeet - AI-Powered Meeting Transcription

SmartMeet is an AI-based backend service that provides real-time and post-meeting audio transcription using OpenAI's Whisper model. It supports automatic language detection, translation to English, and is built with FastAPI for flexible integration.

---

## 🚀 Features

- 🎧 Live and post-meeting transcription
- 🌍 Automatic language detection
- 🌐 Translation from any language to English (optional)
- 🎤 Whisper-powered transcription (supports `.wav`, `.mp3`, etc.)
- 🔀 REST API + WebSocket support (for live streaming)
- 🧪 FastAPI backend with async handling

---

## 📦 Tech Stack

- **Python**
- **FastAPI**
- **OpenAI Whisper**
- **Uvicorn**
- **WebSockets (for live transcription)**
- **Postman** (for API testing)

---

## 📁 Project Structure

```bash
smartmeet-backend/
│
├── app/
│   ├── api/
│   │   └── transcribe.py       # API route for transcription
│   ├── services/
│   │   └── whisper_service.py  # Core Whisper logic
│   └── main.py                 # FastAPI app entry point
│
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── ...
```

---

## 🪠 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourfriend/smartmeet.git
cd smartmeet
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for Swagger API UI.

---

## 📬 API Endpoints

### POST `/transcribe/`

**Body:**

- `file`: Upload audio file
- `task`: `transcribe` or `translate` (optional)

**Response:**

```json
{
  "language": "ur",
  "text": "Transcribed or translated text"
}
```

---

## 🤖 Whisper Model Sizes

- `tiny` (\~39 MB)
- `base` (\~74 MB)
- `small` (\~244 MB)
- `medium` (\~769 MB)
- `large` (\~1550 MB)

Change model in `whisper_service.py`:

```python
model = whisper.load_model("base")  # or "medium", "large", etc.
```

---

## 🥭 Testing

You can test endpoints with:

- **Postman**
- **curl**
- **Swagger UI** (`/docs`)

---

## 🧫 TODO

- [x] Post-meeting transcription
- [x] Translation support
- [ ] Live transcription via WebSocket
- [ ] Summarization and action item extraction
- [ ] Frontend integration

---

## 📄 License

MIT License

---

## 👥 Contributors

- \[Your Name]
- \[Friend's GitHub Username]
