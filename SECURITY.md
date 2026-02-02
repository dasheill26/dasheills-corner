# Security Overview

This project applies multiple complementary security controls:

- **Authentication**: session-based login with password hashing (Werkzeug).
- **Access control**: protected routes via `login_required`; admin access via `ADMIN_EMAILS`.
- **Secrets management**: secrets are read from environment variables (see `.env.example`).
- **Least privilege**: uses managed GCP identity where available; app runs without embedding keys.
- **Safe Firestore usage**: Firestore operations are wrapped so missing credentials won’t crash the app (useful for local testing).
- **Validation**: server-side input checks for registration, login, checkout.
- **Deployment hygiene**: `/healthz` endpoint for monitoring; `.gitignore` prevents committing local DB and secrets.

## Reporting vulnerabilities
For coursework/demo purposes, report issues to the project owner via GitHub Issues (private if required).
