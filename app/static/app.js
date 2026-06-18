const exampleMessages = [
  "I cannot log in to Passport York.",
  "Duo is not working on my new phone.",
  "I need access to a shared mailbox.",
  "I think I clicked a phishing email.",
  "I need software installed for my team.",
  "My laptop will not connect to Wi-Fi.",
];

const textarea = document.getElementById("message");
const submitBtn = document.getElementById("submit-btn");
const clearBtn = document.getElementById("clear-btn");
const statusEl = document.getElementById("status");
const resultCard = document.getElementById("result-card");
const resultFields = document.getElementById("result-fields");
const rawJson = document.getElementById("raw-json");
const examplesContainer = document.getElementById("examples");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#9a1b1f" : "#5c5a57";
}

function renderExamples() {
  exampleMessages.forEach((msg) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "example-btn";
    button.textContent = msg;
    button.addEventListener("click", () => {
      textarea.value = msg;
      textarea.focus();
    });
    examplesContainer.appendChild(button);
  });
}

function toLabel(key) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function renderResult(data) {
  resultFields.innerHTML = "";

  Object.entries(data).forEach(([key, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = toLabel(key);

    const dd = document.createElement("dd");
    if (Array.isArray(value)) {
      dd.textContent = value.length ? value.join(", ") : "—";
    } else if (value === null || value === "") {
      dd.textContent = "—";
    } else {
      dd.textContent = String(value);
    }

    resultFields.append(dt, dd);
  });

  rawJson.textContent = JSON.stringify(data, null, 2);
  resultCard.hidden = false;
}

async function classifyMessage() {
  const message = textarea.value.trim();
  if (!message) {
    setStatus("Please enter a message before classifying.", true);
    return;
  }

  submitBtn.disabled = true;
  setStatus("Classifying request...");

  try {
    const response = await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (!response.ok) {
      const detail = data?.detail ? JSON.stringify(data.detail) : "Unexpected error";
      throw new Error(`Request failed (${response.status}): ${detail}`);
    }

    renderResult(data);
    setStatus("Classification complete.");
  } catch (error) {
    setStatus(error.message || "Unable to classify request right now.", true);
  } finally {
    submitBtn.disabled = false;
  }
}

submitBtn.addEventListener("click", classifyMessage);
clearBtn.addEventListener("click", () => {
  textarea.value = "";
  setStatus("");
  resultCard.hidden = true;
  textarea.focus();
});

textarea.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    classifyMessage();
  }
});

renderExamples();
