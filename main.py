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
        "Order type": "Order type",
        "Delivery": "Delivery",
        "Collection": "Collection",
        "Eat-in": "Eat-in",
        "Booking": "Booking",
        "Delivery address": "Delivery address",
        "Collection time": "Collection time",
        "Booking time": "Booking time",
        "Table number (optional)": "Table number (optional)",
        "Choose how you want your order. Delivery needs an address. Collection / Booking can include a time.": (
            "Choose how you want your order. Delivery needs an address. Collection / Booking can include a time."
        ),
        "Tip: you can enter ASAP or a time like 18:30.": "Tip: you can enter ASAP or a time like 18:30.",
        "Add a date/time so we can reserve it.": "Add a date/time so we can reserve it.",
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
        "Order type": "Tipo de pedido",
        "Delivery": "Entrega",
        "Collection": "Recogida",
        "Eat-in": "Comer allí",
        "Booking": "Reserva",
        "Delivery address": "Dirección de entrega",
        "Collection time": "Hora de recogida",
        "Booking time": "Hora de reserva",
        "Table number (optional)": "Número de mesa (opcional)",
        "Choose how you want your order. Delivery needs an address. Collection / Booking can include a time.": (
            "Elige cómo quieres tu pedido. La entrega necesita una dirección. Recogida / Reserva puede incluir una hora."
        ),
        "Tip: you can enter ASAP or a time like 18:30.": "Consejo: puedes escribir ASAP o una hora como 18:30.",
        "Add a date/time so we can reserve it.": "Añade fecha/hora para poder reservar.",
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
        "Order type": "Type de commande",
        "Delivery": "Livraison",
        "Collection": "À emporter",
        "Eat-in": "Sur place",
        "Booking": "Réservation",
        "Delivery address": "Adresse de livraison",
        "Collection time": "Heure de retrait",
        "Booking time": "Heure de réservation",
        "Table number (optional)": "Numéro de table (optionnel)",
        "Choose how you want your order. Delivery needs an address. Collection / Booking can include a time.": (
            "Choisissez votre mode de commande. La livraison nécessite une adresse. À emporter / Réservation peut inclure une heure."
        ),
        "Tip: you can enter ASAP or a time like 18:30.": "Astuce : vous pouvez écrire ASAP ou une heure comme 18:30.",
        "Add a date/time so we can reserve it.": "Ajoutez une date/heure pour réserver.",
    },
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    # DB init
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ---------------- Helpers ----------------
    def current_user():
        uid = session.get("user_id")
        return db.session.get(User, uid) if uid else None

    def is_admin_user(u):
        if not u:
            return False
        admins = os.environ.get("ADMIN_EMAILS", "").strip()
        if not admins:
            return False
        admin_list = [a.strip().lower() for a in admins.split(",") if a.strip()]
        return u.email.lower() in admin_list

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
        lang = (session.get("lang") or "en").lower()
        return lang if lang in SUPPORTED_LANGS else "en"

    def t(key: str, **kwargs) -> str:
        lang = get_lang()
        text = TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["en"].get(key, key))
        if kwargs:
            try:
                return text % kwargs
            except Exception:
                return text
        return text

    # ✅ THIS fixes: jinja2.exceptions.UndefinedError: 't' is undefined
    @app.context_processor
    def inject_globals():
        u = current_user()
        return {
            "app_name": APP_NAME,
            "current_user": u,
            "is_admin": is_admin_user(u),
            "cart_count": cart_count(),
            "lang": get_lang(),
            "languages": SUPPORTED_LANGS,
            "t": t,
            "_": t,  # allow {{ _("Menu") }}
        }

    # ---------------- Health check ----------------
    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    # ---------------- Language switch ----------------
    @app.get("/lang/<code>")
    def set_language(code):
        code = (code or "").lower()
        if code in SUPPORTED_LANGS:
            session["lang"] = code

        nxt = request.args.get("next")
        if nxt:
            return redirect(nxt)
        ref = request.referrer
        return redirect(ref or url_for("index"))

    # ---------------- Pages ----------------
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/menu")
    def menu():
        items = get_menu_items()

        categories = {"Mains": [], "Sides": [], "Drinks": []}
        for it in items:
            categories.setdefault(it.get("category", "Other"), []).append(it)
        for k in categories:
            categories[k].sort(key=lambda x: x.get("sortOrder", 9999))

        cm = {}
        for ci in cart_items():
            cm[str(ci["itemId"])] = int(ci.get("qty", 0))

        return render_template("menu.html", categories=categories, cart_map=cm)

    @app.get("/cart")
    def cart():
        return render_template("cart.html", cart=cart_items(), subtotal_pence=cart_subtotal_pence())

    @app.get("/checkout")
    @login_required
    def checkout():
        if not cart_items():
            flash("Your cart is empty.", "error")
            return redirect(url_for("menu"))

        u = current_user()
        return render_template(
            "checkout.html",
            cart=cart_items(),
            subtotal_pence=cart_subtotal_pence(),
            user_points=int(getattr(u, "reward_points", 0) or 0),
            coupons=[]
        )

    # ---------------- REST API ----------------
    @app.get("/api/menu")
    def api_menu():
        items = get_menu_items(include_unavailable=True)
        normalized = []
        for it in items:
            normalized.append({
                "id": it.get("id") or it.get("itemId"),
                "itemId": it.get("itemId") or it.get("id"),
                "name": it.get("name", ""),
                "description": it.get("description", ""),
                "pricePence": int(it.get("pricePence", 0) or 0),
                "category": it.get("category", "Other"),
                "image": it.get("image", ""),
                "sortOrder": int(it.get("sortOrder", 9999) or 9999),
                "isAvailable": bool(it.get("isAvailable", True)),
            })
        return jsonify(normalized), 200

    # ---------------- Demo Payment (2-step) ----------------
    @app.post("/pay/stripe")
    @login_required
    def pay_stripe():
        if not cart_items():
            flash("Your cart is empty.", "error")
            return redirect(url_for("menu"))

        order_type = request.form.get("order_type", "delivery").strip().lower()
        collection_time = request.form.get("collection_time", "ASAP").strip()
        booking_time = request.form.get("booking_time", "").strip()
        table_number = request.form.get("table_number", "").strip()

        name = request.form.get("customer_name", "").strip()
        address = request.form.get("delivery_address", "").strip()

        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("checkout"))

        if order_type == "delivery" and not address:
            flash("Delivery address is required.", "error")
            return redirect(url_for("checkout"))

        if order_type == "booking" and not booking_time:
            flash("Booking time is required.", "error")
            return redirect(url_for("checkout"))

        coupon_code = request.form.get("coupon_code", "").strip().upper()
        redeem_points = (request.form.get("redeem_points") == "on")

        session["pending_payment"] = {
            "order_type": order_type,
            "collection_time": collection_time,
            "booking_time": booking_time,
            "table_number": table_number,
            "customer_name": name,
            "delivery_address": address,
            "coupon_code": coupon_code,
            "redeem_points": redeem_points,
            "subtotal_pence": cart_subtotal_pence(),
        }
        return redirect(url_for("pay_card"))

    @app.get("/pay/card")
    @login_required
    def pay_card():
        if not cart_items() or not session.get("pending_payment"):
            flash("No pending payment found. Please checkout again.", "error")
            return redirect(url_for("checkout"))

        return render_template(
            "pay_card.html",
            cart=cart_items(),
            subtotal_pence=int(session["pending_payment"].get("subtotal_pence", cart_subtotal_pence())),
        )

    def _looks_like_card_number(num: str) -> bool:
        digits = "".join(ch for ch in num if ch.isdigit())
        return 12 <= len(digits) <= 19

    @app.post("/pay/confirm")
    @login_required
    def pay_confirm():
        if not cart_items() or not session.get("pending_payment"):
            flash("No pending payment found. Please checkout again.", "error")
            return redirect(url_for("checkout"))

        card_name = request.form.get("card_name", "").strip()
        card_number = request.form.get("card_number", "").strip()
        exp = request.form.get("exp", "").strip()
        cvc = request.form.get("cvc", "").strip()

        if not card_name or not card_number or not exp or not cvc:
            flash("Please fill in all card details (demo).", "error")
            return redirect(url_for("pay_card"))

        if not _looks_like_card_number(card_number):
            flash("Card number looks invalid (demo). Try 4242 4242 4242 4242.", "error")
            return redirect(url_for("pay_card"))

        if len("".join(ch for ch in cvc if ch.isdigit())) < 3:
            flash("CVC looks invalid (demo).", "error")
            return redirect(url_for("pay_card"))

        u = current_user()
        total = cart_subtotal_pence()

        order = Order(user_id=u.id, total_pence=total)
        db.session.add(order)
        db.session.commit()

        for it in cart_items():
            db.session.add(OrderItem(
                order_id=order.id,
                item_id=str(it["itemId"]),
                name=str(it["name"]),
                price_pence=int(it["pricePence"]),
                qty=int(it["qty"]),
            ))
        db.session.commit()

        earned = int(round(total * 0.05))
        if hasattr(u, "reward_points"):
            u.reward_points = int(getattr(u, "reward_points", 0) or 0) + earned
            db.session.commit()

        session["cart"] = []
        session.pop("pending_payment", None)

        flash(f"Payment approved (demo). Order #{order.id} placed!", "ok")
        return redirect(url_for("orders"))

    @app.get("/orders")
    @login_required
    def orders():
        u = current_user()
        orders_q = (
            Order.query
            .filter_by(user_id=u.id)
            .order_by(Order.created_at.desc())
            .all()
        )
        order_items_map = {o.id: OrderItem.query.filter_by(order_id=o.id).all() for o in orders_q}
        user_points = int(getattr(u, "reward_points", 0) or 0)
        return render_template("orders.html", orders=orders_q, order_items_map=order_items_map, user_points=user_points)

    @app.post("/orders/<int:order_id>/status")
    @login_required
    def update_order_status(order_id: int):
        u = current_user()
        o = Order.query.filter_by(id=order_id, user_id=u.id).first()
        if not o:
            flash("Order not found.", "error")
            return redirect(url_for("orders"))

        new_status = request.form.get("status", "Placed").strip()
        allowed = {"Placed", "Preparing", "Ready"}
        if new_status not in allowed:
            flash("Invalid status.", "error")
            return redirect(url_for("orders"))
        o.status = new_status
        db.session.commit()
        flash(f"Order #{o.id} updated to {new_status}.", "ok")

        return redirect(url_for("orders"))

    # ---------------- Auth ----------------
    @app.get("/login")
    def login():
        return render_template("login.html")

    @app.post("/login")
    def login_post():
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        u = User.query.filter_by(email=email).first()
        if not u or not u.check_password(password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))
        session["user_id"] = u.id
        flash("Logged in.", "ok")
        return redirect(url_for("menu"))

    @app.get("/register")
    def register():
        return render_template("register.html")

    @app.post("/register")
    def register_post():
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or "@" not in email:
            flash("Enter a valid email.", "error")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("That email is already registered. Please login.", "error")
            return redirect(url_for("login"))

        u = User(email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        session["user_id"] = u.id
        flash("Account created!", "ok")
        return redirect(url_for("menu"))

    @app.get("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "ok")
        return redirect(url_for("index"))

    # ---------------- Cart API ----------------
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
            if str(it["itemId"]) == str(item_id):
                it["qty"] = int(it["qty"]) + 1
                session["cart"] = c
                return jsonify({
                    "cart": c,
                    "cartCount": sum(int(x.get("qty", 0)) for x in c),
                    "subtotalPence": sum(int(x["pricePence"]) * int(x["qty"]) for x in c),
                })

        c.append({"itemId": str(item_id), "name": name, "pricePence": int(price), "qty": 1})
        session["cart"] = c
        return jsonify({
            "cart": c,
            "cartCount": sum(int(x.get("qty", 0)) for x in c),
            "subtotalPence": sum(int(x["pricePence"]) * int(x["qty"]) for x in c),
        })

    @app.post("/api/cart/setqty")
    def api_cart_setqty():
        data = request.get_json(force=True) or {}
        item_id = data.get("itemId")
        qty = data.get("qty")

        if not item_id or not isinstance(qty, int):
            return jsonify({"error": "Invalid request"}), 400

        new_cart = []
        for it in cart_items():
            if str(it["itemId"]) == str(item_id):
                if qty > 0:
                    it["qty"] = qty
                    new_cart.append(it)
            else:
                new_cart.append(it)

        session["cart"] = new_cart
        subtotal = sum(int(i["pricePence"]) * int(i["qty"]) for i in new_cart)
        return jsonify({
            "cart": new_cart,
            "cartCount": sum(int(x.get("qty", 0)) for x in new_cart),
            "subtotalPence": subtotal
        })

    # ---------------- Error handlers ----------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500


    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
