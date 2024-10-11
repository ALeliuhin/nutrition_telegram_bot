import telebot
from telebot import types
import db_manager

BOT_TOKEN = "TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)


if __name__ == '__main__' :

    keyboard_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard_reply.add(types.KeyboardButton('/menu'))

    @bot.message_handler(commands=['start'])
    def start_command(message):
        bot.send_message(message.chat.id, 'Welcome! Use the /menu button below to access the menu:', reply_markup=keyboard_reply)

    @bot.message_handler(commands=['menu'])
    def question(message):
        markup = types.InlineKeyboardMarkup(row_width=2)

        search = types.InlineKeyboardButton('Search for a product', callback_data='choice_search')
        select_meal = types.InlineKeyboardButton('Select food', callback_data='choice_select')
        suggest = types.InlineKeyboardButton('Suggest food to add', callback_data='choice_suggest')
        admin_change = types.InlineKeyboardButton('Modify data (admin)', callback_data='choice_modify')

        markup.add(search, select_meal, suggest, admin_change)

        bot.send_message(message.chat.id, 'Welcome to the Main Menu', reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def answer(callback):
        if callback.message:
            if callback.data == 'choice_search':
                bot.send_message(callback.message.chat.id, 'Great choice!')

    bot.infinity_polling()
