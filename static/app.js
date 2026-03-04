const form = document.getElementById("form");
const resultEl = document.getElementById("result");
const errorEl = document.getElementById("error");
const btn = document.getElementById("btn");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.style.display = "none";
  resultEl.style.display = "none";
  const problem = document.getElementById("problem").value.trim();
  const topic = document.getElementById("topic").value.trim() || null;
  const grade = document.getElementById("grade").value;
  const apiKey = document.getElementById("apikey").value || "dev-key-change-in-production";

  btn.disabled = true;
  try {
    const res = await fetch("/v1/score", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({
        problem_text: problem,
        topic: topic || null,
        grade_level: grade ? parseInt(grade, 10) : null,
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      errorEl.textContent = data.detail || res.statusText || "Request failed";
      errorEl.style.display = "block";
      return;
    }
    renderResult(data);
    resultEl.style.display = "block";
  } catch (err) {
    errorEl.textContent = err.message || "Network error";
    errorEl.style.display = "block";
  } finally {
    btn.disabled = false;
  }
});

function renderResult(r) {
  const diffClass = r.difficulty === "easy" ? "easy" : r.difficulty === "hard" ? "hard" : "medium";
  const qualityPct = Math.round((r.quality_score || 0) * 100);
  const diffPct = Math.round((r.difficulty_score || 0) * 100);
  const answer = r.answer || {};
  const steps = (answer.steps || []).length ? `<ul>${answer.steps.map(s => `<li>${escapeHtml(s)}</li>`).join("")}</ul>` : "";

  resultEl.innerHTML = `
    <h3>Difficulty</h3>
    <span class="badge ${diffClass}">${r.difficulty}</span>
    <div class="score-bar"><span style="width:${diffPct}%"></span></div>
    <small>${r.readability_notes || ""}</small>

    <h3 style="margin-top:1rem">Quality</h3>
    <div class="score-bar"><span style="width:${qualityPct}%"></span></div>
    <small>${r.quality_factors?.length_ok ? "✓ Length OK" : ""} ${r.quality_factors?.has_question_mark ? "✓ Clear question" : ""}</small>

    ${r.topic_match ? `<h3 style="margin-top:1rem">Topic</h3><p>${escapeHtml(r.topic_match)}</p>` : ""}

    <h3 style="margin-top:1rem">Answer</h3>
    <div class="answer-box">${escapeHtml(answer.answer_text || "—")}</div>
    ${steps}
  `;
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}
