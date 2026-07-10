const audioInput = document.getElementById("audioFile");
const audioPlayer = document.getElementById("audioPlayer");

const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const fileDuration = document.getElementById("fileDuration");

const analyzeBtn = document.getElementById("analyzeBtn");

const loading = document.getElementById("loading");
const results = document.getElementById("results");

analyzeBtn.disabled = true;

// --------------------
// File Selection
// --------------------

audioInput.addEventListener("change", function () {
  const file = this.files[0];

  if (!file) return;

  fileName.textContent = file.name;

  fileSize.textContent =
    "Size : " + (file.size / (1024 * 1024)).toFixed(2) + " MB";

  const url = URL.createObjectURL(file);

  audioPlayer.src = url;

  const audio = new Audio(url);

  audio.addEventListener("loadedmetadata", () => {
    const duration = Math.floor(audio.duration);

    fileDuration.textContent = "Duration : " + duration + " seconds";

    if (duration < 30 || duration > 45) {
      alert("Audio duration must be between 30 and 45 seconds.");

      analyzeBtn.disabled = true;

      return;
    }

    analyzeBtn.disabled = false;
  });
});

// --------------------
// Upload & Analyze
// --------------------

analyzeBtn.addEventListener("click", async () => {
  const file = audioInput.files[0];

  if (!file) {
    alert("Please select an audio file.");

    return;
  }

  const formData = new FormData();

  formData.append("file", file);

  loading.style.display = "block";

  results.style.display = "none";

  analyzeBtn.disabled = true;

  try {
    const response = await fetch(
      "https://pronunciation-ai-backend.onrender.com/upload-audio",
      {
        method: "POST",
        body: formData,
      },
    );

    const data = await response.json();

    loading.style.display = "none";

    analyzeBtn.disabled = false;

    if (!response.ok) {
      alert(data.detail || "Something went wrong.");

      return;
    }

    results.style.display = "grid";

    // --------------------
    // Score
    // --------------------

    document.getElementById("score").textContent =
      data.evaluation.overall_score;

    // --------------------
    // Transcript
    // --------------------

    document.getElementById("transcript").textContent = data.transcript;

    document.getElementById("correctedTranscript").textContent =
      data.corrected_transcript;

    // --------------------
    // Detailed Scores
    // --------------------

    document.getElementById("pronunciationScore").textContent =
      data.evaluation.pronunciation_score;

    document.getElementById("fluencyScore").textContent =
      data.evaluation.fluency_score;

    document.getElementById("clarityScore").textContent =
      data.evaluation.clarity_score;

    document.getElementById("pace").textContent = data.evaluation.pace;

    // --------------------
    // Mistakes
    // --------------------

    const mistakes = document.getElementById("mistakes");

    mistakes.innerHTML = "";

    if (data.evaluation.mispronounced_words.length === 0) {
      mistakes.innerHTML = "<li>No pronunciation mistakes detected.</li>";
    } else {
      data.evaluation.mispronounced_words.forEach((item) => {
        mistakes.innerHTML += `
                    <li>
                        <strong>${item.word}</strong><br>
                        <b>Severity:</b> ${item.severity}<br>
                        <b>Issue:</b> ${item.issue}<br>
                        <b>Tip:</b> ${item.tip}
                    </li>
                `;
      });
    }

    // --------------------
    // Strengths
    // --------------------

    const strengths = document.getElementById("strengths");

    strengths.innerHTML = "";

    data.evaluation.strengths.forEach((item) => {
      strengths.innerHTML += `<li>${item}</li>`;
    });

    // --------------------
    // Suggestions
    // --------------------

    const suggestions = document.getElementById("suggestions");

    suggestions.innerHTML = "";

    data.evaluation.suggestions.forEach((item) => {
      suggestions.innerHTML += `<li>${item}</li>`;
    });

    // --------------------
    // Overall Feedback
    // --------------------

    document.getElementById("overallFeedback").textContent =
      data.evaluation.overall_feedback;

    // --------------------
    // PDF Download
    // --------------------

    document.getElementById("downloadPdf").href = data.pdf_download_url;
  } catch (error) {
    loading.style.display = "none";

    analyzeBtn.disabled = false;

    alert("Unable to connect to backend.");

    console.error(error);
  }
});
