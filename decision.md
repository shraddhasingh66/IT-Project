# EasyCart — Master Architectural & Design Decisions

This document details all technical, architectural, and business logic decisions made during the transformation of **EasyCart** from an initial inventory manager into a full-scale e-commerce storefront.

---

## 1. Project Constraints & Compliance
- **Preserved Existing Structure**: All changes were made directly inside the active workspace directory without initializing Git (`.git` is not created or modified).
- **Zero Heavy Dependencies**: Built entirely on **Python 3**, **Flask**, **SQLite3** (standard library), vanilla **HTML5**, **CSS3**, and **JavaScript (ES6+)**. No heavy front-end build tools, bundlers, or third-party CSS frameworks were introduced.
- **Data Preservation & Migration**: Existing items (`Sample Item` ID 1 and `Phone` ID 2) from `products.json` were preserved and seeded into the persistent SQLite database (`easycart.db`), while `products.json` continues to be maintained in real time for backup compatibility.

---

## 2. System Architecture

```text
Inventory and shopping cart Manager/
├── Backend/                   # Dedicated backend folder
│   ├── app.py                 # Flask REST APIs, business logic & SQLite ORM layer
│   ├── easycart.db            # SQLite database (Products, Users, Orders, Order Items)
│   └── products.json          # Synchronized JSON data store
├── Frontend/
│   ├── index.html             # Single-page e-commerce storefront, modals & drawers
│   └── Style/
│       ├── style.css          # CSS Variables, Light/Dark mode, Responsive grid, Print styles
│       ├── script.js          # Client-side reactivity, cart synchronization, auth & filters
│       └── images/            # 25 Offline-guaranteed vector SVG product images (p1.svg - p25.svg)
├── app.py                     # Root entry point delegating cleanly to Backend/app.py
├── products.json              # Preserved root JSON store
├── requirements.txt           # Dependencies (Flask==3.0.2, werkzeug==3.0.1)
├── README.md                  # Quickstart & Windows/VS Code setup guide
└── decision.md                # Comprehensive architectural specification
```

---

## 3. Database Schema (`easycart.db`)

### 3.1 Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'Electronics',
    price REAL NOT NULL,
    original_price REAL,
    quantity INTEGER NOT NULL DEFAULT 0,
    rating REAL DEFAULT 4.5,
    rating_count INTEGER DEFAULT 50,
    image TEXT,
    description TEXT
);
```

### 3.2 Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 Orders Table
```sql
CREATE TABLE orders (
    id TEXT PRIMARY KEY,
    user_id INTEGER,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_phone TEXT,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    subtotal REAL NOT NULL,
    discount REAL NOT NULL DEFAULT 0,
    delivery_fee REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL,
    coupon_code TEXT,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### 3.4 Order Items Table
```sql
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    unit_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id)
);
```

---

## 4. Key Business Logic & Algorithms

### 4.1 Server-Authoritative Cart Calculation (`/api/cart/calculate`)
To avoid client-side tampering, all price totals, taxes, discounts, and delivery charges are calculated on the backend:
1. Every submitted product ID is verified against the database.
2. The current unit price from the database is used (client prices are ignored).
3. In-stock limits are enforced: requested quantity cannot exceed current inventory.
4. Promotional coupon rules are applied:
   - `WELCOME10`: 10% discount on order subtotal $\ge ₹200$ (capped at ₹500).
   - `SAVE50`: Flat ₹50 off on order subtotal $\ge ₹499$.
   - `FREESHIP`: Waives standard delivery fee of ₹40 for orders $\ge ₹300$.
5. Standard delivery fee is ₹40, automatically waived for any cart subtotal $\ge ₹999$.

### 4.2 Atomic Checkout Transaction (`/api/cart/checkout`)
1. Validates all mandatory customer delivery fields (Name, Phone, Email, Address, City, State, PIN).
2. Performs a pre-flight stock verification for all cart items. If any item is out of stock or over-allocated, the request fails with HTTP 400 without modifying any database records.
3. Generates a unique human-readable Order ID (`EC-XXXXXX`).
4. Atomically records order details, inserts line items, and decrements stock units in the `products` table within a single database transaction.
5. Emits an order confirmation payload used to generate a printable invoice receipt.

---

## 5. UI/UX Decisions & Visual Identity
- **Restrained Commercial Palette**:
  - Light mode: Clean slate-50 background (`#f8fafc`), pure white product cards (`#ffffff`), subtle borders (`#e2e8f0`), deep navy branding (`#1e3a8a`), vibrant blue actions (`#2563eb`), and emerald green checkouts (`#16a34a`).
  - Dark mode: Slate-900 surfaces (`#0b1120`), slate-800 card elevation (`#1e293b`), slate-700 dividers (`#334155`), and high-contrast typography.
- **Modal Visibility & Guest Checkout**:
  - All modals and drawers (`.modal-overlay.hidden`, `.drawer-overlay.hidden`) are strictly suppressed by default with `display: none !important`.
  - The login/account modal has been removed for now. Checkout works seamlessly as guest checkout without requiring any login credentials.
- **Product Presentation**:
  - Uniform `aspect-ratio: 1 / 1` with `object-fit: cover` and fallback placeholders.
  - Clear percentage discount badges (`% OFF`), customer rating badges (`★ 4.7`), and live stock alerts (`Only 2 left`).
- **Navigation & Mobile Adaptation**:
  - Sticky header with responsive search bar, category strip, user greeting, and cart pill badge.
  - Category navigation wraps horizontally with zero scrollbar clutter on mobile.

---

## 6. Security Considerations
- **Password Protection**: Passwords hashed using `werkzeug.security.generate_password_hash` (PBKDF2/SHA-256).
- **Session Security**: Server-side Flask session cookies backed by a configured secret key.
- **XSS Prevention**: All dynamic user-facing strings (product names, descriptions, customer info) pass through client-side HTML entity escaping (`escapeHtml`).
- **SQL Injection Prevention**: All SQL queries utilize parameterized inputs (`?` placeholders).
