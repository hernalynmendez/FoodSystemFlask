# Food Order System - README

## Project Description

A Full-Functional Web System built with Python Flask and XML Database that demonstrates proficiency in Data Persistence and CRUD operations on XML using Python's DOM manipulation capabilities.

## Features

### User Features
- 👤 User Registration with unique username validation
- 🔐 Secure Login and Session Management
- 🍽️ Browse food menu with descriptions and prices
- 🛒 Shopping cart management (add/remove items)
- 💳 Order checkout and placement
- 📋 View order history and status
- 📞 Real-time order tracking

### Admin Features
- 📊 Admin Dashboard with statistics
- 👥 User Management (view, delete users)
- 🍕 Food Item Management (add, edit, delete items)
- 📦 Order Management (view, update status)
- 🔍 System analytics and monitoring

## Technology Stack

- **Backend:** Python 3.14 with Flask Framework
- **Database:** XML (xml.etree.ElementTree)
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Session Management:** Flask Sessions
- **File I/O:** XML file persistence

## Project Structure

```
FoodSystem_Flask/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── xml_helper.py                   # XML CRUD operations
├── TECHNICAL_DOCUMENTATION.md      # Complete technical docs
├── README.md                       # This file
├── core/
│   ├── __init__.py
│   ├── auth.py                     # Authentication logic
│   ├── cart.py                     # Cart management
│   └── orders.py                   # Order management
├── xml_db/
│   ├── users.xml                   # User records
│   ├── food_items.xml              # Menu items
│   ├── orders.xml                  # Order records
│   └── database.xml                # Schema reference
├── templates/
│   ├── base.html                   # Base template
│   ├── index.html                  # Home page
│   ├── login.html                  # Login form
│   ├── register.html               # Registration form
│   ├── menu.html                   # Menu display
│   ├── cart.html                   # Shopping cart
│   ├── checkout.html               # Order checkout
│   ├── dashboard.html              # User dashboard
│   ├── admin_dashboard.html        # Admin dashboard
│   ├── users.html                  # User management
│   ├── manage_items.html           # Item management
│   ├── add_item.html               # Add item form
│   ├── edit_item.html              # Edit item form
│   ├── manage_orders.html          # Order management
│   ├── orders.html                 # User orders
│   ├── 404.html                    # Error page
│   └── 500.html                    # Server error page
└── statistic/
    └── style.css                   # Custom styles
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or extract the project**
   ```bash
   cd FoodSystem_Flask
   ```

2. **Create virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open browser and go to: http://localhost:5000
   - Or directly: http://127.0.0.1:5000

## Demo Credentials

### Admin Account
- **Username:** admin
- **Password:** admin
- **Access:** Admin dashboard, user management, item management

### Regular User Account
- **Username:** demouser
- **Password:** password123
- **Access:** Browse menu, place orders, view history

## Key Features Implementation

### 1. XML Data Persistence
- All data (users, food items, orders) stored in XML files
- Immediate write to disk after every operation
- Data survives application restarts

### 2. Unique Constraint Validation
- Username uniqueness enforced before user creation
- Python validates fields before appending to XML

### 3. CRUD Operations
- **Create:** add_user(), add_food_item(), create_order()
- **Read:** get_all_users(), get_all_food_items(), get_all_orders()
- **Update:** update_food_item(), update_order_status()
- **Delete:** delete_user(), delete_food_item()

### 4. Session Management
- Secure login system with session tracking
- Different dashboards for admin vs. regular users
- Shopping cart stored in session

### 5. Role-Based Access Control
- Regular users can: browse menu, add items to cart, place orders
- Admins can: manage users, manage items, manage orders
- Unauthorized access redirected to appropriate page

## API Routes

### Public Routes
- `GET /` - Home page
- `GET/POST /register` - User registration
- `GET/POST /login` - User login

### User Routes (Authentication Required)
- `GET /menu` - Browse food menu
- `GET /cart` - View shopping cart
- `POST /add-to-cart` - Add item to cart
- `POST /remove-from-cart/<id>` - Remove item from cart
- `GET/POST /checkout` - Order checkout
- `GET /dashboard` - User dashboard
- `GET /logout` - Logout

### Admin Routes (Admin Only)
- `GET /admin-dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `POST /admin/users/delete/<id>` - Delete user
- `GET /admin/items` - Manage food items
- `GET/POST /admin/items/add` - Add food item
- `GET/POST /admin/items/edit/<id>` - Edit food item
- `POST /admin/items/delete/<id>` - Delete food item
- `GET /admin/orders` - Manage orders
- `POST /admin/orders/update/<id>/<status>` - Update order status

## XML File Structures

### users.xml
```xml
<users>
    <user>
        <id>1</id>
        <username>admin</username>
        <password>admin</password>
        <is_admin>true</is_admin>
    </user>
</users>
```

### food_items.xml
```xml
<food_items>
    <item>
        <id>1</id>
        <name>Cheese Pizza</name>
        <price>199</price>
        <description>Classic cheese pizza</description>
    </item>
</food_items>
```

### orders.xml
```xml
<orders>
    <order>
        <id>1</id>
        <user_id>2</user_id>
        <total>548.00</total>
        <status>pending</status>
        <date>2026-05-31 14:30:00</date>
        <items>
            <item>
                <id>1</id>
                <name>Cheese Pizza</name>
                <price>199.00</price>
                <quantity>2</quantity>
            </item>
        </items>
    </order>
</orders>
```

## Important Functions

### User Operations (xml_helper.py)
- `add_user(username, password, is_admin=False)` - Create new user
- `get_all_users()` - Retrieve all users
- `user_exists(username)` - Check username uniqueness
- `delete_user(user_id)` - Remove user by ID
- `get_user_by_id(user_id)` - Get specific user

### Food Item Operations (xml_helper.py)
- `add_food_item(name, price, description)` - Add menu item
- `get_all_food_items()` - Get all menu items
- `update_food_item(item_id, name, price, description)` - Edit item
- `delete_food_item(item_id)` - Remove item
- `get_food_item_by_id(item_id)` - Get specific item

### Order Operations (xml_helper.py)
- `create_order(user_id, items, total)` - Place new order
- `get_all_orders()` - Get all orders
- `get_user_orders(user_id)` - Get user's orders
- `update_order_status(order_id, status)` - Update order status

## Security Notes

⚠️ **Important:** This is a demonstration project. For production use:
- Implement password hashing (bcrypt, argon2)
- Use HTTPS/SSL encryption
- Implement CSRF protection
- Add input validation and sanitization
- Use database instead of XML for better performance
- Implement proper authentication tokens
- Add role-based permission checks

## Testing

To verify the system works:

1. **Test User Registration**
   - Register a new user with unique username
   - Verify unique constraint works (try duplicate username)

2. **Test Login**
   - Login with admin credentials
   - Login with regular user credentials

3. **Test Shopping**
   - Add items to cart
   - View cart
   - Place order

4. **Test Admin Features**
   - Add a new food item
   - Edit existing item
   - Delete an item
   - View user list

5. **Test Data Persistence**
   - Place an order
   - Restart the Flask server
   - Verify order still exists

## Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, port=5001)  # Use different port
```

### XML File Not Found
- Ensure xml_db folder exists in project directory
- Check file permissions

### Session Issues
- Clear browser cookies
- Ensure secret_key is set in app.py

## Future Enhancements

- 🔐 Add password hashing
- 📱 Mobile app version
- 🗄️ Database migration (SQL)
- 💳 Payment gateway integration
- 📧 Email notifications
- 🗺️ Delivery address management
- ⭐ Product reviews and ratings
- 🔍 Advanced search and filtering

## Support & Documentation

For detailed technical information, see:
- `TECHNICAL_DOCUMENTATION.md` - Complete system architecture, XML schemas, and function dictionary

## License

Educational Project - Use for learning purposes

## Authors

Group Members: [Add your names here]

Date: May 31, 2026

---

**Happy Ordering! 🍕**
