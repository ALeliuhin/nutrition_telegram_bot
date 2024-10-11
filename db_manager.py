import sqlite3

connection = sqlite3.connect('nutrition.db')
cursor = connection.cursor()

create_table_query = """

    CREATE TABLE IF NOT EXISTS product_types (
        type_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        type_name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_type INTEGER,
        calories INTEGER,
        FOREIGN KEY (product_type) REFERENCES product_types(type_id)
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

"""

cursor.executescript(create_table_query)

def is_table_empty(table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    result = cursor.fetchone()
    return result[0] == 0

product_types = [
        "Meat", "Dairy", "Grains", "Vegetables", "Fruits", "Beans",
        "Nuts and Seeds", "Beverages", "Bakery", "Snacks","Canned Goods", 
        "Condiments", "Spices and Herbs", "Oils and Fats", "Sweets",
]

if(is_table_empty('product_types')):
    for product_type in product_types:
        cursor.execute("INSERT INTO product_types (type_name) VALUES (?)", (product_type,))

connection.commit()
connection.close()
