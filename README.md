# Dasheill’s Corner — Cloud Restaurant Ordering App (GCP)

Dasheill’s Corner is a full-stack restaurant ordering web app built with **Flask (Python)** and deployed on **Google App Engine**. It provides a modern ordering experience (menu browsing, cart, checkout), account authentication, admin management, and a **points-based rewards system**. The UI is fully customised and responsive, keeping consistent theming across Home, Menu, Cart/Checkout, and Auth pages.

## Key Features
- **Menu browsing** with categories and images
- **Cart**: add/remove items, adjust quantities, live totals
- **Checkout & Orders**: place orders and view order history
- **Authentication**: register/login/logout, session-based auth
- **Password strength meter** on registration
- **Rewards**: earn points from orders and redeem as credit (loyalty system)
- **Admin tools** (role-based access): manage menu items and content
- **Internationalisation (i18n)**: language selector + translations

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript (custom responsive UI)
- **Backend**: Python + Flask, Jinja2 templates
- **Cloud Hosting**: Google App Engine
- **Databases**:
  - **SQL** (structured relational data such as users/orders/order_items)
  - **NoSQL (Firestore)** (semi/unstructured data such as rewards, metadata, etc.)
- **Cloud Functions / APIs**: application endpoints and background/processing logic (where implemented)

## Security (Complementary Strategies)
- Password hashing (never store plaintext passwords)
- Session-based authentication + secure cookie practices
- Role-based access control (admin vs user)
- Sensitive configuration isolated from source (environment variables)
- Cloud-managed services (App Engine/Firestore) to reduce infrastructure risk

---

# Run Locally (Cloud Shell / local machine)

## 1) Create & activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2) Environment variables

Create your env configuration as required by the project (examples):

export FLASK_ENV=development
export SECRET_KEY="change-me"
# Add any required database / firestore config env vars used by the project

3) Start the app
python main.py


Open: http://127.0.0.1:5000
 (or the Cloud Shell preview URL)

Deploy to Google App Engine

From the project root:

gcloud app deploy
gcloud app browse

Run Tests
python -m pytest -q

Project Structure (high level)

main.py / app.yaml — App Engine entry + configuration

templates/ — Jinja2 HTML templates

static/ — CSS, JS, images

models.py — data models / DB logic

tests/ — unit tests for key app logic and routes

## Testing

This project includes automated unit and integration tests written using **pytest**.

### How to run tests

```bash
source .venv/bin/activate
pytest -v
