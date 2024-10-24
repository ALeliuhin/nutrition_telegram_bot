import db_manager
import os
password = os.getenv("ADMIN_PWD")

class AdminInterface():

        @staticmethod
        def check_database_for_suggestion():
                connection = db_manager.connect_to_db()
                cursor = connection.cursor()
                data = cursor.execute("""
                        SELECT * FROM list_suggestions;
                """).fetchall()
                connection.commit()
                connection.close()
                return data
        
        @staticmethod
        def inspect_login_data():
                connection = db_manager.connect_to_db()
                cursor = connection.cursor()
                users = cursor.execute("""
                        SELECT DISTINCT tg_username, privilege 
                        FROM login_data
                        ORDER BY privilege;
                """).fetchall()
                connection.commit()
                connection.close()
                return users

        
        @staticmethod
        def check_admins():
                connection = db_manager.connect_to_db()
                cursor = connection.cursor()
                admins_list = [admin[0] for admin in cursor.execute("""
                        SELECT tg_username FROM login_data
                        WHERE privilege = 'admin';
                """).fetchall()]
                connection.commit()
                connection.close()
                return admins_list
        
        @staticmethod
        def grant_privileges(usernames):
                connection = db_manager.connect_to_db()
                cursor = connection.cursor()
                
                success = True
                for username in usernames:
                        try:
                                cursor.execute("""
                                        UPDATE login_data
                                        SET privilege = 'admin'
                                        WHERE tg_username = ?;
                                """, (username,))
                        except Exception as e:
                                success = False
                                print(f"Error updating privileges for {username}: {e}")

                connection.commit()
                connection.close()
                return success

        @staticmethod
        def add_selected_suggestions(selected_ids):
                connection = db_manager.connect_to_db()
                cursor = connection.cursor()

                for suggestion_id in selected_ids:
                        try:
                                current_suggestion = cursor.execute("""
                                        SELECT * FROM list_suggestions
                                        WHERE suggestion_id = ?;
                                """, (suggestion_id,)).fetchone()

                                if current_suggestion is None:
                                        continue

                                product_type_name = current_suggestion[2]
                                product_name = current_suggestion[3]
                                product_supplier_name = current_suggestion[4]
                                product_calories = current_suggestion[5]
                                product_proteins = current_suggestion[6]
                                product_carbs = current_suggestion[7]
                                product_sugars = current_suggestion[8]
                                product_fats = current_suggestion[9]
                                product_fiber = current_suggestion[10]


                                product_type_id = cursor.execute("""
                                        SELECT type_id FROM product_types WHERE type_name = ?;
                                """, (product_type_name,)).fetchone()[0]

                                cursor.execute("""
                                        INSERT OR IGNORE INTO suppliers (supplier_name)
                                        VALUES (?);
                                """, (product_supplier_name,))

                                product_supplier_id = cursor.execute("""
                                        SELECT supplier_id FROM suppliers WHERE supplier_name = ?;
                                """, (product_supplier_name,)).fetchone()[0]

                                cursor.execute("""
                                        INSERT INTO products (product_name, product_type, product_supplier, calories)
                                        VALUES (?, ?, ?, ?);
                                """, (product_name, product_type_id, product_supplier_id, product_calories))

                                product_id = cursor.lastrowid

                                cursor.execute("""
                                        INSERT INTO nutrition_info (product_id, proteins, carbos, sugars, fats, fiber)
                                        VALUES (?, ?, ?, ?, ?, ?);
                                """, (product_id, product_proteins, product_carbs, product_sugars, product_fats, product_fiber))

                                cursor.execute("""
                                        DELETE FROM list_suggestions;
                                """)

                                connection.commit()
                                return True

                        except Exception as e:
                                connection.rollback() 
                                return False

                connection.close()

        @staticmethod
        def delete_product_from_db(product_name, supplier_name):
                connection = db_manager.connect_to_db()
                cursor = connection.cursor()

                try:
                        supplier_id = cursor.execute("""
                        SELECT supplier_id FROM suppliers
                        WHERE supplier_name = ?;
                        """, (supplier_name,)).fetchone()

                        if not supplier_id:
                                raise Exception("Supplier not found.")
                        
                        supplier_id = supplier_id[0]

                        product_id = cursor.execute("""
                        SELECT product_id FROM products
                        WHERE product_name = ? AND product_supplier = ?;
                        """, (product_name, supplier_id)).fetchone()

                        if not product_id:
                                raise Exception("Product not found.")
                        
                        product_id = product_id[0] 

                        cursor.execute("""
                        DELETE FROM products
                        WHERE product_name = ? AND product_supplier = ?;
                        """, (product_name, supplier_id))

                        cursor.execute("""
                        DELETE FROM nutrition_info
                        WHERE product_id = ?;
                        """, (product_id,))

                        remaining_products = cursor.execute("""
                        SELECT product_id FROM products
                        WHERE product_supplier = ?;
                        """, (supplier_id,)).fetchall()

                        if not remaining_products:
                                cursor.execute("""
                                        DELETE FROM suppliers
                                        WHERE supplier_id = ?;
                                """, (supplier_id,))

                        connection.commit()
                        return True

                except Exception as e:
                        connection.rollback()
                        print(f"Error: {e}")
                        return False

                finally:
                        connection.close()
