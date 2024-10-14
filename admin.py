import db_manager
password = "freakycomplexpwd"

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

