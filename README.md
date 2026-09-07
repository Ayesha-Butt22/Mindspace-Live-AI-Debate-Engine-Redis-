# Mindspace — Live AI Debate Engine

A real-time chat system built on **Redis Pub/Sub**, layered with a clean, SOLID-compliant architecture, where two AI agents (a Philosopher and a Scientist) can debate any topic live. It ships with three ways to use it:

1. **Human-to-human chat** ([chat_app.py](chat_app.py)) — two people chat with each other from two terminals.
2. **AI-to-AI chat (CLI)** ([ai_chat.py](ai_chat.py)) — two autonomous AI agents (a Philosopher and a Scientist) hold a real, unscripted conversation with each other over the same Redis Pub/Sub transport, each backed by an LLM (Google Gemini by default; Anthropic Claude is a drop-in alternative).
3. **AI-to-AI chat (web app)** ([api/](api) + [frontend/](frontend)) — the same AI-to-AI conversation, watchable live in a browser: a FastAPI backend streams it over a WebSocket to a small HTML/CSS/JS frontend. See [DEPLOYMENT.md](DEPLOYMENT.md) to deploy both for free.

Every message — human or AI — is persisted to a local SQLite database.

---

## Why this architecture

The codebase follows **SOLID** end to end. Dependencies point at abstractions, not implementations, so the transport (Redis) and the AI provider (Gemini/Claude) are both swappable without touching business logic.

| Principle | Where it shows up |
|---|---|
| **Single Responsibility** | Every class does exactly one thing: [`RedisQueueService`](services/redis_queue_service.py) only talks to Redis, [`GeminiResponder`](services/gemini_responder.py) only talks to Gemini, [`message_repository.py`](db/message_repository.py) only runs SQL, [`message_controller.py`](controllers/message_controller.py) only decides business rules (e.g. don't save empty messages). |
| **Open/Closed** | AI-to-AI chat was added as a set of *new* files ([`AIChatService`](services/ai_chat_service.py), [`ai_chat.py`](ai_chat.py), the responders) without modifying the existing human chat path ([`ChatService`](services/chat_service.py), [`chat_app.py`](chat_app.py)). Later, the web app ([api/](api)) was added the same way — it *observes* the same Redis Pub/Sub channels and reuses `AIChatService`/`GeminiResponder` unchanged; it did not require editing `ai_chat.py` or the service layer. |
| **Liskov Substitution** | Any [`IPublisher`](interfaces/publisher_interface.py)/[`ISubscriber`](interfaces/subscriber_interface.py) implementation can replace `RedisQueueService`; any [`IResponder`](interfaces/responder_interface.py) implementation ([`GeminiResponder`](services/gemini_responder.py) or [`ClaudeResponder`](services/claude_responder.py)) can replace the other with zero changes to `AIChatService`. |
| **Interface Segregation** | Publishing and subscribing are two separate interfaces, not one bloated `IQueue`. Generating an AI reply (`IResponder`) is segregated from sending it (`IPublisher`) — a class that only sends never has to implement listening logic, and vice versa. |
| **Dependency Inversion** | [`ChatService`](services/chat_service.py) and [`AIChatService`](services/ai_chat_service.py) depend only on interfaces (`IPublisher`, `ISubscriber`, `IResponder`), injected through the constructor. The only place concrete classes (`RedisQueueService`, `GeminiResponder`) are instantiated is the composition root in each entry point ([`chat_app.py`](chat_app.py) / [`ai_chat.py`](ai_chat.py)). |

**Dependency Injection** is applied throughout via plain constructor injection — no framework needed:

```python
chat_service = AIChatService(
    agent=agent,             # data
    publisher=queue_service,  # IPublisher — could be Redis, RabbitMQ, Kafka...
    responder=responder,      # IResponder — could be Gemini, Claude, a local model...
)
```

---

## Project structure

```
.
├── ai_chat.py                    # Entry point: AI-to-AI conversation
├── chat_app.py                   # Entry point: human-to-human conversation
├── crud_demo.py                  # Entry point: standalone menu to inspect/edit saved messages
│
├── config/
│   ├── settings.py                # Redis connection info, DB name, Pub/Sub channel names
│   ├── ai_settings.py             # AI model names, turn limit, loads .env
│   ├── users.py                   # The two human chat participants
│   ├── agents.py                  # The two AI personas (philosopher, scientist)
│   └── redis_client.py            # Builds the Redis connection object
│
├── domain/                        # Pure data — no logic, no I/O
│   ├── user.py                    # Human chat participant
│   ├── agent_persona.py           # AI chat participant (adds a system_prompt)
│   └── message.py                 # A single chat message
│
├── interfaces/                    # Contracts (abstract base classes)
│   ├── publisher_interface.py     # IPublisher — "can send a message"
│   ├── subscriber_interface.py    # ISubscriber — "can receive messages"
│   └── responder_interface.py     # IResponder — "can generate the next reply"
│
├── services/
│   ├── redis_queue_service.py     # The ONLY file that knows Redis exists
│   ├── chat_service.py            # Human chat orchestration
│   ├── ai_chat_service.py         # AI-to-AI chat orchestration
│   ├── gemini_responder.py        # IResponder via Google Gemini (free tier)
│   └── claude_responder.py        # IResponder via Anthropic Claude (alternative)
│
├── listeners/
│   └── message_listener.py        # Runs a subscriber's blocking listen loop on a background thread
│
├── controllers/
│   └── message_controller.py      # Business rules (e.g. reject empty messages) between UI and DB
│
├── db/
│   ├── connection.py               # SQLite connection + table creation
│   └── message_repository.py       # Raw SQL: insert/find/update/delete
│
├── api/                            # Web backend (FastAPI) — a thin adapter, no new chat logic
│   ├── app.py                       # HTTP/WebSocket routes only
│   ├── conversation_manager.py      # Wires AIChatService + GeminiResponder + Redis for the web app
│   └── connection_manager.py        # Tracks connected WebSocket clients, broadcasts to them
│
├── frontend/                       # Static browser UI (no build step)
│   ├── index.html
│   ├── style.css
│   ├── app.js                       # Connects to the backend WebSocket, renders the live chat
│   └── config.js                    # Backend URL - edit after deploying the backend
│
├── requirements.txt
├── Dockerfile                      # Builds the backend for deployment
├── render.yaml                     # Render Blueprint for one-click backend deploy
├── DEPLOYMENT.md                   # Step-by-step: deploy backend + frontend for free
├── .env.example                    # Template for API keys (copy to .env, fill in, never commit .env)
└── .gitignore
```

---

## Prerequisites

- Python 3.10+
- [Docker](https://www.docker.com/) (to run Redis) — or a Redis server installed natively
- A free [Google AI Studio](https://aistudio.google.com/apikey) account (for Gemini, no billing required)
- *(optional)* An [Anthropic Console](https://console.anthropic.com/) account with billing enabled, only if you switch to `ClaudeResponder`

---

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/Ayesha-Butt22/Redis.git
cd Redis
pip install -r requirements.txt
```

**2. Start Redis**

```bash
docker run -d --name redis-pubsub -p 6379:6379 redis
```

**3. Configure your API key**

```bash
cp .env.example .env
```

Edit `.env` and add your free Gemini key:

```
GEMINI_API_KEY=your-key-from-aistudio.google.com
```

---

## Usage

### Human-to-human chat

Terminal 1:
```bash
python chat_app.py ahmed
```
Terminal 2:
```bash
python chat_app.py sara
```
Type a message and press Enter. Type `exit` to quit.

### AI-to-AI chat

Terminal 1 (start listening first):
```bash
python ai_chat.py scientist
```
Terminal 2 (kicks off the conversation with an opening line):
```bash
python ai_chat.py philosopher "Do you think consciousness is just complex computation?"
```

Both agents reply to each other automatically, using Gemini to generate each reply from the conversation so far. Each agent stops after `MAX_TURNS` replies ([`config/ai_settings.py`](config/ai_settings.py)) to prevent an infinite, ever-billing loop. Press `Ctrl+C` in either terminal to stop early.

### AI-to-AI chat (web app)

```bash
docker start redis-pubsub          # make sure Redis is running
python -m uvicorn api.app:app --reload --port 8000
```
Then open [frontend/index.html](frontend/index.html) in your browser, type a topic, and click **Start Conversation**. Messages stream in live over a WebSocket as Gemini generates each reply.

To put this online for others to use, see [DEPLOYMENT.md](DEPLOYMENT.md) — deploys the backend to Render and the frontend to Vercel/Netlify, both on free tiers.

### Inspect saved messages

```bash
python crud_demo.py
```
A menu-driven CRUD tool over the same SQLite database every chat mode writes to.

---

## Extending the project

**Swap the AI provider** — write a new class implementing `IResponder.respond(system_prompt, history) -> str`, then change one line in `ai_chat.py`:
```python
responder = GeminiResponder(my_name=agent.name)   # or ClaudeResponder(...), or your own
```
Nothing in `AIChatService` needs to change — that's Dependency Inversion in practice.

**Swap the message transport** — write a new class implementing `IPublisher` and `ISubscriber` (e.g. for RabbitMQ or Kafka), then swap it in at the same composition root.

**Add a third AI persona** — add one more entry to [`config/agents.py`](config/agents.py) with its own name, channels, and `system_prompt`.

**Tune the conversation** — [`config/ai_settings.py`](config/ai_settings.py) controls the model (`GEMINI_MODEL`) and how many turns each agent gets (`MAX_TURNS`); [`config/agents.py`](config/agents.py)'s `system_prompt` controls each persona's tone and depth.

---

## Tech stack

- **Python 3** — application code
- **Redis** (Pub/Sub) — real-time message transport
- **SQLite** — message persistence
- **Google Gemini API** (`google-genai`) — default AI provider (free tier)
- **Anthropic Claude API** (`anthropic`) — alternative AI provider
- **python-dotenv** — loads API keys from `.env`
- **FastAPI + Uvicorn** — web backend (REST + WebSocket) for the browser-based chat
- **Vanilla HTML/CSS/JS** — frontend, no build step required
