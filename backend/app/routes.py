from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import os

from app.utils import save_uploaded_file, get_audio_duration
from app.ai import transcribe_audio
from app.gemini import evaluate_pronunciation

from fastapi.responses import FileResponse
from app.pdf_generator import generate_pdf

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "OK"}


@router.post("/upload-audio")
async def upload_audio(
    request: Request,
    file: UploadFile = File(...)
):
    print("Filename:", file.filename)
    print("Content-Type:", file.content_type)

    # Save uploaded file
    file_path = save_uploaded_file(file)

    # Get audio duration
    duration = get_audio_duration(file_path)

    if duration is None:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="Unable to read audio duration."
        )

    # Assignment requirement
    if duration < 30 or duration > 45:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="Audio duration must be between 30 and 45 seconds."
        )

    # Convert speech to text
    result = transcribe_audio(file_path)

    # Reject non-English audio
    if result["language"] != "en":
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="Please upload an English audio file."
        )

    print("Detected language:", result["language"])
    print("Transcript:", result["transcript"])

    # Gemini evaluation
    evaluation = evaluate_pronunciation(
    file_path,
    result["transcript"])

    pdf_path = generate_pdf(
    filename=file.filename,
    duration=round(duration, 2),
    language=result["language"],
    transcript=result["transcript"],
    corrected_transcript=evaluation["corrected_transcript"],
    evaluation=evaluation
)

    # Delete uploaded file after processing
    if os.path.exists(file_path):
       os.remove(file_path)

    return {
    "message": "Audio evaluated successfully",
    "filename": file.filename,
    "duration": round(duration, 2),
    "language": result["language"],
    "transcript": result["transcript"],
    "corrected_transcript": evaluation["corrected_transcript"],
   "pdf_download_url": (
    f"{request.base_url}download-report/"
    f"{os.path.basename(pdf_path)}"
),
    "evaluation": {
        "overall_score": evaluation["overall_score"],
        "pronunciation_score": evaluation["pronunciation_score"],
        "fluency_score": evaluation["fluency_score"],
        "clarity_score": evaluation["clarity_score"],
        "pace": evaluation["pace"],
        "mispronounced_words": evaluation["mispronounced_words"],
        "strengths": evaluation["strengths"],
        "suggestions": evaluation["suggestions"],
        "overall_feedback": evaluation["overall_feedback"]
    }
}
@router.get("/download-report/{filename}")
def download_report(filename: str):

    file_path = os.path.join("reports", filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )