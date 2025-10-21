from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, Depends, File, UploadFile, Form, HTTPException
)
from fastapi.responses import JSONResponse
from uuid import uuid4
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.config import SessionLocal
from app.models.meeting import Participant, MeetingAudio, Meeting
from datetime import datetime
import psycopg2
import tempfile, shutil, subprocess, os, uuid
import whisper  # ✅ Whisper for accurate offline transcription

router = APIRouter(prefix="/meeting", tags=["meeting"])

# ---------------------- In-memory meeting store ----------------------
meetings: Dict[str, Dict[str, Any]] = {}

# ---------------------- DB Helper ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- Load Whisper Model (once globally) ----------------------
# Model choices: tiny | base | small | medium | large
print("🎙️ Loading Whisper model... (this may take a minute on first run)")
WHISPER_MODEL = whisper.load_model("small")
print("✅ Whisper model loaded successfully!")

def convert_webm_to_wav(input_path: str, output_path: str):
    """Convert WebM audio to 16kHz mono WAV for Whisper."""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-vn",
        "-f", "wav",
        output_path
    ]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {process.stderr.decode()}")

# ---------------------- Create Meeting ----------------------
@router.post("/start")
async def start_meeting(
    title: str = Form(...),
    speaker: str = Form(...),
    db: Session = Depends(get_db)
):
    """Start a new meeting and mark it active."""
    meeting_id = str(uuid4())[:8]

    meetings[meeting_id] = {
        "participants": [{"name": speaker, "email": None}],
        "participants_ws": [],
        "is_active": True,
        "speaker": speaker,
        "created_from_form": True,
    }

    meeting = Meeting(id=meeting_id, title=title, speaker=speaker, is_active=True)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return {"message": "Meeting started", "meeting_id": meeting_id, "speaker": speaker}

# ---------------------- End Meeting ----------------------
@router.post("/{meeting_id}/end")
async def end_meeting(meeting_id: str, audio_file: UploadFile = File(...)):
    """
    Ends meeting: converts audio, transcribes using Whisper, and returns transcript text.
    """
    try:
        # ✅ Read uploaded audio
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file received")

        file_format = (
            audio_file.filename.split('.')[-1]
            if '.' in audio_file.filename else 'webm'
        )

        # ✅ Save audio temporarily
        temp_dir = tempfile.mkdtemp(prefix="meeting_audio_")
        input_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.{file_format}")
        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        # ✅ Convert WebM → WAV (for Whisper)
        wav_path = os.path.join(temp_dir, "converted.wav")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-vn",
            "-f", "wav",
            wav_path
        ]
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"FFmpeg conversion failed: {process.stderr.decode()}")

        # ✅ Transcribe using Whisper
        print(f"🔊 Transcribing meeting {meeting_id} ...")
        result = WHISPER_MODEL.transcribe(wav_path, language="en")
        transcript_text = result.get("text", "").strip()

        # ✅ Cleanup temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)

        print(f"✅ Transcription complete for meeting {meeting_id}!")

        # ✅ Return transcript to frontend
        return JSONResponse({
            "message": "Meeting ended successfully",
            "audio_saved": True,
            "meeting_id": meeting_id,
            "transcript_text": transcript_text
        })

    except Exception as e:
        print("❌ Error ending meeting:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {e}")
# ---------------------- Join Meeting ----------------------
@router.post("/{meeting_id}/join")
async def join_meeting(meeting_id: str, user: Dict[str, str], db: Session = Depends(get_db)):
    """Allow participant to join meeting and notify all others."""
    name = user.get("name", "Guest")
    email = user.get("email", "")

    if meeting_id not in meetings:
        meetings[meeting_id] = {
            "participants": [],
            "participants_ws": [],
            "is_active": False,
            "created_from_form": False
        }

    meeting = meetings[meeting_id]
    existing = db.query(Participant).filter(
        Participant.meeting_id == meeting_id, Participant.name == name
    ).first()

    if not existing:
        new_participant = Participant(name=name, email=email, meeting_id=meeting_id)
        db.add(new_participant)
        db.commit()

    if not any(p["name"] == name for p in meeting["participants"]):
        meeting["participants"].append({"name": name, "email": email})

    msg = {"type": "user_joined", "name": name}
    for client in list(meeting["participants_ws"]):
        try:
            await client.send_json(msg)
        except Exception:
            meeting["participants_ws"].remove(client)

    return {"status": "ok", "meeting_id": meeting_id}

# ---------------------- WebSocket Endpoint ----------------------
@router.websocket("/ws/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    """Real-time communication for participants (join messages, etc.)."""
    await websocket.accept()

    if meeting_id not in meetings:
        meetings[meeting_id] = {
            "participants": [],
            "participants_ws": [],
            "is_active": False,
            "created_from_form": False
        }

    meeting = meetings[meeting_id]
    meeting["participants_ws"].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "user_joined":
                name = data.get("name", "Guest")
                if not any(p["name"] == name for p in meeting["participants"]):
                    meeting["participants"].append({"name": name, "email": None})

                msg = {"type": "user_joined", "name": name}
                for client in list(meeting["participants_ws"]):
                    try:
                        await client.send_json(msg)
                    except Exception:
                        meeting["participants_ws"].remove(client)
            else:
                for client in list(meeting["participants_ws"]):
                    if client != websocket:
                        try:
                            await client.send_json(data)
                        except Exception:
                            meeting["participants_ws"].remove(client)
    except WebSocketDisconnect:
        if meeting_id in meetings and websocket in meetings[meeting_id]["participants_ws"]:
            meetings[meeting_id]["participants_ws"].remove(websocket)
