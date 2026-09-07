# Deploying the Web App (Frontend + Backend)

This project can run two ways:
- **CLI mode** (original): `chat_app.py` / `ai_chat.py`, two terminals, no web server.
- **Web mode** (this guide): a FastAPI backend + a browser frontend, so anyone can watch the Philosopher/Scientist conversation live in a browser, hosted for free.

Web mode reuses the exact same `AIChatService` / `GeminiResponder` / `RedisQueueService` classes the CLI uses — the backend ([api/](api)) is just a new, thin adapter on top (see [README.md](README.md) for the architecture).

You need three free-tier services:

| Piece | Where | Why |
|---|---|---|
| Redis | [Upstash](https://upstash.com) | Local Docker Redis isn't reachable from the internet — the deployed backend needs a Redis it can reach over the network. |
| Backend | [Render](https://render.com) | Runs `api/app.py` (FastAPI) via the included `Dockerfile`. |
| Frontend | [Vercel](https://vercel.com) or [Netlify](https://netlify.com) | Serves the static files in [frontend/](frontend). |

---

## 1. Redis — Upstash (free)

1. Sign up at https://upstash.com (no credit card required for the free tier).
2. Create a new **Redis** database (any region close to where you'll deploy the backend).
3. On the database page, copy the **"Redis URL"** — it looks like:
   ```
   rediss://default:AbC123...@some-name.upstash.io:6379
   ```
4. Keep this URL — you'll paste it into Render as `REDIS_URL` in the next step.

## 2. Backend — Render (free)

1. Push this repo to GitHub if you haven't already (`git push`).
2. Go to https://dashboard.render.com → **New** → **Blueprint**.
3. Connect your GitHub account and select this repository. Render will detect [render.yaml](render.yaml) automatically.
4. When prompted for environment variables, set:
   - `GEMINI_API_KEY` → your free key from https://aistudio.google.com/apikey
   - `REDIS_URL` → the Upstash URL from step 1
   - `FRONTEND_ORIGINS` → leave blank for now (you'll set this after deploying the frontend in step 3)
5. Click **Apply**. Render builds the [Dockerfile](Dockerfile) and deploys it.
6. Once live, copy the backend's public URL (something like `https://redis-ai-chat-backend.onrender.com`).
7. Verify it's working: open `https://<your-backend-url>/api/health` in a browser — you should see `{"status":"ok"}`.

> **Free tier note:** Render's free web services spin down after periods of inactivity and take ~30-60s to wake back up on the next request. This is normal — just wait for the first request to complete.

## 3. Frontend — Vercel (free)

1. Edit [frontend/config.js](frontend/config.js) and set:
   ```js
   const BACKEND_URL = "https://<your-backend-url>.onrender.com";
   ```
   Commit and push this change.
2. Go to https://vercel.com → **Add New** → **Project** → import this same GitHub repo.
3. When configuring the project, set **Root Directory** to `frontend`. No build command is needed — it's plain HTML/CSS/JS.
4. Deploy. Vercel gives you a URL like `https://your-app.vercel.app`.
5. Go back to Render, open your backend service → **Environment**, and set:
   ```
   FRONTEND_ORIGINS=https://your-app.vercel.app
   ```
   This locks down CORS so only your deployed frontend can call the backend. Save — Render redeploys automatically.

*(Netlify works the same way: point it at the `frontend` folder, no build command, no framework.)*

## 4. Try it

Open your Vercel/Netlify URL. You should see "Connected - ready to start a conversation". Type a topic and click **Start Conversation** — the Philosopher and Scientist will start talking, streamed live over WebSocket.

---

## Running the web app locally (before deploying)

```bash
docker start redis-pubsub   # or: docker run -d --name redis-pubsub -p 6379:6379 redis
python -m uvicorn api.app:app --reload --port 8000
```

Then just open [frontend/index.html](frontend/index.html) directly in your browser (`config.js` already points at `http://localhost:8000`).
