# Evaluation Report Outline (<=1000 words)

## Stack used
- Python/Flask, Jinja2, SQLAlchemy, Firestore client, App Engine

## Alternatives (compare at least 2 each)
- Backend: Django / FastAPI
- Frontend: React / Next.js
- SQL: Cloud SQL Postgres / MySQL
- NoSQL: Firestore / DynamoDB / MongoDB Atlas
- Hosting: Cloud Run / GKE vs App Engine

## Security evaluation
- Password hashing, sessions, env vars
- RBAC (ADMIN_EMAILS)
- Firestore credentials strategy
- Improvements: rate limiting, CSRF, CSP headers

## Database evaluation
- Why SQL for relational orders/users
- Why NoSQL for menu + event logging
- Tradeoffs and consistency model

## APIs and functions evaluation
- REST endpoints + optional cloud function usage
- Improvements: versioning, auth tokens, OpenAPI

## Testing and professionalism
- pytest suite + evidence outputs
- git history and commits
