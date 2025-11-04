# Release Notes

## v0.1.0 (2025-11-04)
Initial public open-source release of FLAST-AI v1-Weaviate.

Highlights:
- FastAPI backend with `/generate_answers/` endpoint and Weaviate hybrid search.
- Streamlit UI for interactive Q&A.
- Prompts-driven answer and reasoning generation via OpenAI.
- Docs: README, INSTALL, CONTRIBUTING, Project_Status, Code of Conduct, Security, Changelog, License.
- CI: Markdown/YAML lint and Python smoke checks.

Known items to improve next:
- Replace hardcoded `user_auth` with proper auth.
- Expand `requirements.txt` to include all runtime dependencies with pins.
- Add tests for API and Weaviate integration (mocked where possible).
