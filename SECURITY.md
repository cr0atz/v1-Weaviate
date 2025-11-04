# Security Policy

## Supported Versions
This is an early open-source release. Security fixes will be best-effort until 1.0.0.

## Reporting a Vulnerability
Please open a private advisory (GitHub Security Advisories) or email the maintainers. Do not publicly disclose vulnerabilities until a fix is available.

## Guidelines
- Never commit secrets. Use `.env` and GitHub Actions secrets.
- Rotate keys regularly. Remove hardcoded tokens from code before production.
- Limit inbound access to the FastAPI service via Apache reverse proxy and firewall.
