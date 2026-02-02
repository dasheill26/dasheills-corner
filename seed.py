import os
import re
import shutil
import urllib.request
from google.cloud import firestore

db = firestore.Client()
col = db.collection("menuItems")

def p(x):
    return int(round(x * 100))

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

# ----------------------------
# Your menu items (UNCHANGED)
# ----------------------------
MAINS = [
    ("Classic Wings (6pc)", 7.99, "Crispy wings, sauce of your choice."),
    ("Classic Wings (10pc)", 10.49, "Crispy wings, sauce of your choice."),
    ("Classic Wings (15pc)", 13.99, "Crispy wings, sauce of your choice."),
    ("Boneless Wings (6pc)", 7.49, "Juicy boneless bites, sauce of your choice."),
    ("Boneless Wings (10pc)", 9.99, "Juicy boneless bites, sauce of your choice."),
    ("Boneless Wings (15pc)", 12.99, "Juicy boneless bites, sauce of your choice."),
    ("Tender Strips (3pc)", 6.99, "Golden tenders with dip."),
    ("Tender Strips (5pc)", 9.49, "Golden tenders with dip."),
    ("Tender Strips (7pc)", 11.99, "Golden tenders with dip."),
    ("Classic Chicken Burger", 8.49, "Crispy chicken, slaw, signature sauce."),
    ("Spicy Chicken Burger", 8.79, "Heat + crunch, spicy mayo."),
    ("BBQ Chicken Burger", 8.79, "Smoky BBQ glaze, crispy chicken."),
    ("Garlic Parm Wings (10pc)", 10.99, "Garlic parmesan coating."),
    ("Lemon Pepper Wings (10pc)", 10.99, "Zesty lemon pepper rub."),
    ("Hot Honey Wings (10pc)", 11.49, "Sweet heat hot honey glaze."),
    ("Smoky BBQ Wings (10pc)", 10.99, "Smoky BBQ sauce."),
    ("Extra Hot Wings (10pc)", 11.49, "For serious heat lovers."),
    ("Wing Combo (10pc + fries)", 13.49, "Wings + seasoned fries."),
    ("Boneless Combo (10pc + fries)", 12.99, "Boneless + seasoned fries."),
    ("Tenders Combo (5pc + fries)", 12.49, "Tenders + seasoned fries."),
    ("Loaded Wing Box", 15.99, "Wings + fries + dip."),
    ("Family Feast", 26.99, "Big bundle for sharing."),
    ("Party Platter", 35.99, "Perfect for groups."),
    ("Chicken Wrap", 7.99, "Crispy chicken wrap, house sauce."),
    ("Spicy Chicken Wrap", 8.29, "Spicy wrap with crunchy slaw."),
    ("Grilled Chicken Wrap", 8.49, "Grilled chicken, lighter option."),
    ("Double Chicken Burger", 10.49, "Two crispy fillets, extra sauce."),
    ("Wings & Tenders Mix Box", 18.99, "Half wings, half tenders."),
    ("Boneless Meal Box", 16.99, "Boneless bites + fries + dip."),
    ("Signature Wing Meal", 17.99, "Wings + side + drink (classic)."),
]

SIDES = [
    ("Seasoned Fries", 2.99, "Crispy fries with signature seasoning."),
    ("Large Seasoned Fries", 3.99, "Bigger portion of seasoned fries."),
    ("Sweet Potato Fries", 3.49, "Sweet potato fries, lightly salted."),
    ("Onion Rings", 3.49, "Crispy battered onion rings."),
    ("Mozzarella Sticks", 4.49, "Cheesy sticks with dip."),
    ("Mac & Cheese", 3.99, "Creamy mac & cheese."),
    ("Loaded Fries", 4.99, "Cheese + sauce + crispy toppings."),
    ("Coleslaw", 2.49, "Fresh slaw, creamy dressing."),
    ("Corn on the Cob", 2.99, "Buttery corn cob."),
    ("Garlic Bread", 2.49, "Toasted garlic bread."),
    ("Cheesy Garlic Bread", 2.99, "Garlic bread with melted cheese."),
    ("Side Salad", 3.49, "Fresh greens + dressing."),
    ("Veggie Sticks", 1.99, "Crunchy carrot & celery."),
    ("Jalapeño Poppers", 4.49, "Cream cheese poppers."),
    ("Mashed Potatoes", 2.99, "Smooth mash."),
    ("Gravy Dip", 0.99, "Classic gravy dip."),
    ("Ranch Dip", 0.99, "Cool ranch dip."),
    ("Blue Cheese Dip", 0.99, "Tangy blue cheese dip."),
    ("BBQ Dip", 0.99, "Smoky BBQ dip."),
    ("Honey Mustard Dip", 0.99, "Sweet honey mustard."),
    ("Hot Sauce Dip", 0.99, "Extra kick."),
    ("Cheese Sauce", 1.49, "Warm cheese sauce."),
    ("Chilli Cheese Fries", 5.49, "Fries + chilli + cheese."),
    ("Curly Fries", 3.49, "Spiral seasoned fries."),
    ("Waffle Fries", 3.99, "Crispy waffle fries."),
    ("Cajun Fries", 3.49, "Cajun spice fries."),
    ("Rice Bowl", 4.99, "Seasoned rice side."),
    ("Baked Beans", 2.99, "Smoky baked beans."),
    ("Pickles", 1.49, "Crunchy pickles."),
    ("Extra Slaw", 2.49, "Extra portion of slaw."),
]

DRINKS = [
    ("Coke", 1.79, "Classic chilled can."),
    ("Diet Coke", 1.79, "Zero sugar classic."),
    ("Coke Zero", 1.79, "No sugar, full taste."),
    ("Fanta Orange", 1.79, "Orange fizz."),
    ("Sprite", 1.79, "Lemon-lime."),
    ("Dr Pepper", 1.79, "Classic blend."),
    ("Pepsi", 1.79, "Chilled can."),
    ("Pepsi Max", 1.79, "No sugar."),
    ("7UP", 1.79, "Citrus fizz."),
    ("Still Water", 1.49, "Refreshing water."),
    ("Sparkling Water", 1.49, "Sparkling water."),
    ("Lemonade", 1.99, "Sweet lemonade."),
    ("Iced Tea", 1.99, "Cold brewed iced tea."),
    ("Apple Juice", 1.89, "Apple juice carton."),
    ("Orange Juice", 1.89, "Orange juice carton."),
    ("Mango Juice", 1.99, "Mango juice."),
    ("Pineapple Juice", 1.99, "Pineapple juice."),
    ("Strawberry Milkshake", 3.99, "Creamy shake."),
    ("Vanilla Milkshake", 3.99, "Classic vanilla."),
    ("Chocolate Milkshake", 3.99, "Rich chocolate."),
    ("Oreo Milkshake", 4.49, "Oreo blended shake."),
    ("Energy Drink", 2.49, "Boosted energy drink."),
    ("Milk", 1.49, "Chilled milk."),
    ("Coffee", 1.99, "Hot coffee."),
    ("Latte", 2.49, "Milky latte."),
    ("Cappuccino", 2.49, "Foamy cappuccino."),
    ("Hot Chocolate", 2.49, "Warm cocoa."),
    ("Green Tea", 1.79, "Green tea."),
    ("Black Tea", 1.79, "Black tea."),
    ("Strawberry Lemonade", 2.29, "Fruity lemonade."),
]

# ----------------------------
# Image helpers
# ----------------------------
MENU_IMG_DIR = os.path.join("static", "images", "menu")
BASE_MAIN = os.path.join("static", "images", "mains.jpg")
BASE_SIDE = os.path.join("static", "images", "sides.jpg")
BASE_DRINK = os.path.join("static", "images", "drinks.jpg")

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def download_if_missing(path: str, url: str) -> None:
    """Download a jpg if it's missing (used only for base images)."""
    if os.path.exists(path):
        return
    ensure_dir(os.path.dirname(path))
    print(f"Downloading missing base image: {path}")
    urllib.request.urlretrieve(url, path)

def ensure_base_images():
    # Picsum is simple, no API key. These are just placeholders you can replace later.
    download_if_missing(BASE_MAIN, "https://picsum.photos/1200/800?random=201")
    download_if_missing(BASE_SIDE, "https://picsum.photos/1200/800?random=202")
    download_if_missing(BASE_DRINK, "https://picsum.photos/1200/800?random=203")

def ensure_item_image(category: str, name: str) -> str:
    """
    Makes sure a local jpg exists for this item.
    Returns the URL path that the website will use: /static/images/menu/<slug>.jpg
    """
    ensure_dir(MENU_IMG_DIR)

    slug = slugify(f"{category}-{name}")
    filename = f"{slug}.jpg"
    filepath = os.path.join(MENU_IMG_DIR, filename)

    if not os.path.exists(filepath):
        # Copy category base image to create a real per-item jpg
        if category == "Mains":
            src = BASE_MAIN
        elif category == "Sides":
            src = BASE_SIDE
        else:
            src = BASE_DRINK

        shutil.copyfile(src, filepath)

    # what we store in Firestore (your menu.html expects /static/... paths)
    return f"/static/images/menu/{filename}"

# ----------------------------
# Firestore seeding
# ----------------------------
def wipe_menu():
    existing = list(col.stream())
    if existing:
        batch = db.batch()
        for doc in existing:
            batch.delete(doc.reference)
        batch.commit()
        print(f"Deleted {len(existing)} existing menu items")

def seed_category(category_name, items):
    for idx, (name, price, desc) in enumerate(items, start=1):
        image_path = ensure_item_image(category_name, name)
        col.add({
            "name": name,
            "description": desc,
            "pricePence": p(price),
            "category": category_name,
            "image": image_path,
            "sortOrder": idx,
            "isAvailable": True
        })

if __name__ == "__main__":
    ensure_base_images()
    wipe_menu()
    seed_category("Mains", MAINS)
    seed_category("Sides", SIDES)
    seed_category("Drinks", DRINKS)
    print("✅ Seeded 90 real menu items AND created local JPG images for each item")
