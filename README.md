# Nutrition Telegram Bot

Welcome to the **Nutrition Telegram Bot**! 🥗🤖

This bot is designed to help users easily manage and explore nutrition data for various products, all through a simple and intuitive Telegram interface. Whether you're looking to inspect product details, compose a meal, or suggest new products, this bot has you covered!

---

## Features 🚀

- **Product Lookup**: Search for a product and view detailed nutrition information.
- **Meal Composition**: Select products and combine them to create a meal.
- **Recipe Generation**: Generate a recipe using selected products via OpenAI API.
- **Product Suggestions**: Suggest new products and have them added to the database.
- **Admin Privileges**: Certain users can be granted *admin* rights to modify data directly from the bot interface.
- **Supplier Information**: Easily manage supplier names and their related products.
  
---

## Current Implementation

### Hardware 💻

- **Raspberry Pi 4**: The bot is hosted on a Raspberry Pi 4, serving as a micro-server.

### Software 🛠️

- **Python**: Tested on versions 3.7 through 3.12.
- **SQLite3**: For lightweight, file-based database storage.
- **pyTelegramBotAPI**: A Python library that interfaces with Telegram's Bot API.
- **Telegram Application**: User interaction with the bot is done via the Telegram app.
- **OpenAI API**: For recipe generation based on a predefined prompt.

---

## Installation Guide 📝

1. **Clone the repository**:

    ```bash
    git clone https://github.com/ALeliuhin/nutrition_telegram_bot
    ```

2. **Set up Python environment**:

    - Make sure you have Python 3.7+ installed.
    - Install dependencies:

      ```bash
      pip install pyTelegramBotAPI
      
      pip install openai

      pip install pydantic
      ```

3. **Configure your bot**:
    - Create a new bot via [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
    - Obtain the API token and add it to the bot's configuration file, specifically to /activate script as an environment varible.

4. **Run the bot**:

    ```bash
    python main.py
    ```

---

## Usage Instructions 📖

1. **Start the bot**: Once you have set up the bot, you can find it on Telegram and start interacting with it using `/start`.
2. **Admin functions**: If you are an admin, you will have access to additional commands to interact with the database.
3. **Suggestions**: Any user can suggest new products, which will be reviewed and possibly added to the database.
4. **Product lookup**: Search for a product by name and view its detailed nutritional information.
5. **Meal composition**: Select products and combine them to create a meal.
6. **Recipe generation**: Generate a recipe using selected products via OpenAI API.
7. **Supplier information**: Easily manage supplier names and their related products.

---

## Database Structure 🗄️

- **Products**: Stores all products with their respective nutritional information.
- **Suppliers**: Keeps track of supplier names and associates them with products.
- **Types**: Contains product types (e.g., fruits, vegetables, dairy).
- **Nutrition Info**: Detailed nutrition information (calories, proteins, carbs, etc.) for each product.
- **User Suggestions**: Stores user suggestions for new products to be added to the database.
- **LoginData**: Contains login information for users.

---

## Contact 📧

- For any inquiries, please contact me at `aleliuhin@gmail.com`.

---

Enjoy using the **Nutrition Telegram Bot** and stay healthy! 🌱🥑