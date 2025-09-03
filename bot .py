{\rtf1\ansi\ansicpg1251\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
}from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = 8023291896:AAHLylZMF7pcTWkC_VfL6xFCztMkoxCsUy4
YOUR_TELEGRAM_ID = 8072909779

user_messages = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Напиши мне сообщение, и я передам его владельцу бота.")

def receive_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    user_messages[user_id] = text

    update.message.reply_text("Сообщение получено! Владелец бота скоро ответит.")

    context.bot.send_message(
        chat_id=YOUR_TELEGRAM_ID,
        text=f"📩 Новое сообщение от {update.message.from_user.first_name} ({user_id}):\n{text}"
    )

def reply_user(update: Update, context: CallbackContext):
    if update.message.from_user.id != YOUR_TELEGRAM_ID:
        update.message.reply_text("У вас нет доступа к этой команде.")
        return

    try:
        user_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])
        context.bot.send_message(chat_id=user_id, text=reply_text)
        update.message.reply_text("✅ Ответ отправлен пользователю!")
    except (IndexError, ValueError):
        update.message.reply_text("Использование: /reply <user_id> <текст ответа>")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reply", reply_user))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
