from fastapi import APIRouter, UploadFile, File, Form

from app.services.whisper_service import transcribe_audio

router = APIRouter()

@router.post("/transcribe/")
async def transcribe(file: UploadFile = File(...), task: str = Form("transcribe")):
    result = await transcribe_audio(file, task)
    return result
