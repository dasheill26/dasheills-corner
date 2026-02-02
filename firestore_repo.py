import os
from typing import List, Dict, Any, Optional

from google.cloud import firestore

MENU_COLLECTION = "menuItems"

_db = None


def _get_db() -> Optional["firestore.Client"]:
    """
    Returns a Firestore client.
    If credentials/project are not available (e.g., during pytest), returns None.
    """
    global _db
    if _db is not None:
        return _db

    try:
        project_id = os.environ.get("FIRESTORE_PROJECT_ID")
        _db = firestore.Client(project=project_id) if project_id else firestore.Client()
        return _db
    except Exception:
        # IMPORTANT: don't crash tests/local if Firestore isn't available
        return None


def get_menu_items(include_unavailable: bool = True) -> List[Dict[str, Any]]:
    """
    Returns menu items from Firestore.
    Safe fallback: returns [] if Firestore isn't available.
    """
    db = _get_db()
    if db is None:
        return []

    docs = db.collection(MENU_COLLECTION).stream()

    items: List[Dict[str, Any]] = []
    for d in docs:
        data = d.to_dict() or {}

        # normalize id fields for consistency across templates + cart + APIs
        data["id"] = d.id
        data["itemId"] = d.id  # <- important alias used by your cart/session logic

        if "image" not in data and "imageUrl" in data:
            data["image"] = data.get("imageUrl")

        data.setdefault("name", "")
        data.setdefault("description", "")
        data.setdefault("pricePence", 0)
        data.setdefault("category", "Other")
        data.setdefault("sortOrder", 9999)
        data.setdefault("isAvailable", True)
        data.setdefault("image", "")

        if not include_unavailable and not data.get("isAvailable", True):
            continue

        items.append(data)

    items.sort(
        key=lambda x: (
            x.get("category", "Other"),
            x.get("sortOrder", 9999),
            x.get("name", ""),
        )
    )
    return items


def update_menu_item(doc_id: str, fields: Dict[str, Any]) -> None:
    db = _get_db()
    if db is None:
        return
    db.collection(MENU_COLLECTION).document(doc_id).update(fields)


def set_menu_item_availability(doc_id: str, is_available: bool) -> None:
    db = _get_db()
    if db is None:
        return
    db.collection(MENU_COLLECTION).document(doc_id).update({"isAvailable": bool(is_available)})


def log_order_event(
    order_id: int,
    user_email: str,
    total_pence: int,
    items: list,
    status: str = "Placed",
) -> None:
    """
    Safe Firestore logger for order events.
    Never crashes the website/tests if Firestore isn't available.
    """
    db = _get_db()
    if db is None:
        return

    try:
        doc = {
            "order_id": int(order_id),
            "user_email": str(user_email),
            "total_pence": int(total_pence),
            "status": str(status),
            "items": items,
            "created_at": firestore.SERVER_TIMESTAMP,
            "source": "flask_app",
        }
        db.collection("order_events").add(doc)
    except Exception:
        return
