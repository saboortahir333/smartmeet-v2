from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.api import meeting, transcribe, transcribe_ws
from app.core.config import Base, engine
import psycopg2
import subprocess
import os
import tempfile

# -------------------------------
# 🚀 Initialize Database Tables
# -------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------
# ⚙️ Initialize FastAPI Application
# -------------------------------
app = FastAPI(title="SmartMeet AI Backend")

# -------------------------------
# 🌐 Configure CORS for Frontend (Next.js)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🔗 Register Routers
# -------------------------------
app.include_router(transcribe.router)
app.include_router(transcribe_ws.router)
app.include_router(meeting.router)

# -------------------------------
# 🎧 Audio Download & Conversion Endpoint
# -------------------------------

@app.get("/download_audio/{meeting_id}")
def download_audio(meeting_id: str):
    """
    Fetch audio (BYTEA) from PostgreSQL using a string meeting_id,
    convert it to .webm using FFmpeg, and return as downloadable file.
    """
    try:
        # --- Connect to PostgreSQL ---
        conn = psycopg2.connect(
            host="localhost",
            database="smartmeet_db",
            user="postgres",
            password="saboor12345"
        )
        cur = conn.cursor()

        # 🧠 Fetch audio by string-based meeting_id
        cur.execute("SELECT audio_data FROM meeting_audio WHERE meeting_id = %s", (meeting_id,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Audio not found for this meeting ID")

        audio_bytes = result[0]

        # --- Write audio bytes to a temporary raw file ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as raw_file:
            raw_file.write(audio_bytes)
            raw_path = raw_file.name

        # --- Prepare output path for converted WebM file ---
        webm_path = tempfile.NamedTemporaryFile(delete=False, suffix=".webm").name

        # --- Convert using FFmpeg ---
        subprocess.run([
            "ffmpeg", "-y", "-f", "wav", "-i", raw_path,
            "-c:a", "libopus", webm_path
        ], check=True)

        # --- Clean up raw file after conversion ---
        os.remove(raw_path)

        # --- Return converted audio as downloadable file ---
        return FileResponse(
            webm_path,
            media_type="audio/webm",
            filename=f"meeting_{meeting_id}.webm"
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg conversion failed: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
