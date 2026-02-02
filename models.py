from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ✅ Rewards: points stored in SQL
    reward_points = db.Column(db.Integer, nullable=False, default=0)  # 1 point = 1 pence

    orders = db.relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    def set_password(self, p: str) -> None:
        self.password_hash = generate_password_hash(p)

    def check_password(self, p: str) -> bool:
        return check_password_hash(self.password_hash, p)


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_pence = db.Column(db.Integer, nullable=False, default=0)  # subtotal after discounts + points
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ✅ Status in SQL
    status = db.Column(db.String(20), nullable=False, default="Placed")  # Placed/Preparing/Ready

    # ✅ Payment (demo-safe)
    payment_method = db.Column(db.String(20), nullable=False, default="COD")  # COD or CARD_DEMO
    payment_status = db.Column(db.String(20), nullable=False, default="UNPAID")  # UNPAID/PAID
    payment_ref = db.Column(db.String(120), nullable=True)

    # ✅ Discounts & rewards usage on the order
    coupon_code = db.Column(db.String(40), nullable=True)
    discount_pence = db.Column(db.Integer, nullable=False, default=0)
    points_redeemed = db.Column(db.Integer, nullable=False, default=0)
    points_earned = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship("User", back_populates="orders", lazy=True)
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy=True
    )


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)

    # Maps to Firestore menu item
    item_id = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(150), nullable=False)

    price_pence = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=1)

    order = db.relationship("Order", back_populates="items", lazy=True)


class Coupon(db.Model):
    __tablename__ = "coupon"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)  # e.g. DASHEILL10
    active = db.Column(db.Boolean, nullable=False, default=True)

    # One of these can be used (percent takes priority if set)
    percent_off = db.Column(db.Integer, nullable=True)       # e.g. 10 means 10% off
    fixed_off_pence = db.Column(db.Integer, nullable=True)   # e.g. 200 means £2.00 off

    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
