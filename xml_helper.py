import xml.etree.ElementTree as ET
import os
from config import XML_PATH
from datetime import datetime

def load_xml(filename='users.xml'):
    """Load XML file from the database directory."""
    file_path = os.path.join(XML_PATH, filename)
    tree = ET.parse(file_path)
    return tree

def save_xml(tree, filename='users.xml'):
    """Save XML tree back to file with proper formatting."""
    file_path = os.path.join(XML_PATH, filename)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

def get_all(filename, tag_name):
    """Retrieve all elements of a specific tag as dictionaries."""
    try:
        tree = load_xml(filename)
        root = tree.getroot()
        items = []
        for item in root.findall(tag_name):
            item_dict = {}
            for child in item:
                item_dict[child.tag] = child.text
            items.append(item_dict)
        return items
    except Exception as e:
        print(f'Error reading {filename}: {e}')
        return []

def get_by_id(filename, tag_name, item_id):
    """Retrieve a specific item by ID."""
    try:
        tree = load_xml(filename)
        root = tree.getroot()
        for item in root.findall(tag_name):
            id_elem = item.find('id')
            if id_elem is not None and id_elem.text == str(item_id):
                item_dict = {}
                for child in item:
                    item_dict[child.tag] = child.text
                return item_dict
        return None
    except Exception as e:
        print(f'Error reading {filename}: {e}')
        return None

def field_exists(filename, tag_name, field_name, value):
    """Check if a field value already exists (for unique constraints)."""
    try:
        items = get_all(filename, tag_name)
        for item in items:
            if item.get(field_name) == value:
                return True
        return False
    except Exception as e:
        print(f'Error checking field: {e}')
        return False

def get_next_id(filename, tag_name):
    """Get the next available ID for a new record."""
    try:
        items = get_all(filename, tag_name)
        if not items:
            return 1
        max_id = max(int(item.get('id', 0)) for item in items if 'id' in item)
        return max_id + 1
    except Exception as e:
        print(f'Error getting next ID: {e}')
        return 1

# USER OPERATIONS
def get_all_users():
    """Get all users from users.xml."""
    return get_all('users.xml', 'user')

def get_user_by_id(user_id):
    """Get a specific user by ID."""
    return get_by_id('users.xml', 'user', user_id)

def user_exists(username):
    """Check if username already exists."""
    return field_exists('users.xml', 'user', 'username', username)

def add_user(username, password, is_admin=False):
    """Add a new user to users.xml with unique constraint checking."""
    try:
        if user_exists(username):
            return {'success': False, 'message': 'Username already exists'}
        
        tree = load_xml('users.xml')
        root = tree.getroot()
        
        user_id = get_next_id('users.xml', 'user')
        
        user = ET.Element('user')
        ET.SubElement(user, 'id').text = str(user_id)
        ET.SubElement(user, 'username').text = username
        ET.SubElement(user, 'password').text = password
        ET.SubElement(user, 'is_admin').text = 'true' if is_admin else 'false'
        ET.SubElement(user, 'is_disabled').text = 'false'
        
        root.append(user)
        save_xml(tree, 'users.xml')
        return {'success': True, 'message': 'User added successfully', 'id': user_id}
    except Exception as e:
        print(f'Error adding user: {e}')
        return {'success': False, 'message': str(e)}

def delete_user(user_id):
    """Delete a user by ID."""
    try:
        tree = load_xml('users.xml')
        root = tree.getroot()
        
        for user in root.findall('user'):
            id_elem = user.find('id')
            if id_elem is not None and id_elem.text == str(user_id):
                root.remove(user)
                save_xml(tree, 'users.xml')
                return {'success': True, 'message': 'User deleted successfully'}
        
        return {'success': False, 'message': 'User not found'}
    except Exception as e:
        print(f'Error deleting user: {e}')
        return {'success': False, 'message': str(e)}


def set_user_disabled(user_id, disabled=True):
    """Set or unset the disabled flag for a user."""
    try:
        tree = load_xml('users.xml')
        root = tree.getroot()
        for user in root.findall('user'):
            id_elem = user.find('id')
            if id_elem is not None and id_elem.text == str(user_id):
                dis = user.find('is_disabled')
                if dis is None:
                    dis = ET.SubElement(user, 'is_disabled')
                dis.text = 'true' if disabled else 'false'
                save_xml(tree, 'users.xml')
                return {'success': True, 'message': 'User disabled' if disabled else 'User enabled'}
        return {'success': False, 'message': 'User not found'}
    except Exception as e:
        print(f'Error setting user disabled: {e}')
        return {'success': False, 'message': str(e)}

def change_user_password(user_id, old_password, new_password):
    """Change a user's password after verifying the current one."""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}

        if user.get('password') != old_password:
            return {'success': False, 'message': 'Current password is incorrect'}

        if len(new_password) < 6:
            return {'success': False, 'message': 'New password must be at least 6 characters'}

        tree = load_xml('users.xml')
        root = tree.getroot()

        for user_elem in root.findall('user'):
            id_elem = user_elem.find('id')
            if id_elem is not None and id_elem.text == str(user_id):
                user_elem.find('password').text = new_password
                save_xml(tree, 'users.xml')
                return {'success': True, 'message': 'Password changed successfully'}

        return {'success': False, 'message': 'User not found'}
    except Exception as e:
        print(f'Error changing password: {e}')
        return {'success': False, 'message': str(e)}

# FOOD ITEMS OPERATIONS
MENU_CATEGORIES = [
    'Appetizers',
    'Beverages',
    'Burgers',
    'Desserts',
    'Pizzas',
    'Salads',
]

def get_menu_categories():
    return MENU_CATEGORIES

def get_all_food_items():
    """Get all food items from food_items.xml."""
    return get_all('food_items.xml', 'item')

def filter_food_items(category=None, search=None):
    """Filter food items by category and/or search term."""
    items = get_all_food_items()
    if category:
        items = [item for item in items if item.get('category') == category]
    if search:
        term = search.strip().lower()
        if term:
            items = [
                item for item in items
                if term in item.get('name', '').lower()
                or term in item.get('description', '').lower()
                or term in item.get('category', '').lower()
            ]
    return items

def get_food_item_by_id(item_id):
    """Get a specific food item by ID."""
    return get_by_id('food_items.xml', 'item', item_id)

def add_food_item(name, price, description, image='uploads/food/magherita pizza.jpg', category='Pizzas'):
    """Add a new food item to food_items.xml."""
    try:
        tree = load_xml('food_items.xml')
        root = tree.getroot()
        item_id = get_next_id('food_items.xml', 'item')

        item = ET.Element('item')
        ET.SubElement(item, 'id').text = str(item_id)
        ET.SubElement(item, 'name').text = name
        ET.SubElement(item, 'price').text = str(price)
        ET.SubElement(item, 'description').text = description
        ET.SubElement(item, 'category').text = category or 'Pizzas'
        ET.SubElement(item, 'is_vegetarian').text = 'false'
        ET.SubElement(item, 'image').text = image or 'uploads/food/magherita pizza.jpg'
        ET.SubElement(item, 'stock').text = '0'
        ET.SubElement(item, 'prep_time').text = '30'
        ET.SubElement(item, 'availability').text = 'available'

        root.append(item)
        save_xml(tree, 'food_items.xml')
        return {'success': True, 'message': 'Food item added successfully', 'id': item_id}
    except Exception as e:
        print(f'Error adding food item: {e}')
        return {'success': False, 'message': str(e)}

def update_food_item(item_id, name, price, description, image=None, stock=None, prep_time=None, availability=None, is_vegetarian=None, category=None):
    """Update a food item's details."""
    try:
        tree = load_xml('food_items.xml')
        root = tree.getroot()
        
        for item in root.findall('item'):
            id_elem = item.find('id')
            if id_elem is not None and id_elem.text == str(item_id):
                item.find('name').text = name
                item.find('price').text = str(price)
                item.find('description').text = description
                if image:
                    image_elem = item.find('image')
                    if image_elem is None:
                        image_elem = ET.SubElement(item, 'image')
                    image_elem.text = image
                elif item.find('image') is None:
                    ET.SubElement(item, 'image').text = 'uploads/food/magherita pizza.jpg'

                # ensure optional fields exist and update if provided
                if item.find('stock') is None:
                    ET.SubElement(item, 'stock').text = '0'
                if stock is not None:
                    item.find('stock').text = str(stock)

                if item.find('prep_time') is None:
                    ET.SubElement(item, 'prep_time').text = '30'
                if prep_time is not None:
                    item.find('prep_time').text = str(prep_time)

                if item.find('availability') is None:
                    ET.SubElement(item, 'availability').text = 'available'
                if availability is not None:
                    item.find('availability').text = availability

                if item.find('is_vegetarian') is None:
                    ET.SubElement(item, 'is_vegetarian').text = 'false'
                if is_vegetarian is not None:
                    item.find('is_vegetarian').text = 'true' if is_vegetarian else 'false'

                if category is not None:
                    cat_elem = item.find('category')
                    if cat_elem is None:
                        ET.SubElement(item, 'category').text = category
                    else:
                        cat_elem.text = category
                save_xml(tree, 'food_items.xml')
                return {'success': True, 'message': 'Food item updated successfully'}
        
        return {'success': False, 'message': 'Food item not found'}
    except Exception as e:
        print(f'Error updating food item: {e}')
        return {'success': False, 'message': str(e)}

def delete_food_item(item_id):
    """Delete a food item by ID."""
    try:
        tree = load_xml('food_items.xml')
        root = tree.getroot()
        
        for item in root.findall('item'):
            id_elem = item.find('id')
            if id_elem is not None and id_elem.text == str(item_id):
                root.remove(item)
                save_xml(tree, 'food_items.xml')
                return {'success': True, 'message': 'Food item deleted successfully'}
        
        return {'success': False, 'message': 'Food item not found'}
    except Exception as e:
        print(f'Error deleting food item: {e}')
        return {'success': False, 'message': str(e)}

# ORDER OPERATIONS
def create_order(user_id, items, total, payment_method=None,
                 delivery_address=None, city=None, state=None,
                 postal_code=None, special_instructions=None):
    """Create a new order with multiple items."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        
        order_id = get_next_id('orders.xml', 'order')
        
        order = ET.Element('order')
        ET.SubElement(order, 'id').text = str(order_id)
        ET.SubElement(order, 'user_id').text = str(user_id)
        ET.SubElement(order, 'total').text = str(total)
        ET.SubElement(order, 'status').text = 'pending'
        # store payment method and initialize payment status
        ET.SubElement(order, 'payment_method').text = payment_method or 'cod'
        ET.SubElement(order, 'payment_status').text = 'pending'
        # delivery info
        ET.SubElement(order, 'delivery_address').text = delivery_address or ''
        ET.SubElement(order, 'city').text = city or ''
        ET.SubElement(order, 'state').text = state or ''
        ET.SubElement(order, 'postal_code').text = postal_code or ''
        ET.SubElement(order, 'special_instructions').text = special_instructions or ''
        ET.SubElement(order, 'date').text = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        items_elem = ET.SubElement(order, 'items')
        for item in items:
            item_elem = ET.SubElement(items_elem, 'item')
            ET.SubElement(item_elem, 'id').text = str(item.get('id'))
            ET.SubElement(item_elem, 'name').text = item.get('name')
            ET.SubElement(item_elem, 'price').text = str(item.get('price'))
            ET.SubElement(item_elem, 'quantity').text = str(item.get('qty', 1))
        
        root.append(order)
        save_xml(tree, 'orders.xml')
        return {'success': True, 'message': 'Order created successfully', 'id': order_id}
    except Exception as e:
        print(f'Error creating order: {e}')
        return {'success': False, 'message': str(e)}

def get_all_orders():
    """Get all orders."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        orders = []
        for order in root.findall('order'):
            order_dict = {}
            for child in order:
                if child.tag != 'items':
                    order_dict[child.tag] = child.text
            orders.append(order_dict)
        return orders
    except Exception as e:
        print(f'Error reading orders: {e}')
        return []

def get_user_orders(user_id):
    """Get all orders for a specific user."""
    try:
        all_orders = get_all_orders()
        return [order for order in all_orders if order.get('user_id') == str(user_id)]
    except Exception as e:
        print(f'Error reading user orders: {e}')
        return []

def update_order_status(order_id, status):
    """Update the status of an order."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        
        for order in root.findall('order'):
            id_elem = order.find('id')
            if id_elem is not None and id_elem.text == str(order_id):
                order.find('status').text = status
                save_xml(tree, 'orders.xml')
                return {'success': True, 'message': 'Order status updated successfully'}
        
        return {'success': False, 'message': 'Order not found'}
    except Exception as e:
        print(f'Error updating order: {e}')
        return {'success': False, 'message': str(e)}

def cancel_order(order_id, user_id=None):
    """Cancel a pending order. Optionally restrict to a specific user."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()

        for order in root.findall('order'):
            id_elem = order.find('id')
            if id_elem is None or id_elem.text != str(order_id):
                continue

            if user_id is not None:
                user_elem = order.find('user_id')
                if user_elem is None or user_elem.text != str(user_id):
                    return {'success': False, 'message': 'Order not found'}

            status_elem = order.find('status')
            if status_elem is None or status_elem.text != 'pending':
                return {'success': False, 'message': 'Only pending orders can be cancelled'}

            status_elem.text = 'cancelled'
            save_xml(tree, 'orders.xml')
            return {'success': True, 'message': 'Order cancelled successfully'}

        return {'success': False, 'message': 'Order not found'}
    except Exception as e:
        print(f'Error cancelling order: {e}')
        return {'success': False, 'message': str(e)}

def delete_order(order_id):
    """Permanently delete an order by ID."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()

        for order in root.findall('order'):
            id_elem = order.find('id')
            if id_elem is not None and id_elem.text == str(order_id):
                root.remove(order)
                save_xml(tree, 'orders.xml')
                return {'success': True, 'message': 'Order deleted successfully'}

        return {'success': False, 'message': 'Order not found'}
    except Exception as e:
        print(f'Error deleting order: {e}')
        return {'success': False, 'message': str(e)}

def request_order_cancellation(order_id, user_id):
    """Customer requests cancellation: set status to 'cancellation_requested' and save previous_status."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()

        for order in root.findall('order'):
            id_elem = order.find('id')
            if id_elem is None or id_elem.text != str(order_id):
                continue

            user_elem = order.find('user_id')
            if user_elem is None or user_elem.text != str(user_id):
                return {'success': False, 'message': 'Order not found'}

            status_elem = order.find('status')
            if status_elem is None:
                return {'success': False, 'message': 'Order has no status'}

            current = status_elem.text or ''
            if current.lower() in ('cancelled', 'delivered'):
                return {'success': False, 'message': 'Cannot request cancellation for this order'}

            # Save previous status
            prev = order.find('previous_status')
            if prev is None:
                prev = ET.SubElement(order, 'previous_status')
            prev.text = current

            status_elem.text = 'cancellation_requested'
            save_xml(tree, 'orders.xml')
            return {'success': True, 'message': 'Cancellation requested'}

        return {'success': False, 'message': 'Order not found'}
    except Exception as e:
        print(f'Error requesting cancellation: {e}')
        return {'success': False, 'message': str(e)}


def respond_order_cancellation(order_id, approve, admin_id=None):
    """Admin responds to a cancellation request. Approve -> cancelled; Reject -> restore previous_status."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()

        for order in root.findall('order'):
            id_elem = order.find('id')
            if id_elem is None or id_elem.text != str(order_id):
                continue

            status_elem = order.find('status')
            if status_elem is None or status_elem.text != 'cancellation_requested':
                return {'success': False, 'message': 'No cancellation request pending for this order'}

            prev = order.find('previous_status')
            if approve:
                status_elem.text = 'cancelled'
                # keep previous_status for history
                add_log(admin_id or 'system', 'cancellation_approved', f'Order {order_id} approved for cancellation')
            else:
                # restore previous status if available
                if prev is not None and prev.text:
                    status_elem.text = prev.text
                else:
                    status_elem.text = 'pending'
                # remove previous_status node
                if prev is not None:
                    order.remove(prev)
                add_log(admin_id or 'system', 'cancellation_rejected', f'Order {order_id} cancellation rejected')

            save_xml(tree, 'orders.xml')
            return {'success': True, 'message': 'Cancellation response saved'}

        return {'success': False, 'message': 'Order not found'}
    except Exception as e:
        print(f'Error responding to cancellation: {e}')
        return {'success': False, 'message': str(e)}


def add_log(admin_id, action, details):
    """Append an admin activity log to logs.xml."""
    try:
        tree = load_xml('logs.xml')
        root = tree.getroot()

        log_id = get_next_id('logs.xml', 'log')
        log = ET.Element('log')
        ET.SubElement(log, 'id').text = str(log_id)
        ET.SubElement(log, 'admin_id').text = str(admin_id)
        ET.SubElement(log, 'action').text = action
        ET.SubElement(log, 'details').text = details
        ET.SubElement(log, 'date').text = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        root.append(log)
        save_xml(tree, 'logs.xml')
        return {'success': True}
    except Exception as e:
        print(f'Error adding log: {e}')
        return {'success': False, 'message': str(e)}


def get_all_categories():
    return get_all('categories.xml', 'category')


def add_category(name):
    try:
        tree = load_xml('categories.xml')
        root = tree.getroot()
        cat_id = get_next_id('categories.xml', 'category')
        cat = ET.Element('category')
        ET.SubElement(cat, 'id').text = str(cat_id)
        ET.SubElement(cat, 'name').text = name
        ET.SubElement(cat, 'date').text = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        root.append(cat)
        save_xml(tree, 'categories.xml')
        return {'success': True, 'id': cat_id}
    except Exception as e:
        print(f'Error adding category: {e}')
        return {'success': False, 'message': str(e)}


def update_category(cat_id, name):
    try:
        tree = load_xml('categories.xml')
        root = tree.getroot()
        for cat in root.findall('category'):
            id_elem = cat.find('id')
            if id_elem is not None and id_elem.text == str(cat_id):
                cat.find('name').text = name
                save_xml(tree, 'categories.xml')
                return {'success': True}
        return {'success': False, 'message': 'Category not found'}
    except Exception as e:
        print(f'Error updating category: {e}')
        return {'success': False, 'message': str(e)}


def delete_category(cat_id):
    try:
        tree = load_xml('categories.xml')
        root = tree.getroot()
        for cat in root.findall('category'):
            id_elem = cat.find('id')
            if id_elem is not None and id_elem.text == str(cat_id):
                root.remove(cat)
                save_xml(tree, 'categories.xml')
                return {'success': True}
        return {'success': False, 'message': 'Category not found'}
    except Exception as e:
        print(f'Error deleting category: {e}')
        return {'success': False, 'message': str(e)}


def get_all_admins():
    return get_all('admins.xml', 'admin')


def add_admin(username, password):
    try:
        tree = load_xml('admins.xml')
        root = tree.getroot()
        admin_id = get_next_id('admins.xml', 'admin')
        admin = ET.Element('admin')
        ET.SubElement(admin, 'id').text = str(admin_id)
        ET.SubElement(admin, 'username').text = username
        ET.SubElement(admin, 'password').text = password
        ET.SubElement(admin, 'date').text = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        root.append(admin)
        save_xml(tree, 'admins.xml')
        return {'success': True, 'id': admin_id}
    except Exception as e:
        print(f'Error adding admin: {e}')
        return {'success': False, 'message': str(e)}


def get_monthly_sales():
    """Return monthly sales aggregated from orders.xml (completed/delivered)."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        sales = {}
        for order in root.findall('order'):
            status = (order.find('status').text or '').lower() if order.find('status') is not None else ''
            if status not in ('completed', 'delivered'):
                continue
            date_text = order.find('date').text if order.find('date') is not None else ''
            if not date_text:
                continue
            month = date_text[:7]  # YYYY-MM
            total = float(order.find('total').text or 0)
            sales[month] = sales.get(month, 0) + total
        # convert to sorted list of tuples
        result = [{'month': m, 'total': sales[m]} for m in sorted(sales.keys())]
        return result
    except Exception as e:
        print(f'Error computing monthly sales: {e}')
        return []


def get_weekly_sales():
    """Return weekly sales aggregated from orders.xml (ISO year-week)."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        sales = {}
        for order in root.findall('order'):
            status = (order.find('status').text or '').lower() if order.find('status') is not None else ''
            if status not in ('completed', 'delivered'):
                continue
            date_text = order.find('date').text if order.find('date') is not None else ''
            if not date_text:
                continue
            try:
                dt = datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
            except Exception:
                # fallback: try parse date-only or skip
                try:
                    dt = datetime.strptime(date_text[:10], '%Y-%m-%d')
                except Exception:
                    continue
            year, week, _ = dt.isocalendar()
            key = f"{year}-W{week:02d}"
            total = float(order.find('total').text or 0)
            sales[key] = sales.get(key, 0) + total
        result = [{'week': k, 'total': sales[k]} for k in sorted(sales.keys())]
        return result
    except Exception as e:
        print(f'Error computing weekly sales: {e}')
        return []


def get_daily_sales():
    """Return daily sales aggregated from orders.xml (YYYY-MM-DD)."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        sales = {}
        for order in root.findall('order'):
            status = (order.find('status').text or '').lower() if order.find('status') is not None else ''
            if status not in ('completed', 'delivered'):
                continue
            date_text = order.find('date').text if order.find('date') is not None else ''
            if not date_text:
                continue
            day = date_text[:10]
            total = float(order.find('total').text or 0)
            sales[day] = sales.get(day, 0) + total
        result = [{'day': d, 'total': sales[d]} for d in sorted(sales.keys())]
        return result
    except Exception as e:
        print(f'Error computing daily sales: {e}')
        return []


def get_top_products(limit=5):
    """Return top selling products by quantity in orders.xml."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        counts = {}
        for order in root.findall('order'):
            items = order.find('items')
            if items is None:
                continue
            for item in items.findall('item'):
                name = item.find('name').text if item.find('name') is not None else 'Unknown'
                qty = int(item.find('quantity').text or 0)
                counts[name] = counts.get(name, 0) + qty
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{'name': name, 'quantity': qty} for name, qty in sorted_items[:limit]]
    except Exception as e:
        print(f'Error computing top products: {e}')
        return []


def update_order(order_id, status=None, payment_status=None, remarks=None):
    """Update multiple order fields and save back to orders.xml."""
    try:
        tree = load_xml('orders.xml')
        root = tree.getroot()
        for order in root.findall('order'):
            id_elem = order.find('id')
            if id_elem is None or id_elem.text != str(order_id):
                continue

            if status is not None:
                st = order.find('status')
                if st is None:
                    st = ET.SubElement(order, 'status')
                st.text = status

            if payment_status is not None:
                ps = order.find('payment_status')
                if ps is None:
                    ps = ET.SubElement(order, 'payment_status')
                ps.text = payment_status

            if remarks is not None:
                r = order.find('remarks')
                if r is None:
                    r = ET.SubElement(order, 'remarks')
                r.text = remarks

            save_xml(tree, 'orders.xml')
            return {'success': True}

        return {'success': False, 'message': 'Order not found'}
    except Exception as e:
        print(f'Error updating order: {e}')
        return {'success': False, 'message': str(e)}
