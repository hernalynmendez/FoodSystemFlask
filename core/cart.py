def add_to_cart(session, item):
    if "cart" not in session:
        session["cart"] = []

    item_id = str(item.get("id"))
    qty = int(item.get("qty", 1))

    for cart_item in session["cart"]:
        if str(cart_item.get("id")) == item_id:
            cart_item["qty"] = int(cart_item.get("qty", 0)) + qty
            if item.get("image"):
                cart_item["image"] = item.get("image")
            session.modified = True
            return

    session["cart"].append({
        "id": item_id,
        "name": item.get("name"),
        "price": float(item.get("price", 0)),
        "qty": qty,
        "image": item.get("image", "uploads/food/magherita pizza.jpg"),
    })
    session.modified = True


def get_cart(session):
    return session.get("cart", [])


def clear_cart(session):
    session["cart"] = []
    session.modified = True


def remove_from_cart(session, item_id):
    cart = session.get("cart", [])
    session["cart"] = [item for item in cart if str(item.get("id")) != str(item_id)]
    session.modified = True


def cart_total(session):
    total = 0.0
    for item in get_cart(session):
        total += float(item.get("price", 0)) * int(item.get("qty", 1))
    return total
