async def transcribe_audio(file, task):
    return {"filename": file.filename, "task": task}
