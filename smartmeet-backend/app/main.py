from fastapi import FastAPI
from app.api import transcribe, transcribe_ws  # <-- added

app = FastAPI()

app.include_router(transcribe.router)
app.include_router(transcribe_ws.router)  # <-- added
