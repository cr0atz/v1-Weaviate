# Contributing to v1-Weaviate

Thanks for contributing! This project uses FastAPI (backend), Streamlit (UI), Weaviate (vector DB), and OpenAI.

## Workflow
- Open an Issue or Draft PR to discuss non-trivial changes.
- Keep PRs focused and small.
- Update docs (`README.md`, `Project_Status.md`) as needed.

## Branching
- Default branch: `main`
- Feature branches: `feature/<topic>`
- Fix branches: `fix/<topic>`

## Commits
- Imperative style, short and descriptive.
- Conventional prefixes encouraged: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.

## Pull Requests
- Include context, approach, and testing notes.
- Add screenshots for UI changes.

## Code Style
- Python: follow PEP8; prefer clarity.
- Add tests for new behavior where practical.

## Environment & Secrets
- Use `.env` for `OPENAI_API_KEY`, `API_ENDPOINT`, and Weaviate URL.
- Do not commit secrets. `.env` is in `.gitignore`.

## Running Locally
- Backend: `uvicorn Main:app --reload --port 8000`
- UI: `streamlit run pages/Question_Answer.py`
- Docs: `http://127.0.0.1:8000/docs`

## CI
- GitHub Actions lints Markdown/YAML and runs Python smoke checks/tests.
