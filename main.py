import telebot
from telebot import types
import db_manager
from datetime import datetime

BOT_TOKEN = "INSERT HERE"
bot = telebot.TeleBot(BOT_TOKEN)


if __name__ == '__main__' :

    @bot.message_handler(commands=['start'])
    def start_command(message):
        bot.send_message(message.chat.id, f'Welcome, {message.from_user.first_name}! Use the /menu button below to access the menu:')
        connection = db_manager.connect_to_db()
        cursor = connection.cursor()
        db_manager.create_tables_db(cursor)
        db_manager.add_user_to_db(cursor, f'@{message.from_user.username}', message.from_user.first_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
    def question(message):
        markup = types.InlineKeyboardMarkup(row_width=2)

        search = types.InlineKeyboardButton('Search for a product', callback_data='choice_search')
        select_meal = types.InlineKeyboardButton('Select food', callback_data='choice_select')
        suggest = types.InlineKeyboardButton('Suggest food to add', callback_data='choice_suggest')
        admin_change = types.InlineKeyboardButton('Modify data (admin)', callback_data='choice_modify')

        markup.add(search, select_meal, suggest, admin_change)

        bot.send_message(message.chat.id, '<b>Welcome to the Main Menu</b>', parse_mode= "HTML", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def answer(callback):
        if callback.message:
            if callback.data == 'choice_search':
                bot.answer_callback_query(callback.id, 'Great choice!')

    bot.infinity_polling()
