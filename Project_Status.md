# Project Status – v1-Weaviate

## Summary
- FastAPI backend + Streamlit UI using Weaviate for RAG-style retrieval and OpenAI for responses.
- Docs and CI being added to make the repo development-ready.

## Current State
- README created with setup, run, and troubleshooting.
- CI to lint docs/YAML and run Python checks will be added.
- .gitignore to exclude virtualenv, caches, and datasets will be added.

## Milestones
- [x] Analyze repository and stack
- [x] Create README
- [ ] Add Project Status document
- [ ] Add .gitignore
- [ ] Add basic CI workflow
- [ ] Initialize git and create initial commit
- [ ] Define first development tasks (tests, auth hardening, config)

## Key Decisions
- Default branch: `main`
- Auth: temporary token in code; to be replaced with proper auth
- Config: `.env` for secrets and endpoints

## Risks
- Missing dependency pins for many Python packages
- Hardcoded auth token
- Weaviate schema assumptions (class `AI_v1` with fields `data`, `case_name`)

## Next Actions
- Add .gitignore and CI workflow
- Initialize git and commit
- Add tests for FastAPI endpoints and Weaviate integration (mock where possible)
- Improve configuration and secrets handling
