# Architecture Overview

## Components
- **FastAPI backend (Main.py)**
  - Exposes `/` and `POST /generate_answers/`.
  - Loads `.env` via `python-dotenv`.
  - Connects to Weaviate (default `http://localhost:8080`).
  - Reads prompts from `prompts/`.
  - Uses OpenAI Chat Completions to produce `answer` and `reasoning`.

- **Weaviate (Vector DB)**
  - Queried with hybrid search over class `AI_v1`.
  - Expects properties: `data`, `case_name` and uses `_additional { score }`.

- **Streamlit UI (pages/Question_Answer.py, Home.py)**
  - UI form posts to FastAPI `API_ENDPOINT` from `.env`.
  - Displays `answer`, `reasoning`, `context`, `case_name`.
  - `Home.py` routes to pages via `switch_page`.

- **Data ingestion (pages/Upload_Data.py)**
  - Uploads text files and indexes into Weaviate.
  - Cleans/normalizes text, tokenizes with GPT2, batches into chunks.
  - Uses OpenAI Embeddings (text-embedding-ada-002) to generate vectors (legacy OpenAI Embeddings API).

- **Prompts (prompts/)**
  - `prompt.txt`: system guidance for answer generation.
  - `reasoning_prompt.txt`: system guidance for reasoning/fact-check and scoring.

## Key Environment Variables
- `OPENAI_API_KEY`: required.
- `WEAVIATE_API`: optional; code currently defaults to `http://localhost:8080`.
- `API_ENDPOINT`: used by Streamlit UI to call FastAPI.
- `API_AUTH_TOKEN`: required; used for API authentication (replaces hardcoded token).

## Notable Behaviors
- `Main.py` picks top Weaviate hit by `_additional.score` and feeds `data` into LLM prompts.
- Auth: payload `user_auth` must match `API_AUTH_TOKEN` from `.env` (secure, rotatable).
- Tokenization via `transformers` GPT2 tokenizer determines chunking logic in ingestion.

## Risks / Gaps
- Auth token now secure via `.env` (✅ resolved).
- `requirements.txt` missing many runtime deps (use `requirements.txt.old` as reference and pin versions).
- Unused/legacy patterns (e.g., older OpenAI embeddings usage in `Upload_Data.py`).
- Weaviate schema assumptions may not match deployed instance.

## CI & Docs
- GitHub Actions: lint Markdown/YAML and Python smoke checks.
- Docs: README, INSTALL (Ubuntu + Apache), CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, RELEASE_NOTES, VERSION.
