import whisper

# Load Whisper model once when the server starts
model = whisper.load_model("tiny")


def transcribe_audio(audio_path: str):
    """
    Detects language and transcribes audio using Whisper.
    """

    # Transcribe with language detection
    result = model.transcribe(audio_path)

    return {
        "language": result["language"],
        "transcript": result["text"].strip()
    }