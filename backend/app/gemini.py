import os
import json
import time
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configure Gemini
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def evaluate_pronunciation(audio_path):

    prompt = """
You are an expert English pronunciation evaluator.

The attached file is an English speech recording.

Your tasks are:

1. Transcribe the audio accurately.
2. Detect the spoken language and return its ISO code in the "language" field (for example "en", "hi", "fr").
3. Evaluate the speaker's pronunciation.
4. Evaluate fluency.
5. Evaluate clarity.
6. Determine speaking pace.
7. Identify mispronounced words.
8. Suggest improvements.
9. Give overall feedback.

Return ONLY valid JSON in this exact format:

{
  "language": "en",
  "transcript": "",
  "corrected_transcript": "",
  "overall_score": 0,
  "pronunciation_score": 0,
  "fluency_score": 0,
  "clarity_score": 0,
  "pace": "",
  "mispronounced_words": [
    {
      "word": "",
      "severity": "",
      "issue": "",
      "tip": ""
    }
  ],
  "strengths": [],
  "suggestions": [],
  "overall_feedback": ""
}

Rules:
- Return ONLY JSON.
- Do NOT use markdown.
- Do NOT use code blocks.
- Do NOT explain your answer.
- Return the transcript exactly as spoken in the "transcript" field.
If small transcription corrections are needed, return the corrected version in "corrected_transcript".
"""
    try:

        # Upload audio to Gemini
        uploaded_file = client.files.upload(file=audio_path)

        print("=" * 50)
        print("Audio uploaded successfully")
        print("File Name:", uploaded_file.name)
        print("Initial State:", uploaded_file.state.name)
        print("=" * 50)

        # Wait for Gemini to process the file
        for attempt in range(30):

            uploaded_file = client.files.get(name=uploaded_file.name)

            print(f"Attempt {attempt + 1}")
            print("Current State:", uploaded_file.state.name)

            if uploaded_file.state.name == "ACTIVE":
               print("File is ACTIVE!")
               break

            if uploaded_file.state.name == "FAILED":
               raise Exception("Gemini failed to process the uploaded file.")

            time.sleep(2)

        else:
            raise Exception("Timed out waiting for Gemini to process the file.")

    # Generate pronunciation evaluation
        response = client.models.generate_content(
           model="gemini-2.5-flash",
           contents=[
              uploaded_file,
              prompt
           ]
       )

    text = response.text.strip()

      # Delete uploaded file from Gemini
    client.files.delete(name=uploaded_file.name)

      # Remove markdown if Gemini returns it
    text = (
    text.replace("```json", "")
        .replace("```", "")
        .strip()
)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
         return {
        "error": "Gemini returned invalid JSON.",
        "raw_response": text
    }

    except Exception as e:
        return {
        "error": str(e)
    }