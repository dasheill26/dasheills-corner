import os
from typing import List, Dict, Any
from google.cloud import firestore

MENU_COLLECTION = "menuItems"

_db = None


def _get_db():
    """
    Returns a Firestore client.
    Uses FIRESTORE_PROJECT_ID if set; otherwise uses default credentials/project.
    """
    global _db
    if _db is None:
        project_id = os.environ.get("FIRESTORE_PROJECT_ID")
        _db = firestore.Client(project=project_id) if project_id else firestore.Client()
    return _db


def get_menu_items(include_unavailable: bool = True) -> List[Dict[str, Any]]:
    """
    Returns menu items from Firestore.
    Each item includes:
      - id (document id)
      - name, description, pricePence, category, image, sortOrder, isAvailable
    """
    db = _get_db()
    docs = db.collection(MENU_COLLECTION).stream()

    items: List[Dict[str, Any]] = []
    for d in docs:
        data = d.to_dict() or {}
        data["id"] = d.id

        # Backward compatibility: some earlier seeds used imageUrl instead of image
        if "image" not in data and "imageUrl" in data:
            data["image"] = data.get("imageUrl")

        # Ensure keys exist (avoid template crashes)
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

    # Sort: category then sortOrder then name
    items.sort(
        key=lambda x: (
            x.get("category", "Other"),
            x.get("sortOrder", 9999),
            x.get("name", ""),
        )
    )
    return items


def update_menu_item(doc_id: str, fields: Dict[str, Any]) -> None:
    """Updates a Firestore menu item document by id. Only updates fields provided."""
    db = _get_db()
    db.collection(MENU_COLLECTION).document(doc_id).update(fields)


def set_menu_item_availability(doc_id: str, is_available: bool) -> None:
    db = _get_db()
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
    - If Firestore isn't available or credentials missing, it will NOT crash your app.
    - It simply returns without doing anything.
    """
    try:
        db = _get_db()

        doc = {
            "order_id": int(order_id),
            "user_email": str(user_email),
            "total_pence": int(total_pence),
            "status": str(status),
            "items": items,
            "created_at": firestore.SERVER_TIMESTAMP,
            "source": "flask_app",
        }

        # Keep collection name consistent (you can change later if you want)
        db.collection("order_events").add(doc)

    except Exception:
        # IMPORTANT: never crash the website if Firestore logging fails
        return
