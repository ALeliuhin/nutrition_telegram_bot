import telebot
from telebot import types
import openai
import db_manager, admin
from datetime import datetime

BOT_TOKEN = admin.os.getenv("BOT_TOKEN")
OPENAI_API_KEY = admin.os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)


if __name__ == '__main__' :

    suggest_product_list = {}
    selected_products = []


    @bot.message_handler(commands=['start'])
    def start_command(message):
        markup_remove = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f'Welcome, {message.from_user.username}! Use the /menu button below to access the menu:', reply_markup=markup_remove)
        connection = db_manager.connect_to_db()
        cursor = connection.cursor()
        if message.from_user.username == "olegovich_la":
            db_manager.create_tables_db(cursor)
        db_manager.add_user_to_db(cursor, f'@{message.from_user.username}', message.from_user.first_name, 
                            "admin" if message.from_user.username == "olegovich_la" else "user", 
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        connection.commit()
        connection.close()
        
    @bot.message_handler(content_types=['photo', 'document'])
    def handle_audio_doc(message):
        if message.photo:
            bot.reply_to(message, "This is an image!")
        elif message.document:
            bot.reply_to(message, "This is a document!")

    @bot.message_handler(commands=['info'])
    def inspect_info_bot(message):
        bot.send_message(message.chat.id,
                'This is a Nutrition Manager Bot that allows you to search for a specific product, '
                'inspect its nutrients data, pick products from the list and compose a meal. '
                'You will be able to look at a number of calories of a product per 100g, '
                'as well as the amount of proteins or fats in this product. '
                'Use the command "/menu" to see the options.'
        )       

    ### Main Menu

    @bot.message_handler(commands=['menu'])
    def main_menu_interface(message):
        markup = types.InlineKeyboardMarkup(row_width=2)

        search = types.InlineKeyboardButton('Search for a product', callback_data='choice_search')
        select_meal = types.InlineKeyboardButton('Select food', callback_data='choice_select')
        suggest = types.InlineKeyboardButton('Suggest food to add', callback_data='choice_suggest')
        admin_change = types.InlineKeyboardButton('Modify data (admin)', callback_data='choice_modify')
        generate_recipe_ai = types.InlineKeyboardButton('Generate recipe AI', callback_data='choice_generate')

        markup.add(search, select_meal, suggest, admin_change, generate_recipe_ai)

        bot.send_message(message.chat.id, '<b>Welcome to the Main Menu</b>', parse_mode= "HTML", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("choice_"))
    def answer_main_menu(callback):
        if callback.message:
            if callback.data == 'choice_suggest':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                for type in db_manager.product_types:
                    markup.add(type)
                bot.send_message(callback.message.chat.id, "Please choose the product's type:", reply_markup=markup)
                bot.register_next_step_handler(callback.message, input_name)
            elif callback.data == 'choice_modify':
                bot.send_message(callback.message.chat.id, "Enter admin password:")
                bot.register_next_step_handler(callback.message, check_admin_password)
            elif callback.data == 'choice_search':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add("Search by name", "Search by type", "Search by supplier")
                bot.send_message(callback.message.chat.id, "<b>Choose one of the options:</b>", parse_mode="HTML", reply_markup=markup)
                bot.register_next_step_handler(callback.message, search_product_menu)
            elif callback.data == 'choice_select':
                markup = types.InlineKeyboardMarkup(row_width=2)

                add_products_to_cart = types.InlineKeyboardButton('Add products to cart', callback_data='add_products_to_cart')
                markup.add(add_products_to_cart)
                if len(selected_products) > 0:
                    cancel_button = types.InlineKeyboardButton('Cancel', callback_data='cancel_add_product')
                    markup.add(cancel_button)

                    total_calories = 0
                    total_proteins = 0
                    total_carbs = 0
                    total_sugars = 0
                    total_fats = 0
                    total_fibers = 0

                    response = f"<b>Products in cart: (per 100g)</b>\n"
                    
                    for product in selected_products:
                        product_name = product[0][1]
                        product_supplier = product[0][3]
                        product_type = product[0][2]
                        product_calories = product[0][4]
                        product_proteins = product[0][5]
                        product_carbs = product[0][6]
                        product_sugars = product[0][7]
                        product_fats = product[0][8]
                        product_fibers = product[0][9]

                        total_calories += product_calories * (product[1]/100)
                        total_proteins += product_proteins * (product[1]/100)
                        total_carbs += product_carbs * (product[1]/100)
                        total_sugars += product_sugars * (product[1]/100)
                        total_fats += product_fats * (product[1]/100)
                        total_fibers += product_fibers * (product[1]/100)

                        response += f"""
                        <b>Name:</b> {product_name}
                        <b>Supplier:</b> {product_supplier}
                        <b>Type:</b> {product_type}
                        <b>Calories:</b> {product_calories}
                        <b>Proteins:</b> {product_proteins}
                        <b>Carbs:</b> {product_carbs}
                        \tfrom which <b>sugars:</b> {product_sugars}
                        <b>Fats:</b> {product_fats}
                        <b>Fibers:</b> {product_fibers}
                        <b>Mass: </b> {product[1]}g\n
                        """
                    
                    response += f"""\n<b>Total calories:</b> {round(total_calories, 2)}
                    <b>Total proteins:</b> {round(total_proteins, 2)}
                    <b>Total carbs:</b> {round(total_carbs, 2)}
                    <b>Total sugars:</b> {round(total_sugars, 2)}
                    <b>Total fats:</b> {round(total_fats, 2)}
                    <b>Total fibers:</b> {round(total_fibers, 2)}
                    """
                    bot.send_message(callback.message.chat.id, response, parse_mode="HTML", reply_markup=markup)
                else:
                    bot.send_message(callback.message.chat.id, '<b>The cart is currently empty</b>', parse_mode="HTML", reply_markup=markup)                
            elif callback.data == 'choice_generate':
                try:
                    completion = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a good cook, suggesting a nice meal recipe in a short message"},
                            {"role": "user", "content": "Generate a tasty recipe"}
                        ],
                    )
                    recipe = completion.choices[0].message.content
                    bot.send_message(callback.message.chat.id, recipe)
                except Exception as e:
                    bot.send_message(callback.message.chat.id, f"An error occurred: {str(e)}")

    ## Add product to cart

    @bot.callback_query_handler(func=lambda call: call.data in ['add_products_to_cart'])
    def add_product_to_cart(callback):
        if(len(selected_products) > 10):
            bot.send_message(callback.message.chat.id, "The cart is full. You cannot add more products")
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Select by name", "Select by type", "Select by supplier")
        bot.send_message(callback.message.chat.id, "<b>Choose one of the options:</b>", parse_mode="HTML", reply_markup=markup)
        bot.register_next_step_handler(callback.message, search_product_menu)

    @bot.callback_query_handler(func=lambda call: call.data in ['cancel_add_product'])
    def cancel_add_product(callback):
        if callback.message:
            selected_products.clear()
            bot.send_message(callback.message.chat.id, "<b>The cart is now empty!</b>", parse_mode="HTML")


    ## Suggest a product

    def input_name(message):
        suggest_product_list['type'] = message.text
        markup_remove = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Please input the name of the product:', reply_markup=markup_remove)
        bot.register_next_step_handler(message, input_suppliers_name)

    def input_suppliers_name(message):
        suggest_product_list['name'] = message.text.capitalize()
        bot.send_message(message.chat.id, "Specify the supplier's company name")
        bot.register_next_step_handler(message, input_calories)

    def input_calories(message):
        suggest_product_list['supplier'] = message.text.capitalize()
        bot.send_message(message.chat.id, "Input the amount of calories of the product per 100g")
        bot.register_next_step_handler(message, process_calories_data)

    def process_calories_data(message):
        try:
            suggest_product_list['calories'] = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "The value must be numerical")
            return
        bot.send_message(message.chat.id, 
                'Input the amount of <b>Proteins, Carbs, Sugars, Fats and Fiber </b>'
                'separated by spaces, e.g., <b>21 30 17 4 0</b>', parse_mode="HTML"
        )
        bot.register_next_step_handler(message, input_nutrition_data)

    def input_nutrition_data(message):
        nutrients = message.text.split()
        if len(nutrients) != 5:
            bot.send_message(message.chat.id, "Something is wrong in your data. Please try again.")
            return
        try:
            nutrients = list(map(float, nutrients))
            proteins, carbs, sugars, fats, fiber = nutrients
        except ValueError:
            bot.send_message(message.chat.id, "Please enter valid numeric values for nutrients.")
            return
        
        product_type = suggest_product_list['type']
        product_name = suggest_product_list['name']
        product_supplier = suggest_product_list['supplier']
        product_calories = suggest_product_list['calories']

        product_tuple = (f'@{message.from_user.username}', 
                        product_type, product_name, 
                        product_supplier, product_calories, 
                        proteins, carbs, sugars, fats, fiber
        )
        connection = db_manager.connect_to_db()
        cursor = connection.cursor()
        db_manager.suggest_adding_product(cursor, product_tuple)
        connection.commit()
        connection.close()

        bot.send_message(message.chat.id, "<b>Success! The admin has been notified, please wait for approval.</b>", parse_mode="HTML")

    ## Search for a product

    def search_product_menu(message):
        if message.text == "Search by type" or message.text == "Select by type":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for type in db_manager.product_types:
                markup.add(type)
            bot.send_message(message.chat.id, "Please choose the type:", reply_markup=markup)
            if message.text == "Search by type":
                bot.register_next_step_handler(message, search_by_type)
            else:
                bot.register_next_step_handler(message, select_by_type)
        elif message.text == 'Search by supplier' or message.text == "Select by supplier":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            suppliers = db_manager.inspect_suppliers()
            if len(suppliers) != 0:
                for row in suppliers:
                    markup.add(row[0])
            else: 
                bot.send_message(message.chat.id, "No suppliers were found in the database.")
                return
            bot.send_message(message.chat.id, "Select a supplier:", reply_markup=markup)
            if message.text == "Search by supplier": 
                bot.register_next_step_handler(message, search_by_supplier)
            else:
                bot.register_next_step_handler(message, select_by_supplier)
        elif message.text == 'Search by name' or 'Select by name':
            bot.send_message(message.chat.id, "Please write the name of the product:")
            if message.text == "Search by name":
                bot.register_next_step_handler(message, search_by_name)
            else:
                bot.register_next_step_handler(message, select_by_name)


    # Search by type

    def search_by_type(message):
        type = message.text
        markup_remove = types.ReplyKeyboardRemove()
        list_of_products = db_manager.inspect_by_type(type)

        if not list_of_products:
            bot.send_message(message.chat.id, f"No products of type \"{type}\" were found")
            return

        response = f"<b>Selected by type \"{type}\":</b>\n"
        
        for product in list_of_products:
            product_name = product[0][1]
            product_supplier = product[0][3]
            product_type = product[0][2]
            product_calories = product[0][4]
            product_proteins = product[1][0]
            product_carbs = product[1][1]
            product_sugars = product[1][2]
            product_fats = product[1][3]
            product_fibers = product[1][4]

            response += f"""
            <b>Name:</b> {product_name}
            <b>Supplier:</b> {product_supplier}
            <b>Type:</b> {product_type}
            <b>Calories:</b> {product_calories}
            <b>Proteins:</b> {product_proteins}
            <b>Carbs:</b> {product_carbs}
            \tfrom which <b>sugars:</b> {product_sugars}
            <b>Fats:</b> {product_fats}
            <b>Fibers:</b> {product_fibers}\n
            """
        
        bot.send_message(message.chat.id, response, parse_mode="HTML", reply_markup=markup_remove)


    # Search by supplier

    def search_by_supplier(message):
        supplier = message.text
        markup_remove = types.ReplyKeyboardRemove()

        list_of_products = db_manager.inspect_by_supplier(supplier)

        if not list_of_products:
            bot.send_message(message.chat.id, f"No products of type \"{supplier}\" were found")
            return

        response = f"<b>Selected by supplier \"{supplier}\":</b>\n"
        
        for product in list_of_products:
            product_name = product[0][1]
            product_supplier = product[0][3]
            product_type = product[0][2]
            product_calories = product[0][4]
            product_proteins = product[1][0]
            product_carbs = product[1][1]
            product_sugars = product[1][2]
            product_fats = product[1][3]
            product_fibers = product[1][4]

            response += f"""
            <b>Name:</b> {product_name}
            <b>Supplier:</b> {product_supplier}
            <b>Type:</b> {product_type}
            <b>Calories:</b> {product_calories}
            <b>Proteins:</b> {product_proteins}
            <b>Carbs:</b> {product_carbs}
            \tfrom which <b>sugars:</b> {product_sugars}
            <b>Fats:</b> {product_fats}
            <b>Fibers:</b> {product_fibers}\n
            """
        
        bot.send_message(message.chat.id, response, parse_mode="HTML", reply_markup=markup_remove)

    # Search by name

    def search_by_name(message):
        name = message.text.capitalize()
        markup_remove = types.ReplyKeyboardRemove()

        list_of_products = db_manager.inspect_by_name(name)

        if not list_of_products:
            bot.send_message(message.chat.id, f"No products of name \"{name}\" were found")
            return

        response = f"<b>Selected by name \"{name}\":</b>\n"
        
        for product in list_of_products:
            product_name = product[0][1]
            product_supplier = product[0][3]
            product_type = product[0][2]
            product_calories = product[0][4]
            product_proteins = product[1][0]
            product_carbs = product[1][1]
            product_sugars = product[1][2]
            product_fats = product[1][3]
            product_fibers = product[1][4]

            response += f"""
            <b>Name:</b> {product_name}
            <b>Supplier:</b> {product_supplier}
            <b>Type:</b> {product_type}
            <b>Calories:</b> {product_calories}
            <b>Proteins:</b> {product_proteins}
            <b>Carbs:</b> {product_carbs}
            \tfrom which <b>sugars:</b> {product_sugars}
            <b>Fats:</b> {product_fats}
            <b>Fibers:</b> {product_fibers}\n
            """
        
        bot.send_message(message.chat.id, response, parse_mode="HTML", reply_markup=markup_remove)

    # Select by type

    def select_by_type(message):
        type = message.text
        markup_remove = types.ReplyKeyboardRemove()

        list_of_products = db_manager.inspect_by_type(type)

        if not list_of_products:
            bot.send_message(message.chat.id, f"No products of type \"{type}\" were found", reply_markup=markup_remove)
            return
        
        markup_inline = types.InlineKeyboardMarkup(row_width=2)
        for product in list_of_products:
            product_id = product[0][0]
            product_name = product[0][1]
            product_supplier = product[0][3]
            markup_inline.add(types.InlineKeyboardButton(f'{product_name} by "{product_supplier}"', callback_data=f"product_{product_id}"))
        bot.send_message(message.chat.id, "Pick a product to add to the cart:", reply_markup=markup_inline)


    # Select by supplier

    def select_by_supplier(message):
        pass

    # Select by name

    def select_by_name(message):
        pass

    @bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
    def add_products_to_cart(callback):
        if callback.message:
            if len(selected_products) >= 7:
                bot.send_message(callback.message.chat.id, "The cart is full. You can add at most 7 products.")
                return
            splitted_callback = callback.data.split('_')
            product_id = splitted_callback[1]
            product = db_manager.find_by_id(product_id)
            if product is None:
                bot.answer_callback_query(callback.id, "No products found.", show_alert=True)
                return

            bot.send_message(callback.message.chat.id, "Specify the amount of the product: (e.g., 100g...)")
            bot.register_next_step_handler(callback.message, lambda message: mass_calculation(message, product))

    def mass_calculation(message, product):
        try:
            mass = int(message.text)
            if not (1 <= mass <= 10000):
                bot.send_message(message.chat.id, "Invalid input for mass in gramms.")
                return
            selected_products.append((product, mass))
            bot.send_message(message.chat.id, f"{mass} gramms of '{product[1]}' have been added!")
        except ValueError:
            bot.send_message(message.chat.id, "Invalid input for mass in gramms.")


    ## Modify data (admin privileges only)

    def check_admin_password(message):
        users = admin.AdminInterface.check_admins()
        if message.text == admin.password and f"@{message.from_user.username}" in users:
            bot.reply_to(message, "<b>Access granted!</b>", parse_mode="HTML")
            markup = types.InlineKeyboardMarkup(row_width=2)

            inspect_suggestions = types.InlineKeyboardButton('Inspect current suggestions', callback_data='inspect_suggestions')
            delete_product = types.InlineKeyboardButton('Delete a product', callback_data='delete_product')
            grant_privileges = types.InlineKeyboardButton('Grant privileges', callback_data='grant_privileges')
            
            markup.add(inspect_suggestions, delete_product, grant_privileges)

            bot.send_message(message.chat.id, "<b>Select one of the options:</b>", parse_mode="HTML", reply_markup=markup)
        else:
            bot.reply_to(message, "Wrong password or lack of privileges. Please try again.")
            return
    
    selected_suggestions = {}

    @bot.callback_query_handler(func=lambda call : call.data in ['inspect_suggestions', 'delete_product', 'grant_privileges'])
    def answer_admin_menu(callback):
        if callback.message:
            if callback.data == 'inspect_suggestions':
                list_suggestions = admin.AdminInterface.check_database_for_suggestion()
                if len(list_suggestions) == 0:
                    bot.answer_callback_query(callback.id, "No suggestions found.", show_alert=True)
                    return 
                
                render_suggestions_menu(callback.message.chat.id, list_suggestions)
            elif callback.data == 'grant_privileges':
                users = admin.AdminInterface.inspect_login_data()
                response = "<b>Login Data:</b>\n\n"
                for user in users:
                    tg_username, privilege = user 
                    response += f"Username: {tg_username}, Privilege: {privilege}\n"
                
                bot.send_message(callback.message.chat.id, response, parse_mode="HTML")
                bot.send_message(callback.message.chat.id, "Type in manually usernames to grant privilege 'admin', separated by spaces & including '@'")
                bot.register_next_step_handler(callback.message, grant_privileges)
            elif callback.data == 'delete_product':
                bot.send_message(callback.message.chat.id, "Please write the name of the product")
                bot.register_next_step_handler(callback.message, find_product_to_delete)

    def render_suggestions_menu(chat_id, list_suggestions):
        markup = types.InlineKeyboardMarkup(row_width=2)

        for suggestion in list_suggestions:
            suggestion_id = suggestion[0]
            product_type = suggestion[2]
            product_name = suggestion[3]
            product_supplier = suggestion[4]

            selected = selected_suggestions.get(suggestion_id, False)
            button_text = f"{'✅' if selected else '⬜'} {product_type}: {product_name} by \"{product_supplier}\""

            markup.add(types.InlineKeyboardButton(button_text, callback_data=f"toggle_{suggestion_id}"))

        markup.add(types.InlineKeyboardButton("✅ Submit", callback_data="submit_suggestions"))

        bot.send_message(chat_id, "<b>Please review the following suggestions:</b>", parse_mode="HTML", reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_"))
    def toggle_suggestion(callback):
        suggestion_id = int(callback.data.split('_')[1])

        if suggestion_id in selected_suggestions:
            selected_suggestions[suggestion_id] = not selected_suggestions[suggestion_id]
        else:
            selected_suggestions[suggestion_id] = True

        list_suggestions = admin.AdminInterface.check_database_for_suggestion()
        markup = types.InlineKeyboardMarkup(row_width=2)

        for suggestion in list_suggestions:
            suggestion_id = suggestion[0]
            product_type = suggestion[2]
            product_name = suggestion[3]
            product_supplier = suggestion[4]

            selected = selected_suggestions.get(suggestion_id, False)
            button_text = f"{'✅' if selected else '⬜'} {product_type}: {product_name} by \"{product_supplier}\""

            markup.add(types.InlineKeyboardButton(button_text, callback_data=f"toggle_{suggestion_id}"))

        markup.add(types.InlineKeyboardButton("✅ Submit", callback_data="submit_suggestions"))

        bot.edit_message_text(
                "<b>Please review the following suggestions:</b>",
                callback.message.chat.id,
                callback.message.message_id,
                parse_mode="HTML",
                reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data == "submit_suggestions")
    def submit_selected_suggestions(callback):
        selected_ids = [suggestion_id for suggestion_id, is_selected in selected_suggestions.items() if is_selected]

        if not selected_ids:
            bot.answer_callback_query(callback.id, "No suggestions were selected.", show_alert=True)
            return
        
        result = admin.AdminInterface.add_selected_suggestions(selected_ids)

        if result:
            bot.send_message(callback.message.chat.id, "Selected suggestions have been successfully added to the database.")
        else:
            bot.send_message(callback.message.chat.id, "Error adding suggestions to the database.")

        selected_suggestions.clear()

    def grant_privileges(message):
        users_to_be_granted = message.text.split()
        current_users = {user[0] for user in admin.AdminInterface.inspect_login_data()}
        valid_users = [user for user in users_to_be_granted if user in current_users]
        
        if not valid_users:
            bot.send_message(message.chat.id, "Error: No valid usernames found in the database.")
            return
        
        result = admin.AdminInterface.grant_privileges(valid_users)
        
        if result:
            bot.send_message(message.chat.id, "Privileges granted to the following users: " + ", ".join(valid_users))
        else:
            bot.send_message(message.chat.id, "Error: Some usernames may not exist or there was an issue granting privileges.")

    def find_product_to_delete(message):
        name = message.text.capitalize()
        markup = types.InlineKeyboardMarkup(row_width=2)

        list_of_products = db_manager.inspect_by_name(name)
        if not list_of_products:
            bot.send_message(message.chat.id, "No product with such name was found")
            return
        for product in list_of_products:
            markup.add(types.InlineKeyboardButton(f"{product[0][1]} by '{product[0][3]}'", callback_data=f"delete_{product[0][1]}_{product[0][3]}"))

        bot.send_message(message.chat.id, "<b>Click on the product to delete:</b>", parse_mode="HTML", reply_markup=markup)
        return

    @bot.callback_query_handler(func=lambda call : call.data.startswith('delete_'))
    def delete_product(callback):
        if callback.message:
            product_data = callback.data.split("_")
            product_name = product_data[1]
            product_supplier = product_data[2]

            deleted_bool = admin.AdminInterface.delete_product_from_db(product_name, product_supplier)

            if deleted_bool:
                bot.send_message(callback.message.chat.id, f"{product_name} by '{product_supplier}' has been succesfully deleted!")
            else:
                bot.send_message(callback.message.chat.id, "Error deleting a product. Please try again.")

    bot.infinity_polling()  