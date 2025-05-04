from fastapi import APIRouter, UploadFile, File, Form, WebSocket
from app.services.whisper_service import transcribe_audio, transcribe_stream

router = APIRouter()

@router.post("/transcribe/")
async def transcribe(
    file: UploadFile = File(...),
    task: str = Form("transcribe")  # "transcribe" or "translate"
):
    result = await transcribe_audio(file, task)
    return result

@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()

    audio_buffer = bytearray()

    while True:
        data = await websocket.receive()

        if "text" in data:
            if data["text"] == "EOF":
                break
        elif "bytes" in data:
            audio_buffer.extend(data["bytes"])

    result = await transcribe_stream(audio_buffer)

    await websocket.send_json(result)
    await websocket.close()
