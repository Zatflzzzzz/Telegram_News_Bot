import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import requests

from app.config.config import settings

TOKEN = settings.TELEGRAM_BOT_TOKEN
API_URL = "http://localhost:8000"

def register(username: str, password: str):

    data = {"username": username, "password": password}
    response = requests.post(f"{API_URL}/register", params=data)

    if response.status_code == 200:
        return "Регистрация успешна! Теперь выполните вход с помощью /login."

    return f"Ошибка регистрации: {response.json().get('detail', 'Неизвестная ошибка')}"

def login(username: str, password: str):

    data = {"username": username, "password": password}
    response = requests.post(f"{API_URL}/login", params=data)

    if response.status_code == 200:
        token = response.json()["access_token"]
        return token

    return None

user_tokens = {}

async def start(
        update: Update,
        context: CallbackContext):
    await update.message.reply_text("Привет! Я бот для получения новостей.\n"
                                    "Команды:\n"
                                    "/register <username> <password> – регистрация\n"
                                    "/login <username> <password> – вход\n"
                                    "/news_by_category <category> – получить новости по интересующей вас категории. Вот список доступных категорий:\n\n"
                                    "---------------------"
                                    "\nbusiness\n"
                                    "entertainment\n"
                                    "general\n"
                                    "health\n"
                                    "science\n"
                                    "sports\n"
                                    "technology\n"
                                    "---------------------\n\n"
                                    "/last_popular_news – получить самые последние новости в России")


async def register_user(
        update: Update,
        context: CallbackContext):

    if len(context.args) < 2:
        await update.message.reply_text("Используйте: /register <username> <password>")
        return

    username, password = context.args
    response = register(username, password)

    await update.message.reply_text(response)


async def login_user(
        update: Update,
        context: CallbackContext):

    if len(context.args) < 2:
        await update.message.reply_text("Используйте: /login <username> <password>")
        return

    username, password = context.args

    token = login(username, password)

    if token:
        user_tokens[update.message.chat_id] = token

        await update.message.reply_text("Вход выполнен! Теперь вы можете получать новости")
    else:
        await update.message.reply_text("Ошибка входа. Проверьте логин и пароль.")


async def get_news_by_category(
        update: Update,
        context: CallbackContext):

    if update.message.chat_id not in user_tokens:
        await update.message.reply_text("Сначала выполните вход с помощью /login.")
        return

    if not context.args:
        await update.message.reply_text("Используйте: /news <category>")
        return

    category = context.args[0]
    headers = {"Authorization": f"Bearer {user_tokens[update.message.chat_id]}"}

    response = requests.get(f"{API_URL}/get_news_by_category?category={category}", headers=headers)

    if response.status_code == 200:
        news_list = response.json()

        for news in news_list:
            message = f"📰 Заголовок: {news['title']}\n\nАвтор: {news['author']}\n\nКатегория: {news["category"]}\n\n{news['urlToImage']}"
            await update.message.reply_text(message)
    else:
        await update.message.reply_text("Ошибка получения новостей.")


async def get_last_popular_news(
        update: Update,
        context: CallbackContext):

    if update.message.chat_id not in user_tokens:
        await update.message.reply_text("Сначала выполните вход с помощью /login.")
        return

    headers = {"Authorization": f"Bearer {user_tokens[update.message.chat_id]}"}

    response = requests.get(f"{API_URL}/get_last_popular_news", headers=headers)

    if response.status_code == 200:
        news_list = response.json()

        for news in news_list:
            message = f"📰 Заголовок: {news['title']}\n\nАвтор: {news['author']}\n\nКатегория: {news["category"]}\n\n{news['urlToImage']}"
            await update.message.reply_text(message)
    else:
        await update.message.reply_text("Ошибка получения новостей.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register_user))
    app.add_handler(CommandHandler("login", login_user))
    app.add_handler(CommandHandler("news_by_category", get_news_by_category))
    app.add_handler(CommandHandler("last_popular_news", get_last_popular_news))

    app.run_polling()

if __name__ == "__main__":
    main()
