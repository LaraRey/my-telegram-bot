from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram ID администратора
ADMIN_ID = 8072909779  # <- замени на свой ID

# Словарь для хранения активных сессий пользователей
active_chats = {}

# Команда /start_chat — пользователь начинает диалог
async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in active_chats:
        await update.message.reply_text("У тебя уже есть активная сессия. Напиши своё сообщение.")
        return

    # Создаём новую сессию
    active_chats[user_id] = {"message": None}
    await update.message.reply_text("Напиши сообщение, которое ты хочешь отправить администратору:")

# Перехватываем текст от пользователя
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Если пользователь не начал сессию — игнорируем сообщение
    if user_id not in active_chats:
        await update.message.reply_text("Чтобы написать сообщение, сначала введи команду /start_chat")
        return

    # Сохраняем сообщение
    active_chats[user_id]["message"] = update.message.text

    # Пересылаем администратору
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Сообщение от {update.message.from_user.first_name} "
             f"(@{update.message.from_user.username}, id={user_id}):\n{update.message.text}"
    )

    await update.message.reply_text("Сообщение отправлено администратору! Ожидайте ответа.")

# Команда /reply — админ отвечает пользователю
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return  # только админ

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /reply <user_id> <сообщение>")
        return

    user_id = int(context.args[0])
    reply_text = " ".join(context.args[1:])

    # Проверка, есть ли активная сессия
    if user_id not in active_chats:
        await update.message.reply_text("Сессия с этим пользователем неактивна.")
        return

    # Отправка сообщения пользователю
    await context.bot.send_message(chat_id=user_id, text=reply_text)

    # Уведомление пользователя о закрытии сессии
    await context.bot.send_message(chat_id=user_id, text="Сессия с администратором завершена. Чтобы написать снова, используй /start_chat.")

    # Закрываем сессию
    del active_chats[user_id]
    await update.message.reply_text(f"Сообщение отправлено пользователю {user_id}, сессия закрыта.")

# Запуск бота
if __name__ == "__main__":
    TOKEN = "8023291896:AAHLylZMF7pcTWkC_VfL6xFCztMkoxCsUy4"  # <- вставь сюда свой токен
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start_chat", start_chat))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CommandHandler("reply", reply))

    app.run_polling()
