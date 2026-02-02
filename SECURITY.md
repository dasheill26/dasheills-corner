# Security Notes

## Implemented
- Password hashing (Werkzeug)
- Session-based authentication
- Protected routes for checkout/orders
- Admin access via ADMIN_EMAILS env var
- Secrets not hard-coded (see .env.example)

## Recommended improvements
- CSRF protection for form posts
- Rate limiting for login endpoints
- Security headers (CSP, HSTS)
- Audit logging and monitoring on GCP
