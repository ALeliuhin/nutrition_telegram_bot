import telebot
from telebot import types
import db_manager, admin
from datetime import datetime

BOT_TOKEN = admin.os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


if __name__ == '__main__' :

    suggest_product_ansewers = {}

    @bot.message_handler(commands=['start'])
    def start_command(message):
        markup_remove = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f'Welcome, {message.from_user.username}! Use the /menu button below to access the menu:', reply_markup=markup_remove)
        connection = db_manager.connect_to_db()
        cursor = connection.cursor()
        db_manager.create_tables_db(cursor)
        db_manager.add_user_to_db(cursor, f'@{message.from_user.username}', message.from_user.first_name, 
                            "admin" if message.from_user.username == "olegovich_la" else "user", 
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'
        )
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

    @bot.message_handler(commands=['menu'])
    def main_menu_interface(message):
        markup = types.InlineKeyboardMarkup(row_width=2)

        search = types.InlineKeyboardButton('Search for a product', callback_data='choice_search')
        select_meal = types.InlineKeyboardButton('Select food', callback_data='choice_select')
        suggest = types.InlineKeyboardButton('Suggest food to add', callback_data='choice_suggest')
        admin_change = types.InlineKeyboardButton('Modify data (admin)', callback_data='choice_modify')

        markup.add(search, select_meal, suggest, admin_change)

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
                bot.send_message(callback.message.chat.id, "In development!")
            elif callback.data == 'choice_select':
                bot.send_message(callback.message.chat.id, "In development!")


    ### Suggest a product

    def input_name(message):
        suggest_product_ansewers['type'] = message.text
        markup_remove = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Please input the name of the product:', reply_markup=markup_remove)
        bot.register_next_step_handler(message, input_suppliers_name)

    def input_suppliers_name(message):
        suggest_product_ansewers['name'] = message.text.capitalize()
        bot.send_message(message.chat.id, "Specify the supplier's company name")
        bot.register_next_step_handler(message, input_calories)

    def input_calories(message):
        suggest_product_ansewers['supplier'] = message.text.capitalize()
        bot.send_message(message.chat.id, "Input the amount of calories of the product per 100g")
        bot.register_next_step_handler(message, process_calories_data)

    def process_calories_data(message):
        try:
            suggest_product_ansewers['calories'] = int(message.text)
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
        
        product_type = suggest_product_ansewers['type']
        product_name = suggest_product_ansewers['name']
        product_supplier = suggest_product_ansewers['supplier']
        product_calories = suggest_product_ansewers['calories']

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
        
    ### Modify data (admin privileges only)

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


    bot.infinity_polling()  