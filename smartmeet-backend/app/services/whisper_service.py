import whisper
import tempfile
import os

# Load the Whisper model (you can change "small" to "base", "medium", etc.)
model = whisper.load_model("small")

async def transcribe_audio(file, task="transcribe"):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Run Whisper transcription
        result = model.transcribe(tmp_path, task=task)
        return {
            "filename": file.filename,
            "task": task,
            "transcription": result.get("text", "")
        }
    finally:
        # Clean up the temporary file
        os.remove(tmp_path)
