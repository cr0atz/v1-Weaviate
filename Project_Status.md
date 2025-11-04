# Project Status – v1-Weaviate

## Summary
- FastAPI backend + Streamlit UI using Weaviate for RAG-style retrieval and OpenAI for responses.
- Open-source release on GitHub with comprehensive documentation and CI.
- Domain: Australian Family Law (FLAST-AI).

## Current State
- **Repository**: Public on GitHub at https://github.com/cr0atz/v1-Weaviate
- **Version**: v0.1.0 (initial release)
- **Status**: Production-ready with secure auth and pinned dependencies

## Milestones
- [x] Analyze repository and stack
- [x] Create comprehensive documentation (README, INSTALL, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT)
- [x] Add Project Status document
- [x] Add .gitignore for Python/venv/datasets/secrets
- [x] Add GitHub Actions CI workflow (Markdown/YAML lint, Python smoke checks)
- [x] Initialize git repository and create initial commit
- [x] Pin runtime dependencies in requirements.txt
- [x] Rotate auth token from hardcoded to API_AUTH_TOKEN in .env
- [x] Push to GitHub as public repository
- [x] Tag v0.1.0 release
- [ ] Define Weaviate schema and migration script
- [ ] Add unit tests for FastAPI endpoints
- [ ] Implement retrieval evaluation set
- [ ] Add observability (structured logging, metrics)

## Key Decisions
- Default branch: `main`
- License: MIT
- Auth: `API_AUTH_TOKEN` from `.env` (secure, rotatable) ✅
- Config: `.env` for secrets and endpoints
- Open source: Public repository to support community exploring RAG + Weaviate

## Completed Improvements
- ✅ Pinned all runtime dependencies with versions
- ✅ Replaced hardcoded auth token with environment variable
- ✅ Added release documentation (LICENSE, CHANGELOG, RELEASE_NOTES, VERSION)
- ✅ Created INSTALL.md for Ubuntu + Apache deployment
- ✅ Added RULES.md for development workflow
- ✅ Created memory/ARCHITECTURE.md for codebase overview
- ✅ Removed secrets from git history

## Remaining Risks
- Weaviate schema not versioned or documented (class `AI_v1` assumptions)
- No automated tests for API endpoints or retrieval quality
- Ingestion pipeline embedded in Streamlit (needs CLI refactor)
- Legacy OpenAI SDK patterns in Upload_Data.py

## Next Actions (Priority Order)
1. Define and version Weaviate schema with migration script
2. Implement API key header auth (replace payload-based auth)
3. Create ingestion CLI for TXT/PDF with metadata extraction
4. Update prompts for Australian Family Law domain specificity
5. Add pytest unit tests and retrieval evaluation set
6. Implement structured logging and request tracing
7. Strengthen CI with linting (ruff/black) and type checking (mypy)
