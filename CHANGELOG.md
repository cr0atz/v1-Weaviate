# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [0.1.1] - 2025-11-04
### Security
- Replaced hardcoded auth token with `API_AUTH_TOKEN` environment variable
- Removed secrets from git history
- Added validation to ensure API_AUTH_TOKEN is configured

### Changed
- Updated Main.py to read auth token from .env
- Updated pages/Question_Answer.py to use API_AUTH_TOKEN
- Updated documentation to reflect secure auth approach

### Fixed
- Pinned all runtime dependencies with specific versions in requirements.txt
- Updated weaviate package from 0.1.0 to weaviate-client 4.7.1

## [0.1.0] - 2025-11-04
### Added
- Initial open-source release of FLAST-AI v1-Weaviate
- FastAPI backend with `/generate_answers/` endpoint
- Streamlit UI page for Q&A
- Weaviate hybrid search integration
- Documentation: README, INSTALL, CONTRIBUTING, Project_Status, SECURITY, Code of Conduct, CHANGELOG, RELEASE_NOTES
- CI: Markdown/YAML lint, Python smoke checks
- .gitignore and LICENSE (MIT)
- RULES.md for development workflow
- memory/ARCHITECTURE.md for codebase overview
