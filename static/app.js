const form = document.getElementById("form");
const messagesEl = document.getElementById("messages");
const errorEl = document.getElementById("error");
const problemEl = document.getElementById("problem");
const topicEl = document.getElementById("topic");
const btn = document.getElementById("btn");

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

function appendMessage(role, content) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = escapeHtml(content);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function appendTeacherMessage(data) {
  const wrap = document.createElement("div");
  wrap.className = "msg teacher";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = `
    <div class="block"><span class="label">Answer</span><div>${escapeHtml(data.answer || "—")}</div></div>
    <div class="block"><span class="label">Difficulty</span><div>${escapeHtml(data.difficulty || "—")}</div></div>
    <div class="block"><span class="label">Relevance to topic</span><div>${escapeHtml(data.relevance_to_topic || "—")}</div></div>
    <div class="block"><span class="label">Explanation</span><div>${escapeHtml(data.explanation || "—")}</div></div>
  `;
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.style.display = "none";
  const problem = problemEl.value.trim();
  const topic = topicEl.value.trim() || null;

  appendMessage("user", problem + (topic ? `\nTopic: ${topic}` : ""));

  problemEl.value = "";
  btn.disabled = true;

  try {
    const res = await fetch("/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem_text: problem, topic }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      errorEl.textContent = data.detail || res.statusText || "Request failed";
      errorEl.style.display = "block";
      appendTeacherMessage({
        answer: "—",
        difficulty: "—",
        relevance_to_topic: "—",
        explanation: "Sorry, something went wrong. Try again.",
      });
      return;
    }
    appendTeacherMessage(data);
  } catch (err) {
    errorEl.textContent = err.message || "Network error";
    errorEl.style.display = "block";
    appendTeacherMessage({
      answer: "—",
      difficulty: "—",
      relevance_to_topic: "—",
      explanation: "Could not reach the server. Check your connection.",
    });
  } finally {
    btn.disabled = false;
  }
});
