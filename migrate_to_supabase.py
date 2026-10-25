"""
One-click data migration utility from local SQLite (easycart.db) to Supabase PostgreSQL.
Run this script with your DATABASE_URL set:
    $env:DATABASE_URL = "postgresql://postgres:[PASSWORD]@db.qsykasqjojcikdfvouml.supabase.co:5432/postgres"
    python migrate_to_supabase.py
"""
import os
import sys
import sqlite3
import psycopg
from psycopg.rows import dict_row

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Backend')
DB_FILE = os.path.join(BACKEND_DIR, 'easycart.db')
DATABASE_URL = os.environ.get('DATABASE_URL')

def migrate():
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable is not set.")
        print("Please set your Supabase PostgreSQL connection string, e.g.:")
        print('  $env:DATABASE_URL = "postgresql://postgres:PASSWORD@db.qsykasqjojcikdfvouml.supabase.co:5432/postgres"')
        sys.exit(1)

    if not os.path.exists(DB_FILE):
        print(f"ERROR: SQLite database file not found at {DB_FILE}")
        sys.exit(1)

    print(f"Connecting to SQLite: {DB_FILE}")
    sqlite_conn = sqlite3.connect(DB_FILE)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    db_url = DATABASE_URL
    if 'sslmode' not in db_url:
        separator = '&' if '?' in db_url else '?'
        db_url += f'{separator}sslmode=require'

    print("Connecting to Supabase PostgreSQL...")
    pg_conn = psycopg.connect(db_url, row_factory=dict_row)
    pg_cur = pg_conn.cursor()

    # 1. Migrate Products
    sqlite_cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = sqlite_cur.fetchall()
    print(f"\nMigrating {len(products)} products...")
    for p in products:
        p_dict = dict(p)
        pg_cur.execute("""
            INSERT INTO products (id, name, category, price, original_price, quantity, rating, rating_count, image, image_url, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                price = EXCLUDED.price,
                original_price = EXCLUDED.original_price,
                quantity = EXCLUDED.quantity,
                rating = EXCLUDED.rating,
                rating_count = EXCLUDED.rating_count,
                image = EXCLUDED.image,
                image_url = EXCLUDED.image_url,
                description = EXCLUDED.description
        """, (
            p_dict['id'], p_dict['name'], p_dict['category'], p_dict['price'], p_dict.get('original_price'),
            p_dict['quantity'], p_dict.get('rating', 4.5), p_dict.get('rating_count', 50),
            p_dict.get('image'), p_dict.get('image_url') or p_dict.get('image'), p_dict.get('description')
        ))
    pg_cur.execute("SELECT setval(pg_get_serial_sequence('products', 'id'), GREATEST((SELECT MAX(id) FROM products), 1))")
    print(f"  ✓ {len(products)} products migrated successfully.")

    # 2. Migrate Users
    sqlite_cur.execute("SELECT * FROM users ORDER BY id ASC")
    users = sqlite_cur.fetchall()
    print(f"\nMigrating {len(users)} users...")
    for u in users:
        u_dict = dict(u)
        pg_cur.execute("""
            INSERT INTO users (id, name, email, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                password_hash = EXCLUDED.password_hash
        """, (
            u_dict['id'], u_dict['name'], u_dict['email'],
            u_dict['password_hash'], u_dict.get('created_at')
        ))
    pg_cur.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), GREATEST((SELECT MAX(id) FROM users), 1))")
    print(f"  ✓ {len(users)} users migrated successfully.")

    # 3. Migrate Orders
    sqlite_cur.execute("SELECT * FROM orders ORDER BY created_at ASC")
    orders = sqlite_cur.fetchall()
    print(f"\nMigrating {len(orders)} orders...")
    for o in orders:
        o_dict = dict(o)
        pg_cur.execute("""
            INSERT INTO orders (
                id, user_id, customer_name, customer_email, customer_phone,
                address, city, state, postal_code, subtotal, discount,
                delivery_fee, total, coupon_code, payment_method, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            o_dict['id'], o_dict.get('user_id'), o_dict['customer_name'], o_dict['customer_email'],
            o_dict.get('customer_phone'), o_dict['address'], o_dict['city'], o_dict['state'],
            o_dict['postal_code'], o_dict['subtotal'], o_dict['discount'], o_dict['delivery_fee'],
            o_dict['total'], o_dict.get('coupon_code'), o_dict['payment_method'],
            o_dict.get('status', 'Confirmed'), o_dict.get('created_at')
        ))
    print(f"  ✓ {len(orders)} orders migrated successfully.")

    # 4. Migrate Order Items
    sqlite_cur.execute("SELECT * FROM order_items ORDER BY id ASC")
    order_items = sqlite_cur.fetchall()
    print(f"\nMigrating {len(order_items)} order items...")
    for oi in order_items:
        oi_dict = dict(oi)
        pg_cur.execute("""
            INSERT INTO order_items (id, order_id, product_id, product_name, unit_price, quantity, total_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            oi_dict['id'], oi_dict['order_id'], oi_dict['product_id'],
            oi_dict['product_name'], oi_dict['unit_price'], oi_dict['quantity'], oi_dict['total_price']
        ))
    pg_cur.execute("SELECT setval(pg_get_serial_sequence('order_items', 'id'), GREATEST((SELECT MAX(id) FROM order_items), 1))")
    print(f"  ✓ {len(order_items)} order items migrated successfully.")

    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print("\n🎉 Full migration from SQLite to Supabase PostgreSQL completed successfully!")

if __name__ == '__main__':
    migrate()

