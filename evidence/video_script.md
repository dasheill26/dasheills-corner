# Video Demo Script (15 mins max)

## 1) Intro (30s)
- What the app is: cloud restaurant ordering on GCP (App Engine).
- Key features: menu, cart, auth, checkout, orders, rewards, i18n.

## 2) UI Walkthrough (3 mins)
- Home -> Menu -> Cart -> Checkout -> Orders
- Show responsive layout + consistent styling.

## 3) Architecture (3 mins)
- Flask (server-side rendered Jinja2)
- SQL (SQLite/SQLAlchemy) for Users/Orders/OrderItems
- NoSQL (Firestore) for Menu + order_events logging
- REST endpoints: /api/menu and cart APIs

## 4) Cloud + Security (4 mins)
- App Engine deployment
- Env vars (.env.example, Secret Key, ADMIN_EMAILS)
- Password hashing (Werkzeug)
- Session auth + protected routes
- Explain Firestore credentials handling

## 5) Tests + Evidence (2 mins)
- Run pytest
- Show evidence/pytest_results*.txt
- Mention what each test covers

## 6) Wrap up (30s)
- What you would improve next (payments, CI, more i18n strings, monitoring)
