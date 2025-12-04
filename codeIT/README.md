# CodeIT AI Assistant

AI assistant for CodeIT Institute of Nepal featuring semantic search, Groq LLM fallback, a FastAPI backend, and a polished React chat experience.

## Requirements

- Python 3.10+
- Node.js 18+
- Groq API key (optional, unlocks LLM fallback)

## Backend (FastAPI)

1. Create a virtual environment:
	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```
2. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```
3. Provide a `.env` file in the project root if you intend to call Groq:
	```env
	GROQ_API_KEY=your-key-here
	```
4. Run the API:
	```powershell
	uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
	```

Key endpoints:

- `GET /health` – liveness probe.
- `POST /chat` – accepts `{ "message": "...", "session_id": "optional" }` and returns the assistant reply plus rolling history.

## Frontend (React + Vite)

1. Install dependencies:
	```powershell
	cd frontend
	npm install
	```
2. (Optional) Point to a different API base:
	```powershell
	echo VITE_API_BASE_URL=http://localhost:8000 > .env.local
	```
3. Start the dev server:
	```powershell
	npm run dev
	```

The UI runs on `http://localhost:5173` and communicates with the FastAPI backend. Conversation history stays within the chat session and is cached locally for convenience.

## Project Structure

```
backend/
  app.py          # FastAPI application
  schemas.py      # Pydantic request/response models
chatbot.py        # Core rule + retrieval-based chatbot logic
utils.py          # Embedding helpers and semantic search utilities
kbuilder.py       # Knowledge-base text construction from dataset
llm.py            # Groq LLM fallback integration
frontend/         # React single-page application
```

## Dataset & Embeddings

- `codeit_dataset.json` – curated institute content powering deterministic answers.
- `kb_texts.json` / `kb_embeddings.npy` – cached semantic search data (auto-generated on first run).

## Testing Checklist

- Verify `/health` returns `{"status": "ok"}` while the API is running.
- Chat through the web UI and confirm history persists locally across refreshes.
- Trigger Groq fallback by asking niche questions when an API key is configured.
