# app/api/transcribe_ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import whisper
import tempfile

router = APIRouter()

# Load Whisper model once globally
model = whisper.load_model("base")

@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()

    audio_buffer = b""

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer += data

            # Start processing when buffer is large enough
            if len(audio_buffer) > 16000 * 5:  # about 5 sec of audio at 16kHz
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_buffer)
                    tmp_path = tmp.name

                result = model.transcribe(tmp_path, task="transcribe")

                await websocket.send_json({
                    "text": result["text"]
                })

                audio_buffer = b""  # Reset buffer after sending back
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
