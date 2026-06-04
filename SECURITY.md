# Security policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.9.x (main) | Yes |

## Reporting a vulnerability

Please **do not** open public GitHub issues for security vulnerabilities.

Email: **security@your-org.example** (replace with your team contact before production use)

Include:

- Description and impact
- Steps to reproduce
- Suggested fix (if any)

We aim to acknowledge reports within 5 business days.

## Secure configuration

- Rotate `NEXUS_API_KEY` and ingest HMAC secrets in production.
- Keep `NEXUS_DEMO_MODE=true` for public demos only.
- See [docs/security-compliance.md](docs/security-compliance.md) for control details.
