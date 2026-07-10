import whisper

model = None

def get_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("tiny")
    return model

def transcribe_audio(audio_path):
    model = get_model()
    result = model.transcribe(audio_path)
    return result