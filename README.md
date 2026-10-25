# EasyCart — Modern E-Commerce Storefront

An online shopping web platform built with Python, Flask, SQLite, and vanilla HTML/CSS/JavaScript. Inspired by the clean, product-first experience of modern retail sites with a distinctive EasyCart visual identity.

---

## Key Features

1. **Product Discovery & Catalogue**:
   - 8 product categories: *Electronics, Grocery, Fashion, Home & Kitchen, Beauty & Personal Care, Books & Stationery, Sports & Fitness, Toys & Accessories*.
   - Live search by product name and description.
   - Dynamic sorting: *Price (Low to High), Price (High to Low), Highest Discount, Top Rated, Name (A-Z)*.
   - Price range and in-stock filters.
   - Product details view with high-res imagery, rating reviews, quantity stepper, stock status, and related recommendations.

2. **Persistent Shopping Cart**:
   - Dedicated cart drawer accessible from anywhere on the site.
   - Client persistence via `localStorage` with automated server-side verification.
   - Steppers with strict inventory limits (prevents adding more than available stock).
   - Dynamic subtotal, discount, delivery fee, and grand total calculations.

3. **Promotions & Demonstration Coupons**:
   - `WELCOME10`: 10% off on orders above ₹200 (Max discount ₹500).
   - `SAVE50`: Flat ₹50 off on orders above ₹499.
   - `FREESHIP`: Free standard delivery on orders above ₹300 (Standard delivery is free on all orders over ₹999).

4. **Checkout & Order Invoicing**:
   - Delivery address validation.
   - Simulated payment selection (*Cash on Delivery*, *Demo UPI*, *Demo Card*).
   - Atomic inventory deduction upon successful checkout.
   - Printable order invoice receipt modal (`window.print()`).

5. **User Accounts & Order History**:
   - Secure customer registration and login (passwords hashed with PBKDF2/SHA-256).
   - Session-backed account menu.
   - Customer-restricted order history view showing all past purchases.

6. **Light & Dark Theme**:
   - Complete CSS variables theme switcher with preference persistence.

---

##  Quickstart for Windows & VS Code

### 1. Open Project in VS Code
Open VS Code, press `Ctrl+O` (or `File -> Open Folder...`), and select:
```text
C:\Users\shraddha\Downloads\Inventory and shopping cart Manager
```

### 2. Verify or Install Dependencies
Open a PowerShell or Command Prompt terminal in VS Code (`Ctrl+` `~`) and run:
```powershell
pip install -r requirements.txt
```

*(Note: SQLite is built into Python standard library; no extra database installations are needed).*

### 3. Start the Web Server
Run:
```powershell
python app.py
```

You should see output similar to:
```text
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 4. Open in Your Browser
Visit:
```text
http://127.0.0.1:5000/
```

---

## Demonstration Credentials & Coupons

- **Coupons**:
  - `WELCOME10` — 10% discount on orders $\ge ₹200$.
  - `SAVE50` — ₹50 discount on orders $\ge ₹499$.
  - `FREESHIP` — Free shipping on orders $\ge ₹300$.
- **Test User**:
  - You can register any new test account directly through the **Sign In** modal in the header.

---

## Project Structure

```text
Inventory and shopping cart Manager/
├── app.py                     # Flask application, REST APIs, cart logic & SQLite access
├── easycart.db                # SQLite database (Products, Users, Orders, Order Items)
├── products.json              # Preserved JSON data backup
├── requirements.txt           # Dependencies (Flask, Werkzeug)
├── decision.md                # Full architectural and implementation documentation
├── README.md                  # Setup & usage instructions
└── Frontend/
    ├── index.html             # Storefront template, modals, drawers & invoice
    └── Style/
        ├── style.css          # CSS Variables, Light/Dark mode, Print styles
        └── script.js          # Client-side reactivity, cart engine & auth
```

