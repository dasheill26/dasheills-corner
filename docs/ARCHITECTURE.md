# Architecture

## Overview
Dasheill’s Corner is a Flask web app deployed on Google App Engine.

## Components
- **Flask + Jinja2 UI**: SSR pages (menu/cart/checkout/auth/orders) with i18n helper.
- **REST endpoints**: JSON endpoints used for menu and cart actions.
- **SQL (SQLite/SQLAlchemy)**: Users, Orders, OrderItems (structured relational data).
- **NoSQL (Firestore)**: Menu items and event logging (semi/unstructured data).

## Data flow (order)
1. User adds items to cart (session).
2. Checkout collects delivery/collection/booking details.
3. Payment demo confirms and creates:
   - Order (SQL)
   - OrderItems (SQL)
   - Optional Firestore order event log (NoSQL)
4. Loyalty points are updated in SQL.

## Deployment
- `app.yaml` configures App Engine.
- `/healthz` supports uptime checks/monitoring.
- `.env.example` documents required environment variables.
