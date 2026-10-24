import os
import sys
import json
import sqlite3
import random
import logging
from flask import Flask, render_template, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('easycart')

# Path configuration for modular Backend structure
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'Frontend')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'Frontend', 'Style')
BANNER_DIR = os.path.join(PROJECT_ROOT, 'banner')
DATA_FILE = os.path.join(BACKEND_DIR, 'products.json')
DB_FILE = os.path.join(BACKEND_DIR, 'easycart.db')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR, static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'easycart-secret-key-2026-development')

# Route to serve banner images with validation
@app.route('/banner/<path:filename>')
def serve_banner(filename):
    from flask import send_from_directory, abort
    try:
        return send_from_directory(BANNER_DIR, filename)
    except Exception as e:
        logger.error(f"Error serving banner {filename}: {e}")
        abort(404)



# Predefined Demonstration Coupons
COUPONS = {
    'WELCOME10': {
        'code': 'WELCOME10',
        'type': 'percentage',
        'value': 10,  # 10% off
        'min_order': 200,
        'max_discount': 500,
        'description': '10% off on orders above ₹200 (Max discount ₹500)'
    },
    'SAVE50': {
        'code': 'SAVE50',
        'type': 'flat',
        'value': 50,  # ₹50 off
        'min_order': 499,
        'max_discount': 50,
        'description': 'Flat ₹50 off on orders above ₹499'
    },
    'FREESHIP': {
        'code': 'FREESHIP',
        'type': 'free_shipping',
        'value': 0,
        'min_order': 300,
        'max_discount': 40,
        'description': 'Free Delivery on orders above ₹300'
    }
}

DELIVERY_FEE = 40.0
FREE_DELIVERY_THRESHOLD = 999.0

# 25 Products across 8 categories with image_url support and offline fallbacks
SEED_PRODUCTS = [
    # Electronics (incorporates legacy items 1 and 2)
    {
        "id": 1,
        "name": "USB-C Multiport Hub",
        "category": "Electronics",
        "price": 1499.00,
        "original_price": 2499.00,
        "quantity": 10,
        "rating": 4.5,
        "rating_count": 128,
        "image": "/static/images/p1.svg",
        "image_url": "https://m.media-amazon.com/images/I/618Cnb3N0qL.jpg",
        "description": "7-in-1 Aluminium Type-C Hub with 4K HDMI, 3 USB 3.0 ports, SD/TF card reader, and 100W Power Delivery."
    },
    {
        "id": 2,
        "name": "Samsung Galaxy S26 Ultra",
        "category": "Electronics",
        "price": 115999.00,
        "original_price": 130999.00,
        "quantity": 10,
        "rating": 4.8,
        "rating_count": 1412,
        "image": "/static/images/p2.svg",
        "image_url": "https://rukminim3.flixcart.com/image/480/640/xif0q/mobile/d/0/x/-resized-original-imahhyzrnhgzvdk4.jpeg?q=90",
        "description": "a flagship smartphone featuring a 6.9-inch Dynamic AMOLED 2X display, built-in privacy protection, and a 200MP main camera"
    },
    {
        "id": 3,
        "name": "Noise-Cancelling Wireless Headphones",
        "category": "Electronics",
        "price": 3499.00,
        "original_price": 5999.00,
        "quantity": 15,
        "rating": 4.7,
        "rating_count": 890,
        "image": "/static/images/p3.svg",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
        "description": "Active Noise Cancellation, 40-hour battery life, plush memory foam earcups, and crystal-clear hands-free calling."
    },
    {
        "id": 4,
        "name": "Smart Fitness Watch with SpO2",
        "category": "Electronics",
        "price": 2199.00,
        "original_price": 3999.00,
        "quantity": 22,
        "rating": 4.3,
        "rating_count": 340,
        "image": "/static/images/p4.svg",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80",
        "description": "1.78-inch HD curved display, 24/7 heart rate and blood oxygen monitoring, 100+ sports modes, and 7-day battery."
    },

    # Grocery
    {
        "id": 5,
        "name": "Organic Arabica Coffee Beans (500g)",
        "category": "Grocery",
        "price": 499.00,
        "original_price": 650.00,
        "quantity": 30,
        "rating": 4.8,
        "rating_count": 215,
        "image": "/static/images/p5.svg",
        "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80",
        "description": "100% single-origin roasted Arabica beans sourced from high-altitude estates with notes of dark chocolate and hazelnut."
    },
    {
        "id": 6,
        "name": "Cold-Pressed Extra Virgin Olive Oil (1L)",
        "category": "Grocery",
        "price": 950.00,
        "original_price": 1200.00,
        "quantity": 18,
        "rating": 4.6,
        "rating_count": 180,
        "image": "/static/images/p6.svg",
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
        "description": "Pure Mediterranean first cold-pressed olive oil, naturally rich in antioxidants and healthy monounsaturated fats."
    },
    {
        "id": 7,
        "name": "Premium California Raw Almonds (500g)",
        "category": "Grocery",
        "price": 420.00,
        "original_price": 550.00,
        "quantity": 25,
        "rating": 4.7,
        "rating_count": 320,
        "image": "/static/images/p7.svg",
        "image_url": "https://storage.googleapis.com/shy-pub/303196/ChatGPTImageMay14202604_04_08PM-1783947728828.png",
        "description": "Crisp, unpasteurized natural almonds vacuum-packed to preserve crunch and rich vitamin E content."
    },

    # Fashion
    {
        "id": 8,
        "name": "Men's Classic Slim-Fit Oxford Shirt",
        "category": "Fashion",
        "price": 1299.00,
        "original_price": 1999.00,
        "quantity": 14,
        "rating": 4.4,
        "rating_count": 156,
        "image": "/static/images/p8.svg",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80",
        "description": "100% breathable combed cotton with button-down collar, tailored cuffs, and subtle texture ideal for work or casual wear."
    },
    {
        "id": 9,
        "name": "Women's Canvas Everyday Tote Bag",
        "category": "Fashion",
        "price": 899.00,
        "original_price": 1499.00,
        "quantity": 20,
        "rating": 4.6,
        "rating_count": 278,
        "image": "/static/images/p9.svg",
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=600&q=80",
        "description": "Heavyweight 16oz eco-friendly canvas tote with reinforced double handles and a zippered internal stash pocket."
    },
    {
        "id": 10,
        "name": "Polarized Aviator Sunglasses",
        "category": "Fashion",
        "price": 799.00,
        "original_price": 1599.00,
        "quantity": 19,
        "rating": 4.5,
        "rating_count": 190,
        "image": "/static/images/p10.svg",
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=600&q=80",
        "description": "UV400 scratch-resistant polarized lenses with a lightweight stainless steel alloy frame and silicone nose pads."
    },

    # Home & Kitchen
    {
        "id": 11,
        "name": "Cast Iron Pre-Seasoned Skillet (10-inch)",
        "category": "Home & Kitchen",
        "price": 1450.00,
        "original_price": 2100.00,
        "quantity": 12,
        "rating": 4.8,
        "rating_count": 520,
        "image": "/static/images/p11.svg",
        "image_url": "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?auto=format&fit=crop&w=600&q=80",
        "description": "Heavy-duty cast iron pan seasoned with 100% natural vegetable oil for superior heat retention and uniform searing."
    },
    {
        "id": 12,
        "name": "Borosilicate Glass Food Storage Set",
        "category": "Home & Kitchen",
        "price": 999.00,
        "original_price": 1699.00,
        "quantity": 16,
        "rating": 4.5,
        "rating_count": 310,
        "image": "/static/images/p12.svg",
        "image_url": "https://image.made-in-china.com/202f0j00ZQNoSRYtYOgu/4-PCS-Set-Lead-Free-Wholesale-High-Borosilicate-Glass-Lunch-Box.webp",
        "description": "Microwave and oven-safe containers with airtight silicone clip-lock lids, 100% leakproof and BPA-free."
    },
    {
        "id": 13,
        "name": "Modern Minimalist Ceramic Desk Lamp",
        "category": "Home & Kitchen",
        "price": 1699.00,
        "original_price": 2499.00,
        "quantity": 8,
        "rating": 4.7,
        "rating_count": 142,
        "image": "/static/images/p13.svg",
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80",
        "description": "Handcrafted matte ceramic base with warm fabric shade, dimmer switch, and energy-efficient warm LED bulb included."
    },

    # Beauty & Personal Care
    {
        "id": 14,
        "name": "Vitamin C + Hyaluronic Acid Glow Serum (30ml)",
        "category": "Beauty & Personal Care",
        "price": 599.00,
        "original_price": 899.00,
        "quantity": 28,
        "rating": 4.6,
        "rating_count": 640,
        "image": "/static/images/p14.svg",
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80",
        "description": "Dermatologist-tested glow formulation with 10% pure ethyl ascorbic acid and moisture-locking hyaluronic acid."
    },
    {
        "id": 15,
        "name": "Natural Tea Tree & Rosemary Hair Care Kit",
        "category": "Beauty & Personal Care",
        "price": 799.00,
        "original_price": 1199.00,
        "quantity": 17,
        "rating": 4.4,
        "rating_count": 210,
        "image": "/static/images/p15.svg",
        "image_url": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=600&q=80",
        "description": "Sulphate-free purifying shampoo and conditioner set formulated to reduce dandruff and strengthen roots."
    },
    {
        "id": 16,
        "name": "Ultrasonic Sonic Electric Toothbrush",
        "category": "Beauty & Personal Care",
        "price": 1499.00,
        "original_price": 2499.00,
        "quantity": 11,
        "rating": 4.7,
        "rating_count": 380,
        "image": "/static/images/p16.svg",
        "image_url": "https://m.media-amazon.com/images/I/71CiwYb8itL.jpg",
        "description": "40,000 vibrations/min with 5 tailored modes, 2-minute smart timer, and 30-day wireless charging battery."
    },

    # Books & Stationery
    {
        "id": 17,
        "name": "Classic Hardcover Dotted Journal (A5)",
        "category": "Books & Stationery",
        "price": 449.00,
        "original_price": 699.00,
        "quantity": 35,
        "rating": 4.8,
        "rating_count": 490,
        "image": "/static/images/p17.svg",
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
        "description": "160 GSM thick bleedproof bamboo paper with faux leather binding, dual ribbon bookmarks, and an expandable back pocket."
    },
    {
        "id": 18,
        "name": "Vintage Brass Fountain Pen with Fine Nib",
        "category": "Books & Stationery",
        "price": 899.00,
        "original_price": 1399.00,
        "quantity": 14,
        "rating": 4.7,
        "rating_count": 135,
        "image": "/static/images/p18.svg",
        "image_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?auto=format&fit=crop&w=600&q=80",
        "description": "Precision weighted solid brass barrel with German iridium-tipped fine nib and piston ink converter included."
    },
    {
        "id": 19,
        "name": "Bestseller Productivity & Mindset Book",
        "category": "Books & Stationery",
        "price": 399.00,
        "original_price": 599.00,
        "quantity": 25,
        "rating": 4.9,
        "rating_count": 880,
        "image": "/static/images/p19.svg",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80",
        "description": "Transformative guide to building sustainable habits, deep focus, and high performance in everyday professional life."
    },

    # Sports & Fitness
    {
        "id": 20,
        "name": "High-Density Non-Slip Yoga Mat (6mm)",
        "category": "Sports & Fitness",
        "price": 799.00,
        "original_price": 1299.00,
        "quantity": 20,
        "rating": 4.6,
        "rating_count": 310,
        "image": "/static/images/p20.svg",
        "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=600&q=80",
        "description": "Eco-friendly TPE dual-layer mat with alignment guidelines, joint cushioning, and complimentary carry strap."
    },
    {
        "id": 21,
        "name": "Adjustable Neoprene Dumbbells Pair (10kg Total)",
        "category": "Sports & Fitness",
        "price": 1899.00,
        "original_price": 2899.00,
        "quantity": 9,
        "rating": 4.5,
        "rating_count": 175,
        "image": "/static/images/p21.svg",
        "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=600&q=80",
        "description": "Hexagonal anti-roll cast iron weights with comfortable non-slip neoprene coating for home strength workouts."
    },
    {
        "id": 22,
        "name": "Insulated Stainless Steel Sports Flask (750ml)",
        "category": "Sports & Fitness",
        "price": 649.00,
        "original_price": 999.00,
        "quantity": 24,
        "rating": 4.7,
        "rating_count": 425,
        "image": "/static/images/p22.svg",
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=600&q=80",
        "description": "Double-wall vacuum insulation keeps drinks chilled for 24 hours or piping hot for 12 hours. Sweat-proof powder finish."
    },

    # Toys & Accessories
    {
        "id": 23,
        "name": "Magnetic STEM Building Tiles Set (64 Pcs)",
        "category": "Toys & Accessories",
        "price": 1299.00,
        "original_price": 1899.00,
        "quantity": 15,
        "rating": 4.8,
        "rating_count": 290,
        "image": "/static/images/p23.svg",
        "image_url": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&w=600&q=80",
        "description": "Vibrant translucent 3D geometric magnetic building tiles fostering creativity, spatial reasoning, and engineering skills."
    },
    {
        "id": 24,
        "name": "Smart RC Stunt Drone with HD Camera",
        "category": "Toys & Accessories",
        "price": 2799.00,
        "original_price": 4499.00,
        "quantity": 7,
        "rating": 4.4,
        "rating_count": 140,
        "image": "/static/images/p24.svg",
        "image_url": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?auto=format&fit=crop&w=600&q=80",
        "description": "Altitude hold, 360-degree flip maneuvers, one-key return, and real-time FPV Wi-Fi camera with smartphone holder."
    },
    {
        "id": 25,
        "name": "Speed Cube 3x3 Smooth Turning Puzzle",
        "category": "Toys & Accessories",
        "price": 349.00,
        "original_price": 549.00,
        "quantity": 30,
        "rating": 4.7,
        "rating_count": 510,
        "image": "/static/images/p25.svg",
        "image_url": "https://images.unsplash.com/photo-1591991731833-b4807cf7ef94?auto=format&fit=crop&w=600&q=80",
        "description": "Stickerless frosted surface with anti-pop mechanism and adjustable tension for lightning-fast competition turns."
    }
]

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Electronics',
            price REAL NOT NULL,
            original_price REAL,
            quantity INTEGER NOT NULL DEFAULT 0,
            rating REAL DEFAULT 4.5,
            rating_count INTEGER DEFAULT 50,
            image TEXT,
            image_url TEXT,
            description TEXT
        )
    ''')

    # Migration: Ensure image_url column exists if table was created previously
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
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
        )
    ''')

    # Order Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')

    conn.commit()

    # Always ensure local SVG paths & direct image_url support are in DB
    for p in SEED_PRODUCTS:
        img_url = p.get('image_url') or p.get('image')
        cursor.execute('''
            INSERT OR REPLACE INTO products (id, name, category, price, original_price, quantity, rating, rating_count, image, image_url, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p['id'], p['name'], p['category'], p['price'], p['original_price'],
            p['quantity'], p['rating'], p['rating_count'], p.get('image', img_url), img_url, p['description']
        ))

    conn.commit()
    sync_json_from_db(conn)
    conn.close()

def sync_json_from_db(conn=None):
    """Keep Backend/products.json synchronized with database."""
    close_after = False
    if conn is None:
        conn = get_db()
        close_after = True
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY id ASC')
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        pass
    if close_after:
        conn.close()

# Initialize DB on start
init_db()

# --- Storefront Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = [
        "Electronics",
        "Grocery",
        "Fashion",
        "Home & Kitchen",
        "Beauty & Personal Care",
        "Books & Stationery",
        "Sports & Fitness",
        "Toys & Accessories"
    ]
    return jsonify(categories)

@app.route('/api/coupons', methods=['GET'])
def get_coupons():
    return jsonify(list(COUPONS.values()))

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        category = request.args.get('category')
        search = request.args.get('search', '').strip().lower()
        sort_by = request.args.get('sort', 'default')
        in_stock_only = request.args.get('in_stock', 'false').lower() == 'true'
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        conn = get_db()
        cursor = conn.cursor()

        query = 'SELECT * FROM products WHERE 1=1'
        params = []

        if category and category.lower() != 'all':
            query += ' AND LOWER(category) = LOWER(?)'
            params.append(category)

        if search:
            query += ' AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])

        if in_stock_only:
            query += ' AND quantity > 0'

        if min_price is not None:
            query += ' AND price >= ?'
            params.append(min_price)

        if max_price is not None:
            query += ' AND price <= ?'
            params.append(max_price)

        if sort_by == 'price_asc':
            query += ' ORDER BY price ASC'
        elif sort_by == 'price_desc':
            query += ' ORDER BY price DESC'
        elif sort_by == 'discount':
            query += ' ORDER BY ((original_price - price) / original_price) DESC'
        elif sort_by == 'rating':
            query += ' ORDER BY rating DESC'
        elif sort_by == 'name':
            query += ' ORDER BY name ASC'
        else:
            query += ' ORDER BY id ASC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        products = [dict(row) for row in rows]
        conn.close()

        return jsonify(products)
    except Exception as e:
        logger.error(f"Error querying products: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve products', 'details': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404

    product = dict(row)

    cursor.execute('''
        SELECT * FROM products
        WHERE category = ? AND id != ?
        LIMIT 4
    ''', (product['category'], product_id))
    related = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({
        'product': product,
        'related': related
    })

# Legacy Inventory Endpoints
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json or {}
    name = data.get('name', '').strip()
    category = data.get('category', 'Electronics')
    quantity = int(data.get('quantity', 0))
    price = float(data.get('price', 0.0))
    original_price = float(data.get('original_price', price * 1.25))
    image_url = data.get('image_url') or data.get('image', '/static/images/p1.svg')
    image = data.get('image', image_url)
    description = data.get('description', 'Authentic product with standard brand warranty.')

    if not name or price < 0 or quantity < 0:
        return jsonify({'error': 'Invalid product parameters'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, category, price, original_price, quantity, rating, rating_count, image, image_url, description)
        VALUES (?, ?, ?, ?, ?, 4.5, 1, ?, ?, ?)
    ''', (name, category, price, original_price, quantity, image, image_url, description))
    new_id = cursor.lastrowid
    conn.commit()

    cursor.execute('SELECT * FROM products WHERE id = ?', (new_id,))
    new_product = dict(cursor.fetchone())
    sync_json_from_db(conn)
    conn.close()

    return jsonify(new_product), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json or {}
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404

    name = data.get('name', existing['name'])
    category = data.get('category', existing['category'])
    quantity = int(data.get('quantity', existing['quantity']))
    price = float(data.get('price', existing['price']))
    original_price = float(data.get('original_price', existing['original_price']))
    description = data.get('description', existing['description'])
    image_url = data.get('image_url', existing['image_url'] if 'image_url' in existing.keys() else existing['image'])
    image = data.get('image', image_url)

    cursor.execute('''
        UPDATE products
        SET name = ?, category = ?, quantity = ?, price = ?, original_price = ?, description = ?, image = ?, image_url = ?
        WHERE id = ?
    ''', (name, category, quantity, price, original_price, description, image, image_url, product_id))
    conn.commit()

    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    updated = dict(cursor.fetchone())
    sync_json_from_db(conn)
    conn.close()

    return jsonify(updated)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    sync_json_from_db(conn)
    conn.close()
    return jsonify({'success': True})

# --- Cart Calculation & Coupons ---

def calculate_cart_totals(cart_items, coupon_code=None):
    conn = get_db()
    cursor = conn.cursor()

    verified_items = []
    subtotal = 0.0
    stock_errors = []

    for item in cart_items:
        pid = item.get('id')
        req_qty = int(item.get('quantity', 1))
        if req_qty <= 0:
            continue

        cursor.execute('SELECT * FROM products WHERE id = ?', (pid,))
        prod = cursor.fetchone()
        if not prod:
            stock_errors.append(f"Product ID {pid} is no longer available.")
            continue

        p_dict = dict(prod)
        if p_dict['quantity'] < req_qty:
            stock_errors.append(f"Only {p_dict['quantity']} unit(s) left for '{p_dict['name']}'.")

        item_total = round(p_dict['price'] * req_qty, 2)
        subtotal += item_total

        verified_items.append({
            'id': p_dict['id'],
            'name': p_dict['name'],
            'category': p_dict['category'],
            'price': p_dict['price'],
            'original_price': p_dict['original_price'],
            'image': p_dict.get('image'),
            'image_url': p_dict.get('image_url') or p_dict.get('image'),
            'quantity': req_qty,
            'max_stock': p_dict['quantity'],
            'total': item_total
        })

    conn.close()
    subtotal = round(subtotal, 2)

    discount_amount = 0.0
    applied_coupon = None
    coupon_message = None

    if coupon_code:
        code_upper = coupon_code.strip().upper()
        if code_upper in COUPONS:
            rule = COUPONS[code_upper]
            if subtotal < rule['min_order']:
                coupon_message = f"Coupon '{code_upper}' requires a minimum cart value of ₹{rule['min_order']}."
            else:
                if rule['type'] == 'percentage':
                    calc_discount = (subtotal * rule['value']) / 100.0
                    discount_amount = min(calc_discount, rule['max_discount'])
                elif rule['type'] == 'flat':
                    discount_amount = min(rule['value'], subtotal)
                elif rule['type'] == 'free_shipping':
                    discount_amount = 0.0

                discount_amount = round(discount_amount, 2)
                applied_coupon = {
                    'code': code_upper,
                    'discount': discount_amount,
                    'type': rule['type'],
                    'description': rule['description']
                }
                coupon_message = f"Coupon '{code_upper}' applied successfully!"
        else:
            coupon_message = f"Invalid coupon code '{coupon_code}'."

    delivery_fee = DELIVERY_FEE if subtotal > 0 else 0.0
    if subtotal >= FREE_DELIVERY_THRESHOLD or (applied_coupon and applied_coupon['type'] == 'free_shipping'):
        delivery_fee = 0.0

    final_total = max(0.0, round(subtotal - discount_amount + delivery_fee, 2))

    return {
        'items': verified_items,
        'subtotal': subtotal,
        'discount': discount_amount,
        'delivery_fee': delivery_fee,
        'total': final_total,
        'free_delivery_threshold': FREE_DELIVERY_THRESHOLD,
        'applied_coupon': applied_coupon,
        'coupon_message': coupon_message,
        'stock_errors': stock_errors
    }

@app.route('/api/cart/calculate', methods=['POST'])
def api_calculate_cart():
    data = request.json or {}
    items = data.get('items', [])
    coupon_code = data.get('coupon_code')
    calculation = calculate_cart_totals(items, coupon_code)
    return jsonify(calculation)

# --- Checkout ---

@app.route('/api/cart/checkout', methods=['POST'])
def api_checkout():
    data = request.json or {}
    cart_items = data.get('items', [])
    coupon_code = data.get('coupon_code')
    delivery_info = data.get('delivery', {})
    payment_method = data.get('payment_method', 'Cash on Delivery (Demo)')

    if not cart_items:
        return jsonify({'error': 'Your cart is empty'}), 400

    required_fields = ['name', 'email', 'phone', 'address', 'city', 'state', 'postal_code']
    for field in required_fields:
        if not delivery_info.get(field, '').strip():
            return jsonify({'error': f"Please enter your {field.replace('_', ' ').capitalize()}."}), 400

    conn = get_db()
    cursor = conn.cursor()

    for item in cart_items:
        pid = item.get('id')
        req_qty = int(item.get('quantity', 1))
        cursor.execute('SELECT quantity, name FROM products WHERE id = ?', (pid,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': f"Product ID {pid} is no longer available"}), 404
        if row['quantity'] < req_qty:
            conn.close()
            return jsonify({
                'error': f"Insufficient stock for '{row['name']}'. Only {row['quantity']} available."
            }), 400

    calc = calculate_cart_totals(cart_items, coupon_code)
    if calc['stock_errors']:
        conn.close()
        return jsonify({'error': calc['stock_errors'][0]}), 400

    order_id = f"EC-{random.randint(100000, 999999)}"
    user_id = session.get('user_id')

    cursor.execute('''
        INSERT INTO orders (
            id, user_id, customer_name, customer_email, customer_phone,
            address, city, state, postal_code, subtotal, discount,
            delivery_fee, total, coupon_code, payment_method, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')
    ''', (
        order_id, user_id,
        delivery_info['name'].strip(),
        delivery_info['email'].strip(),
        delivery_info['phone'].strip(),
        delivery_info['address'].strip(),
        delivery_info['city'].strip(),
        delivery_info['state'].strip(),
        delivery_info['postal_code'].strip(),
        calc['subtotal'],
        calc['discount'],
        calc['delivery_fee'],
        calc['total'],
        calc['applied_coupon']['code'] if calc['applied_coupon'] else None,
        payment_method
    ))

    for item in calc['items']:
        cursor.execute('''
            INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            order_id, item['id'], item['name'], item['price'], item['quantity'], item['total']
        ))

        cursor.execute('''
            UPDATE products
            SET quantity = quantity - ?
            WHERE id = ?
        ''', (item['quantity'], item['id']))

    conn.commit()
    sync_json_from_db(conn)
    conn.close()

    return jsonify({
        'success': True,
        'order_id': order_id,
        'message': 'Order placed successfully! Thank you for shopping with EasyCart.',
        'order_details': {
            'order_id': order_id,
            'customer': delivery_info,
            'items': calc['items'],
            'subtotal': calc['subtotal'],
            'discount': calc['discount'],
            'delivery_fee': calc['delivery_fee'],
            'total': calc['total'],
            'payment_method': payment_method,
            'status': 'Confirmed'
        }
    })

# --- Proper User Authentication (Allows any email to log in seamlessly) ---

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Allows instant login with ANY email address; creates account on the fly if needed."""
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email:
        return jsonify({'error': 'Please enter your email address.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if not user:
        # Generate friendly display name from email (e.g. shraddha.singh@gmail.com -> Shraddha Singh)
        raw_name = email.split('@')[0]
        clean_name = ' '.join(part.capitalize() for part in raw_name.replace('.', ' ').replace('_', ' ').split())
        if not clean_name:
            clean_name = "Shraddha Singh"
        pw_hash = generate_password_hash(password or 'easycart123')
        cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (clean_name, email, pw_hash))
        user_id = cursor.lastrowid
        conn.commit()
        user = {'id': user_id, 'name': clean_name, 'email': email}
    else:
        user = dict(user)

    conn.close()

    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']

    return jsonify({
        'success': True,
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email']},
        'message': f"Signed in as {user['name']}"
    })

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    if not name:
        raw_name = email.split('@')[0]
        name = ' '.join(part.capitalize() for part in raw_name.replace('.', ' ').replace('_', ' ').split())
        if not name:
            name = "Shraddha Singh"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    existing = cursor.fetchone()

    if existing:
        user_id = existing['id']
    else:
        pw_hash = generate_password_hash(password or 'easycart123')
        cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, pw_hash))
        user_id = cursor.lastrowid
        conn.commit()

    conn.close()

    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email

    return jsonify({
        'success': True,
        'user': {'id': user_id, 'name': name, 'email': email}
    })

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        session.clear()
        return jsonify({'authenticated': False})

    return jsonify({
        'authenticated': True,
        'user': dict(user)
    })

@app.route('/api/auth/orders', methods=['GET'])
def api_user_orders():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    orders = [dict(r) for r in cursor.fetchall()]

    for order in orders:
        cursor.execute('''
            SELECT * FROM order_items
            WHERE order_id = ?
        ''', (order['id'],))
        order['items'] = [dict(i) for i in cursor.fetchall()]

    conn.close()
    return jsonify(orders)

if __name__ == '__main__':
    app.run(debug=True)
