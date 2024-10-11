import sqlite3

def connect_to_db():
    return sqlite3.connect('nutrition.db')


product_types = [
    "Meat", "Dairy", "Grains", "Vegetables", "Fruits", "Beans",
    "Nuts and Seeds", "Beverages", "Bakery", "Snacks", "Canned Goods",
    "Condiments", "Spices and Herbs", "Oils and Fats", "Sweets",
]

create_table_query = """

    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS product_types (
        type_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        type_name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_type INTEGER NOT NULL,
        product_supplier INTEGER,
        calories INTEGER,
        FOREIGN KEY (product_type) REFERENCES product_types(type_id),
        FOREIGN KEY (product_supplier) REFERENCES suppliers (supplier_id)
    );

    CREATE TABLE IF NOT EXISTS nutrition_info (
        nutrition_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        proteins REAL,
        carbos REAL,
        sugars REAL,
        fats REAL,
        fiber REAL,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );

    CREATE TABLE IF NOT EXISTS login_data (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_username TEXT NOT NULL,
        user_name TEXT,
        login_time DATETIME NOT NULL 
    );
"""


def is_table_empty(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    result = cursor.fetchone()
    return result[0] == 0



def add_user_to_db(cursor, tg_username, user_name, login_time):
    cursor.execute("INSERT INTO login_data (tg_username, user_name, login_time) VALUES (?, ?, ?)", (tg_username, user_name, login_time))

def create_tables_db(cursor):
    cursor.executescript(create_table_query)
    if is_table_empty(cursor, 'product_types'):
        for product_type in product_types:
            cursor.execute("INSERT INTO product_types (type_name) VALUES (?)", (product_type,))


