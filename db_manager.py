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
        supplier_name TEXT NOT NULL UNIQUE
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
        privilege TEXT NOT NULL,
        login_time DATETIME DEFAULT CURRENT_TIMESTAMP 
    );

    CREATE TABLE IF NOT EXISTS list_suggestions (
        suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_username TEXT NOT NULL,
        product_type TEXT,
        product_name TEXT,
        product_supplier TEXT,
        product_calories INTEGER,
        product_proteins REAL,
        product_carbs REAL,
        product_sugars REAL,
        product_fats REAL,
        product_fiber REAL
    );
"""


def is_table_empty(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    result = cursor.fetchone()
    return result[0] == 0

def add_user_to_db(cursor, tg_username, user_name, privilege, login_time):
    cursor.execute("INSERT INTO login_data (tg_username, user_name, privilege, login_time) VALUES (?, ?, ?, ?)", (tg_username, user_name, privilege, login_time))

def create_tables_db(cursor):
    cursor.executescript(create_table_query)
    if is_table_empty(cursor, 'product_types'):
        for product_type in product_types:
            cursor.execute("INSERT INTO product_types (type_name) VALUES (?)", (product_type,))

def suggest_adding_product(cursor, tuple_to_write):
    cursor.execute("""
                   INSERT INTO list_suggestions (tg_username, product_type, product_name, 
                   product_supplier, product_calories, product_proteins,
                   product_carbs, product_sugars, product_fats, product_fiber)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple_to_write)

def inspect_suppliers():
    connection = connect_to_db()
    cursor = connection.cursor()

    suppliers = cursor.execute("""
        SELECT DISTINCT (supplier_name) FROM suppliers
        ORDER BY supplier_name;
    """).fetchall()

    connection.commit()
    connection.close()

    return suppliers


def inspect_by_type(product_type_name):
    connection = connect_to_db()
    cursor = connection.cursor()

    type_id = cursor.execute("""
        SELECT type_id FROM product_types
        WHERE type_name = ?;
    """, (product_type_name,)).fetchone()

    if type_id is None:
        return None  

    products_by_type = cursor.execute("""
        SELECT p.product_id, p.product_name, pt.type_name, s.supplier_name, p.calories,
               n.proteins, n.carbos, n.sugars, n.fats, n.fiber
        FROM products p
        JOIN product_types pt ON p.product_type = pt.type_id
        JOIN suppliers s ON p.product_supplier = s.supplier_id
        LEFT JOIN nutrition_info n ON p.product_id = n.product_id
        WHERE p.product_type = ?
        ORDER BY p.product_name;
    """, (type_id[0],)).fetchall()

    if len(products_by_type) == 0:
        return None
    
    list_of_products = [
        (
            (product[0], product[1], product[2], product[3], product[4]), 
            (product[5], product[6], product[7], product[8], product[9]) 
        )
        for product in products_by_type
    ]

    connection.commit()
    connection.close()

    return list_of_products


def inspect_by_supplier(product_supplier_name):
    connection = connect_to_db()
    cursor = connection.cursor()

    supplier_id = cursor.execute("""
        SELECT supplier_id FROM suppliers
        WHERE supplier_name = ?;
    """, (product_supplier_name,)).fetchone()

    products_by_supplier = cursor.execute("""
        SELECT p.product_id, p.product_name, pt.type_name, s.supplier_name, p.calories,
            n.proteins, n.carbos, n.sugars, n.fats, n.fiber
        FROM products p
        JOIN product_types pt ON p.product_type = pt.type_id
        JOIN suppliers s ON p.product_supplier = s.supplier_id
        LEFT JOIN nutrition_info n ON p.product_id = n.product_id
        WHERE p.product_supplier = ?
        ORDER BY p.product_name;
    """, (supplier_id[0],)).fetchall()
    
    if len(products_by_supplier) == 0:
        return None
    
    list_of_products = [
        (
            (product[0], product[1], product[2], product[3], product[4]), 
            (product[5], product[6], product[7], product[8], product[9]) 
        )
        for product in products_by_supplier
    ]

    connection.commit()
    connection.close()

    return list_of_products

def inspect_by_name(name):
    connection = connect_to_db()
    cursor = connection.cursor()

    products_by_name = cursor.execute("""
        SELECT p.product_id, p.product_name, pt.type_name, s.supplier_name, p.calories,
            n.proteins, n.carbos, n.sugars, n.fats, n.fiber
        FROM products p 
        JOIN product_types pt ON p.product_type = pt.type_id
        JOIN suppliers s ON p.product_supplier = s.supplier_id
        LEFT JOIN nutrition_info n ON p.product_id = n.product_id
        WHERE product_name = ? OR product_name LIKE ?
        ORDER BY p.product_name;
    """, (name, name[0:2] + '%')).fetchall()

    if len(products_by_name) == 0:
        return None
    
    list_of_products = [
        (
            (product[0], product[1], product[2], product[3], product[4]), 
            (product[5], product[6], product[7], product[8], product[9]) 
        )
        for product in products_by_name
    ]

    connection.commit()
    connection.close()

    return list_of_products