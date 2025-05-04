import whisper
import tempfile

model = whisper.load_model("small")  # or "small", "medium", etc.

async def transcribe_audio(file, task: str = "transcribe"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Detect language
    audio = whisper.load_audio(tmp_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    detected_language = max(probs, key=probs.get)

    # Language mapping
    language_names = {
        "en": "English",
        "ur": "Urdu",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "hi": "Hindi",
        "zh": "Chinese",
        "ja": "Japanese",
        "ar": "Arabic",
        # extend this list as needed
    }
    detected_language_name = language_names.get(detected_language, detected_language)

    # Transcribe or Translate
    result = model.transcribe(tmp_path, task=task)

    return {
        "language_code": detected_language,
        "language_name": detected_language_name,
        "text": result["text"]
    }


async def transcribe_stream(audio_bytes: bytes, task: str = "transcribe"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    audio = whisper.load_audio(tmp_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    detected_language = max(probs, key=probs.get)

    result = model.transcribe(tmp_path, task=task)

    return {
        "language": detected_language,
        "text": result["text"]
    }
