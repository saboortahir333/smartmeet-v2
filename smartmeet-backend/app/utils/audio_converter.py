import psycopg2
import subprocess
import os

def fetch_and_convert_audio(meeting_id):
    connection = psycopg2.connect(
        host="localhost",
        database="smartmeet",
        user="postgres",
        password="saboor12345"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT audio_data FROM meeting_audio WHERE meeting_id = %s", (meeting_id,))
    audio_bytea = cursor.fetchone()[0]

    raw_path = f"/tmp/meeting_{meeting_id}.raw"
    webm_path = f"/tmp/meeting_{meeting_id}.webm"

    # Write the raw data
    with open(raw_path, "wb") as f:
        f.write(audio_bytea)

    # Convert to .webm using ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-f", "wav", "-i", raw_path,
        "-c:a", "libopus", webm_path
    ], check=True)

    cursor.close()
    connection.close()

    os.remove(raw_path)
    return webm_path
