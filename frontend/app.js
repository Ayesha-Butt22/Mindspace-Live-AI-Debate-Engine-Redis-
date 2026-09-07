const chatEl = document.getElementById("chat");
const statusEl = document.getElementById("status");
const formEl = document.getElementById("start-form");
const topicInputEl = document.getElementById("topic-input");
const startButtonEl = document.getElementById("start-button");

function setStatus(text, connected) {
  statusEl.textContent = text;
  statusEl.className = connected ? "status status--connected" : "status status--disconnected";
}

function appendMessage(sender, text) {
  const bubble = document.createElement("div");
  bubble.className = "bubble " + (sender === "Philosopher" ? "bubble--philosopher" : "bubble--scientist");

  const senderEl = document.createElement("div");
  senderEl.className = "bubble__sender";
  senderEl.textContent = sender;

  const textEl = document.createElement("div");
  textEl.className = "bubble__text";
  textEl.textContent = text;

  bubble.appendChild(senderEl);
  bubble.appendChild(textEl);
  chatEl.appendChild(bubble);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function connectWebSocket() {
  const wsUrl = BACKEND_URL.replace(/^http/, "ws") + "/ws";
  const socket = new WebSocket(wsUrl);

  socket.onopen = () => setStatus("Connected - ready to start a conversation", true);
  socket.onclose = () => {
    setStatus("Disconnected - retrying in 3s...", false);
    setTimeout(connectWebSocket, 3000);
  };
  socket.onerror = () => socket.close();

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    appendMessage(data.sender, data.text);
  };
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const topic = topicInputEl.value.trim();
  if (!topic) return;

  chatEl.innerHTML = "";
  startButtonEl.disabled = true;

  try {
    await fetch(`${BACKEND_URL}/api/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
  } catch (error) {
    appendMessage("System", `Could not reach the backend: ${error}`);
  } finally {
    startButtonEl.disabled = false;
  }
});

connectWebSocket();
