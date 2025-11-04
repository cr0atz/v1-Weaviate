# v1-Weaviate

FastAPI backend + Streamlit UI that queries a Weaviate vector database and uses OpenAI to generate answers
and reasoning.

## Open Source Announcement

We're excited to open source an early version of FLAST-AI v1-Weaviate. By sharing this project publicly,
we hope it helps others exploring hybrid search with Weaviate and LLM-backed reasoning.
Contributions and feedback are welcome.

## Overview
- Backend: FastAPI app (`Main.py`) exposing `/` and `/generate_answers/`.
- Vector DB: Weaviate client querying class `AI_v1` with hybrid search.
- LLM: OpenAI Chat Completions (e.g., `gpt-4o`).
- Frontend: Streamlit page (`pages/Question_Answer.py`) posting to the API and displaying answers,
  reasoning, context, and case name.
- Prompts: `prompts/prompt.txt` and `prompts/reasoning_prompt.txt` used to shape responses.

## Requirements
- Python 3.10+
- Weaviate instance (defaults to `http://localhost:8080` in the code)
- OpenAI API key

Current `requirements.txt` includes only core libs used elsewhere (tensorflow/grpc). You will likely also need the following for local dev:
- `fastapi`, `uvicorn`
- `weaviate-client`
- `python-dotenv`
- `openai`
- `transformers`
- `beautifulsoup4`
- `streamlit`
- `requests`

You can install these explicitly if they are not present in your environment.

## Setup
1. Create and activate a virtual environment (recommended):
```
python3 -m venv venv
source venv/bin/activate
```
2. Install dependencies:
```
pip install -r requirements.txt || true
pip install fastapi uvicorn weaviate-client python-dotenv openai transformers beautifulsoup4 streamlit requests
```
3. Set environment variables (create a `.env` file in project root):
```
OPENAI_API_KEY=sk-...            # required
WEAVIATE_API=http://localhost:8080  # optional; code defaults to localhost
API_ENDPOINT=http://127.0.0.1:8000/generate_answers/  # used by Streamlit UI
API_AUTH_TOKEN=<your-secure-token>  # required; generate with: openssl rand -hex 32
```

## Running locally
- Start the FastAPI server:
```
uvicorn Main:app --reload --port 8000
```
- Open the interactive docs:
```
http://127.0.0.1:8000/docs
```
- Start the Streamlit UI:
```
streamlit run pages/Question_Answer.py
```

## API
- `POST /generate_answers/`
  - body: `{ "user_question": str, "user_model": str, "user_auth": str }`
  - returns: `{ answer, context, reasoning, case_name }`

Notes:
- The backend reads prompts from the `prompts/` folder.
- Weaviate class `AI_v1` is expected to have properties: `data`, `case_name`, and `_additional { score }` in the query.
- `user_auth` must match the `API_AUTH_TOKEN` set in `.env` (secure, rotatable).

## Development Notes
- The app loads environment variables via `python-dotenv`.
- Tokenization uses `transformers` GPT2 tokenizer.
- Model defaults to `gpt-4o` but is passed from the client payload.
- Adjust Weaviate URL via `.env` or directly in `Main.py`.

## Project Structure
```
/ (root)
├─ Main.py
├─ Home.py
├─ pages/
│  ├─ Question_Answer.py
│  └─ Upload_Data.py (if used)
├─ prompts/
│  ├─ prompt.txt
│  └─ reasoning_prompt.txt
├─ dataset/            # local data artifacts
├─ cache_dir/          # local cache
├─ requirements.txt
├─ .env                # not committed
└─ venv/               # local virtualenv (not committed)
```

## Troubleshooting
- 401 Unauthorized from API: The `user_auth` must match the expected token in `Main.py`.
- Missing dependency: Install the additional packages listed above.
- Weaviate query errors: Ensure the `AI_v1` class, properties, and schema are present and the server is reachable.

## Next Steps
- Harden auth (remove hardcoded token, use proper authN/Z).
- Add proper dependency pins for all Python libs in `requirements.txt`.
- Add tests around the FastAPI endpoints and Weaviate integration.
- Parameterize Weaviate URL via `.env`.
