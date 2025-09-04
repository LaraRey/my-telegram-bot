from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram ID администратора
ADMIN_ID = 8072909779  # <- замени на свой реальный ID

# Словарь для хранения активных сессий пользователей
active_chats = {}

# /start_chat — начало диалога
async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in active_chats:
        await update.message.reply_text("У тебя уже есть активная сессия. Напиши сообщение.")
        return

    active_chats[user_id] = {"message": None}
    await update.message.reply_text(
        "Привет! Напиши сообщение, которое ты хочешь отправить администратору:"
    )

# Обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in active_chats:
        await update.message.reply_text(
            "Чтобы написать сообщение, сначала введи команду /start_chat"
        )
        return

    active_chats[user_id]["message"] = update.message.text

    # Отправляем сообщение админу
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"Сообщение от {update.message.from_user.first_name} "
            f"(@{update.message.from_user.username}, id={user_id}):\n"
            f"{update.message.text}"
        ),
    )

    await update.message.reply_text(
        "Сообщение отправлено администратору! Ожидайте ответа."
    )

# /reply — ответ админа пользователю
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /reply <user_id> <сообщение>")
        return

    user_id = int(context.args[0])
    reply_text = " ".join(context.args[1:])

    if user_id not in active_chats:
        await update.message.reply_text("Сессия с этим пользователем неактивна.")
        return

    await context.bot.send_message(chat_id=user_id, text=reply_text)
    await context.bot.send_message(
        chat_id=user_id,
        text="Сессия с администратором завершена. Чтобы написать снова, используй /start_chat."
    )

    del active_chats[user_id]
    await update.message.reply_text(
        f"Сообщение отправлено пользователю {user_id}, сессия закрыта."
    )


# ===========================
# Запуск бота через Render
# ===========================
if __name__ == "__main__":
    TOKEN = "8023291896:AAHLylZMF7pcTWkC_VfL6xFCztMkoxCsUy4"  # твой токен
    WEBHOOK_URL = "https://my-telegram-bot-16-fp2s.onrender.com"  # URL сервиса Render

    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд и сообщений
    app.add_handler(CommandHandler("start_chat", start_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("reply", reply))

    # Запуск webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )
