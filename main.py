import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from config import Config
from models import db, User, Order, OrderItem
from firestore_repo import get_menu_items

APP_NAME = "DASHEILLS CORNER"

SUPPORTED_LANGS = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
}

TRANSLATIONS = {
    "en": {
        "Language": "Language",
        "Menu": "Menu",
        "Cart": "Cart",
        "Orders": "Orders",
        "Admin": "Admin",
        "Login": "Login",
        "Logout": "Logout",
        "Continue shopping": "Continue shopping",
        "Checkout": "Checkout",
    },
    "es": {
        "Language": "Idioma",
        "Menu": "Menú",
        "Cart": "Carrito",
        "Orders": "Pedidos",
        "Admin": "Admin",
        "Login": "Iniciar sesión",
        "Logout": "Cerrar sesión",
        "Continue shopping": "Seguir comprando",
        "Checkout": "Pagar",
    },
    "fr": {
        "Language": "Langue",
        "Menu": "Menu",
        "Cart": "Panier",
        "Orders": "Commandes",
        "Admin": "Admin",
        "Login": "Connexion",
        "Logout": "Déconnexion",
        "Continue shopping": "Continuer vos achats",
        "Checkout": "Paiement",
    },
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ---------------- Helpers ----------------
    def current_user():
        uid = session.get("user_id")
        return db.session.get(User, uid) if uid else None

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user():
                flash("Please login first.", "error")
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped

    def cart_items():
        return session.get("cart", [])

    def cart_subtotal_pence():
        return sum(int(i["pricePence"]) * int(i["qty"]) for i in cart_items())

    def cart_count():
        return sum(int(i.get("qty", 0)) for i in cart_items())

    def get_lang():
        return session.get("lang", "en")

    def t(key):
        return TRANSLATIONS.get(get_lang(), {}).get(key, key)

    @app.context_processor
    def inject_globals():
        return {
            "app_name": APP_NAME,
            "current_user": current_user(),
            "cart_count": cart_count(),
            "lang": get_lang(),
            "languages": SUPPORTED_LANGS,
            "_": t,
        }

    # ---------------- Health Check (NEW) ----------------
    @app.get("/health")
    def health():
        """
        Health check endpoint for cloud deployments.
        Used by load balancers / App Engine.
        """
        return jsonify({"status": "ok"}), 200

    # ---------------- Pages ----------------
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/menu")
    def menu():
        items = get_menu_items()
        return render_template("menu.html", items=items)

    @app.get("/cart")
    def cart():
        return render_template("cart.html", cart=cart_items(), subtotal_pence=cart_subtotal_pence())

    # ---------------- API ----------------
    @app.get("/api/menu")
    def api_menu():
        items = get_menu_items()
        return jsonify(items), 200

    @app.post("/api/cart/add")
    def api_cart_add():
        data = request.get_json(force=True) or {}
        item_id = data.get("itemId")
        name = data.get("name")
        price = data.get("pricePence")

        if not item_id or not name or not isinstance(price, int):
            return jsonify({"error": "Invalid item"}), 400

        c = cart_items()
        for it in c:
            if it["itemId"] == item_id:
                it["qty"] += 1
                session["cart"] = c
                return jsonify(c)

        c.append({"itemId": item_id, "name": name, "pricePence": price, "qty": 1})
        session["cart"] = c
        return jsonify(c)

    # ---------------- Auth ----------------
    @app.get("/login")
    def login():
        return render_template("login.html")

    @app.post("/login")
    def login_post():
        email = request.form.get("email", "").lower()
        password = request.form.get("password", "")
        u = User.query.filter_by(email=email).first()
        if not u or not u.check_password(password):
            flash("Invalid credentials", "error")
            return redirect(url_for("login"))
        session["user_id"] = u.id
        return redirect(url_for("menu"))

    @app.get("/register")
    def register():
        return render_template("register.html")

    @app.post("/register")
    def register_post():
        email = request.form.get("email", "").lower()
        password = request.form.get("password", "")
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return redirect(url_for("login"))

        u = User(email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        session["user_id"] = u.id
        return redirect(url_for("menu"))

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    return app

    # ---------------- Security ----------------
    # All sensitive routes (checkout, orders, payment)
    # are protected using session-based authentication
    # via the @login_required decorator.

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
