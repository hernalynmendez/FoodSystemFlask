from functools import wraps
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename

import xml_helper as xml
from config import SECRET_KEY
from core import cart as cart_helper

app = Flask(__name__)
app.secret_key = SECRET_KEY

FOOD_IMAGE_FOLDER = os.path.join(app.root_path, "static", "uploads", "food")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "svg"}
DEFAULT_FOOD_IMAGE = "uploads/food/magherita pizza.jpg"


def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_food_image(file, item_id):
    os.makedirs(FOOD_IMAGE_FOLDER, exist_ok=True)
    original = secure_filename(file.filename)
    ext = original.rsplit(".", 1)[1].lower()
    filename = f"item-{item_id}.{ext}"
    file.save(os.path.join(FOOD_IMAGE_FOLDER, filename))
    return f"uploads/food/{filename}"


@app.template_filter("food_image")
def food_image_filter(image_path):
    path = image_path or DEFAULT_FOOD_IMAGE
    return url_for("static", filename=path)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def home():
    # If an admin is logged in, send them to the admin dashboard landing
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    items = xml.get_all_food_items()
    categories = xml.get_menu_categories()
    return render_template("index.html", items=items[:6], categories=categories, active_category=None, search_query="")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        result = xml.add_user(username, password)
        if result["success"]:
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        flash(result["message"], "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # First check regular users
        users = xml.get_all_users()
        for user in users:
            if user.get("username") == username and user.get("password") == password:
                # prevent disabled users from logging in
                if user.get('is_disabled') == 'true':
                    error_msg = 'Account disabled. Contact an administrator.'
                    return render_template('login.html', error=error_msg, username=username)

                session["user_id"] = user.get("id")
                session["username"] = user.get("username")
                session["is_admin"] = user.get("is_admin") == "true"
                flash(f"Welcome back, {username}!", "success")

                if session["is_admin"]:
                    return redirect(url_for("admin_dashboard"))
                return redirect(url_for("dashboard"))

        # Then check admin accounts stored in admins.xml
        admins = xml.get_all_admins()
        for admin in admins:
            if admin.get("username") == username and admin.get("password") == password:
                session["user_id"] = admin.get("id")
                session["username"] = admin.get("username")
                session["is_admin"] = True
                flash(f"Welcome back, {username}!", "success")
                return redirect(url_for("admin_dashboard"))

        error_msg = "Invalid username or password."
        return render_template("login.html", error=error_msg, username=username)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    user = xml.get_user_by_id(session["user_id"])
    return render_template("profile.html", user=user)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return render_template("change_password.html")

        result = xml.change_user_password(session["user_id"], old_password, new_password)
        flash(result["message"], "success" if result["success"] else "danger")
        if result["success"]:
            return redirect(url_for("profile"))

    return render_template("change_password.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    user = xml.get_user_by_id(session["user_id"])
    orders = xml.get_user_orders(session["user_id"])
    return render_template("dashboard.html", user=user, orders=orders)


@app.route("/menu")
@login_required
def menu():
    if session.get("is_admin"):
        flash("Admins cannot browse the customer menu.", "warning")
        return redirect(url_for("admin_dashboard"))

    category = request.args.get("category") or None
    search = request.args.get("search") or None
    items = xml.filter_food_items(category=category, search=search)
    categories = xml.get_menu_categories()
    return render_template(
        "menu.html",
        items=items,
        categories=categories,
        active_category=category,
        search_query=search or "",
    )


@app.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart_route():
    if session.get("is_admin"):
        flash("Admins cannot use the shopping cart.", "warning")
        return redirect(url_for("admin_dashboard"))

    item = {
        "id": request.form.get("id"),
        "name": request.form.get("name"),
        "price": request.form.get("price"),
        "qty": request.form.get("qty", 1),
        "image": request.form.get("image") or DEFAULT_FOOD_IMAGE,
    }

    if not item["id"] or not item["name"]:
        flash("Invalid item.", "danger")
        return redirect(url_for("menu"))

    food_item = xml.get_food_item_by_id(item["id"])
    if food_item and food_item.get("image"):
        item["image"] = food_item.get("image")

    cart_helper.add_to_cart(session, item)
    flash(f"Added {item['name']} to cart.", "success")
    return redirect(url_for("menu"))


@app.route("/cart")
@login_required
def cart():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    cart_items = cart_helper.get_cart(session)
    total = cart_helper.cart_total(session)
    return render_template("cart.html", cart=cart_items, total=total)


@app.route("/remove-from-cart/<item_id>", methods=["POST"])
@login_required
def remove_from_cart_route(item_id):
    cart_helper.remove_from_cart(session, item_id)
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))


@app.route("/clear-cart", methods=["POST"])
@login_required
def clear_cart_route():
    cart_helper.clear_cart(session)
    flash("Cart cleared.", "info")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    cart_items = cart_helper.get_cart(session)
    total = cart_helper.cart_total(session)

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("menu"))

    if request.method == "POST":
        result = xml.create_order(session["user_id"], cart_items, total)
        if result["success"]:
            cart_helper.clear_cart(session)
            flash("Order placed successfully!", "success")
            return redirect(url_for("dashboard"))
        flash(result["message"], "danger")

    return render_template("checkout.html", cart=cart_items, total=total)


@app.route("/orders")
@login_required
def orders():
    if session.get("is_admin"):
        return redirect(url_for("admin_orders"))

    user_orders = xml.get_user_orders(session["user_id"])
    return render_template("orders.html", orders=user_orders)


@app.route("/orders/cancel/<order_id>", methods=["POST"])
@login_required
def cancel_order_route(order_id):
    if session.get("is_admin"):
        return redirect(url_for("admin_orders"))

    # Customer cancellation requests are recorded for admin review
    result = xml.request_order_cancellation(order_id, user_id=session["user_id"])
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("dashboard"))


@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():
    users = xml.get_all_users()
    items = xml.get_all_food_items()
    orders = xml.get_all_orders()
    users_count = len(users)
    items_count = len(items)
    orders_count = len(orders)

    # analytics
    monthly_sales = xml.get_monthly_sales()
    top_products = xml.get_top_products()

    # recent orders (sorted by date desc)
    try:
        recent_orders = sorted(orders, key=lambda o: o.get('date',''), reverse=True)[:6]
    except Exception:
        recent_orders = orders[:6]

    # recent activity logs
    recent_logs = xml.get_all('logs.xml', 'log')

    return render_template(
        "admin_dashboard.html",
        users_count=users_count,
        items_count=items_count,
        orders_count=orders_count,
        monthly_sales=monthly_sales,
        top_products=top_products,
        recent_orders=recent_orders,
        recent_logs=recent_logs,
    )


@app.route("/admin/users")
@admin_required
def admin_users():
    users = xml.get_all_users()
    return render_template("users.html", users=users)


@app.route("/admin/users/delete/<user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    if str(user_id) == "1":
        flash("Cannot delete the primary admin account.", "danger")
        return redirect(url_for("admin_users"))

    result = xml.delete_user(user_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/disable/<user_id>", methods=["POST"])
@admin_required
def admin_toggle_user_disable(user_id):
    if str(user_id) == "1":
        flash("Cannot disable the primary admin account.", "danger")
        return redirect(url_for("admin_users"))

    user = xml.get_user_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin_users"))

    current = user.get('is_disabled') == 'true'
    result = xml.set_user_disabled(user_id, not current)
    flash(result.get('message', 'Action completed'), 'success' if result.get('success') else 'danger')
    return redirect(url_for('admin_users'))


@app.route("/admin/items")
@admin_required
def admin_items():
    items = xml.get_all_food_items()
    return render_template("manage_items.html", items=items)


@app.route("/admin/items/add", methods=["GET", "POST"])
@admin_required
def admin_add_item():
    categories = xml.get_all_categories()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "")
        description = request.form.get("description", "").strip()
        category = request.form.get('category') or None
        prep_time = request.form.get('prep_time') or 30
        stock = request.form.get('stock') or 0
        is_veg = True if request.form.get('is_vegetarian') == 'on' else False
        image_path = DEFAULT_FOOD_IMAGE

        if not name or not price:
            flash("Name and price are required.", "danger")
            return render_template("add_item.html", categories=categories)

        result = xml.add_food_item(name, price, description, image_path, category)
        if not result["success"]:
            flash(result["message"], "danger")
            return render_template("add_item.html", categories=categories)

        uploaded = request.files.get("image")
        if uploaded and uploaded.filename and allowed_image(uploaded.filename):
            image_path = save_food_image(uploaded, result["id"])
            xml.update_food_item(result["id"], name, price, description, image_path, stock=stock, prep_time=prep_time, is_vegetarian=is_veg, category=category)
        else:
            xml.update_food_item(result["id"], name, price, description, image_path, stock=stock, prep_time=prep_time, is_vegetarian=is_veg, category=category)

        flash(result["message"], "success")
        return redirect(url_for("admin_items"))

    return render_template("add_item.html", categories=categories)


@app.route("/admin/items/edit/<item_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_item(item_id):
    item = xml.get_food_item_by_id(item_id)
    if not item:
        flash("Food item not found.", "danger")
        return redirect(url_for("admin_items"))

    categories = xml.get_all_categories()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "")
        description = request.form.get("description", "").strip()
        category = request.form.get('category') or item.get('category')
        prep_time = request.form.get('prep_time') or item.get('prep_time') or 30
        stock = request.form.get('stock') or item.get('stock') or 0
        is_veg = True if request.form.get('is_vegetarian') == 'on' else False
        image_path = item.get("image") or DEFAULT_FOOD_IMAGE

        uploaded = request.files.get("image")
        if uploaded and uploaded.filename and allowed_image(uploaded.filename):
            image_path = save_food_image(uploaded, item_id)

        result = xml.update_food_item(item_id, name, price, description, image_path, stock=stock, prep_time=prep_time, is_vegetarian=is_veg, category=category)
        flash(result["message"], "success" if result["success"] else "danger")
        if result["success"]:
            return redirect(url_for("admin_items"))

    return render_template("edit_item.html", item=item, categories=categories)


@app.route("/admin/items/delete/<item_id>", methods=["POST"])
@admin_required
def admin_delete_item(item_id):
    result = xml.delete_food_item(item_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_items"))


@app.route("/admin/orders")
@admin_required
def admin_orders():
    orders = xml.get_all_orders()
    return render_template("manage_orders.html", orders=orders)


@app.route('/admin/inventory')
@admin_required
def admin_inventory():
    # Reuse manage items view for inventory
    items = xml.get_all_food_items()
    return render_template('manage_items.html', items=items)


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    # Redirect to dashboard (analytics section)
    return redirect('/admin-dashboard#analytics')


@app.route("/admin/orders/view/<order_id>")
@admin_required
def admin_view_order(order_id):
    order = xml.get_by_id('orders.xml', 'order', order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('admin_orders'))
    # load items using get_all and scanning orders.xml directly for items
    # get_by_id returned dict without items, so parse full order node
    tree = xml.load_xml('orders.xml')
    root = tree.getroot()
    items = []
    for o in root.findall('order'):
        id_elem = o.find('id')
        if id_elem is not None and id_elem.text == str(order_id):
            items_elem = o.find('items')
            if items_elem is not None:
                for it in items_elem.findall('item'):
                    itm = {}
                    for child in it:
                        itm[child.tag] = child.text
                    items.append(itm)
            break
    return render_template('view_order.html', order=order, items=items)


@app.route('/admin/orders/edit/<order_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_order(order_id):
    order = xml.get_by_id('orders.xml', 'order', order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('admin_orders'))

    if request.method == 'POST':
        status = request.form.get('status')
        payment_status = request.form.get('payment_status')
        remarks = request.form.get('remarks')
        result = xml.update_order(order_id, status=status, payment_status=payment_status, remarks=remarks)
        if result.get('success'):
            xml.add_log(session.get('user_id', 'system'), 'order_updated', f'Order {order_id} updated by admin')
            flash('Order updated.', 'success')
            return redirect(url_for('admin_view_order', order_id=order_id))
        flash(result.get('message', 'Failed to update'), 'danger')

    # For GET, fetch items
    tree = xml.load_xml('orders.xml')
    root = tree.getroot()
    items = []
    for o in root.findall('order'):
        id_elem = o.find('id')
        if id_elem is not None and id_elem.text == str(order_id):
            items_elem = o.find('items')
            if items_elem is not None:
                for it in items_elem.findall('item'):
                    itm = {}
                    for child in it:
                        itm[child.tag] = child.text
                    items.append(itm)
            break

    return render_template('edit_order.html', order=order, items=items)


@app.route('/admin/orders/invoice/<order_id>')
@admin_required
def admin_invoice(order_id):
    order = xml.get_by_id('orders.xml', 'order', order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('admin_orders'))
    tree = xml.load_xml('orders.xml')
    root = tree.getroot()
    items = []
    for o in root.findall('order'):
        id_elem = o.find('id')
        if id_elem is not None and id_elem.text == str(order_id):
            items_elem = o.find('items')
            if items_elem is not None:
                for it in items_elem.findall('item'):
                    itm = {}
                    for child in it:
                        itm[child.tag] = child.text
                    items.append(itm)
            break
    return render_template('invoice.html', order=order, items=items)


@app.route('/admin/orders/cancellation/respond/<order_id>', methods=['POST'])
@admin_required
def admin_respond_cancellation(order_id):
    action = request.form.get('action')
    approve = True if action == 'approve' else False
    result = xml.respond_order_cancellation(order_id, approve, admin_id=session.get('user_id'))
    flash(result.get('message', 'No action taken'), 'success' if result.get('success') else 'danger')
    return redirect(url_for('admin_orders'))


@app.route('/admin/api/monthly-sales')
@admin_required
def admin_api_monthly_sales():
    data = xml.get_monthly_sales()
    return (jsonify(data))


@app.route('/admin/api/top-products')
@admin_required
def admin_api_top_products():
    data = xml.get_top_products()
    return (jsonify(data))


@app.route("/admin/orders/update/<order_id>/<status>", methods=["POST"])
@admin_required
def admin_update_order(order_id, status):
    allowed = {"pending", "completed", "cancelled"}
    if status not in allowed:
        flash("Invalid order status.", "danger")
        return redirect(url_for("admin_orders"))

    result = xml.update_order_status(order_id, status)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_orders"))


@app.route("/admin/orders/cancel/<order_id>", methods=["POST"])
@admin_required
def admin_cancel_order(order_id):
    result = xml.cancel_order(order_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_orders"))


@app.route("/admin/orders/delete/<order_id>", methods=["POST"])
@admin_required
def admin_delete_order(order_id):
    result = xml.delete_order(order_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_orders"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("server_error.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
