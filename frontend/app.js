const chatEl = document.getElementById("chat");
const emptyStateEl = document.getElementById("empty-state");
const statusEl = document.getElementById("status");
const statusLabelEl = statusEl.querySelector(".pill__label");
const formEl = document.getElementById("start-form");
const topicInputEl = document.getElementById("topic-input");
const startButtonEl = document.getElementById("start-button");
const chipEls = document.querySelectorAll(".chip");
const newDebateBtnEl = document.getElementById("new-debate-btn");
const newDebateIconEl = document.getElementById("new-debate-icon");
const surpriseBtnEl = document.getElementById("surprise-btn");
const historyIconEl = document.getElementById("history-icon");
const historyOverlayEl = document.getElementById("history-overlay");
const historyCloseEl = document.getElementById("history-close");
const historyListEl = document.getElementById("history-list");

const RANDOM_TOPICS = [
  "Is free will real, or just an illusion?",
  "Could human consciousness ever be fully explained by physics?",
  "Should we be afraid of superintelligent AI?",
  "Is time travel theoretically possible?",
  "Are we living in a simulation?",
  "Does objective morality exist, or is it a human invention?",
  "Can something come from nothing?",
  "Is mathematics discovered or invented?",
];

function setStatus(text, state) {
  // state is one of "pending" | "connected" | "disconnected"
  statusLabelEl.textContent = text;
  statusEl.className = `pill pill--${state}`;
}

function showChat() {
  emptyStateEl.hidden = true;
  chatEl.hidden = false;
}

function resetToEmptyState() {
  chatEl.innerHTML = "";
  chatEl.hidden = true;
  emptyStateEl.hidden = false;
  topicInputEl.value = "";
  topicInputEl.focus();
}

function appendMessage(sender, text) {
  showChat();

  const isPhilosopher = sender === "Philosopher";
  const bubble = document.createElement("div");
  bubble.className = "bubble " + (isPhilosopher ? "bubble--philosopher" : "bubble--scientist");

  const avatarEl = document.createElement("div");
  avatarEl.className = "bubble__avatar";
  avatarEl.textContent = isPhilosopher ? "🧠" : "🔬";

  const contentEl = document.createElement("div");
  contentEl.className = "bubble__content";

  const senderEl = document.createElement("div");
  senderEl.className = "bubble__sender";
  senderEl.textContent = sender;

  const textEl = document.createElement("div");
  textEl.className = "bubble__text";
  // Always textContent, never innerHTML - this is AI-generated text and
  // must never be interpreted as HTML/script.
  textEl.textContent = text;

  contentEl.appendChild(senderEl);
  contentEl.appendChild(textEl);
  bubble.appendChild(avatarEl);
  bubble.appendChild(contentEl);
  chatEl.appendChild(bubble);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function connectWebSocket() {
  const wsUrl = BACKEND_URL.replace(/^http/, "ws") + "/ws";
  const socket = new WebSocket(wsUrl);

  socket.onopen = () => setStatus("Connected", "connected");
  socket.onclose = () => {
    setStatus("Reconnecting...", "disconnected");
    setTimeout(connectWebSocket, 3000);
  };
  socket.onerror = () => socket.close();

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    appendMessage(data.sender, data.text);
  };
}

chipEls.forEach((chip) => {
  chip.addEventListener("click", () => {
    topicInputEl.value = chip.dataset.topic;
    topicInputEl.focus();
  });
});

surpriseBtnEl.addEventListener("click", () => {
  const topic = RANDOM_TOPICS[Math.floor(Math.random() * RANDOM_TOPICS.length)];
  topicInputEl.value = topic;
  topicInputEl.focus();
});

newDebateBtnEl.addEventListener("click", resetToEmptyState);
newDebateIconEl.addEventListener("click", resetToEmptyState);

historyIconEl.addEventListener("click", async () => {
  historyOverlayEl.hidden = false;
  historyListEl.innerHTML = "<div class=\"overlay__empty\">Loading...</div>";

  try {
    const response = await fetch(`${BACKEND_URL}/api/history`);
    const messages = await response.json();

    if (messages.length === 0) {
      historyListEl.innerHTML = "<div class=\"overlay__empty\">No messages saved yet.</div>";
      return;
    }

    historyListEl.innerHTML = "";
    messages
      .slice()
      .reverse()
      .forEach((message) => {
        const item = document.createElement("div");
        item.className = "overlay__item";

        const strong = document.createElement("strong");
        strong.textContent = message.sender + ": ";

        const textNode = document.createTextNode(message.content);

        item.appendChild(strong);
        item.appendChild(textNode);
        historyListEl.appendChild(item);
      });
  } catch (error) {
    historyListEl.innerHTML = "<div class=\"overlay__empty\">Could not load history.</div>";
  }
});

historyCloseEl.addEventListener("click", () => {
  historyOverlayEl.hidden = true;
});

historyOverlayEl.addEventListener("click", (event) => {
  if (event.target === historyOverlayEl) {
    historyOverlayEl.hidden = true;
  }
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const topic = topicInputEl.value.trim();
  if (!topic) return;

  chatEl.innerHTML = "";
  showChat();
  startButtonEl.disabled = true;

  try {
    await fetch(`${BACKEND_URL}/api/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
  } catch (error) {
    appendMessage("Scientist", `Could not reach the backend: ${error}`);
  } finally {
    startButtonEl.disabled = false;
  }
});

setStatus("Connecting", "pending");
connectWebSocket();
