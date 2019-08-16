from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import sqlite3


def module_init(gd):
    global bot_id
    bot_id = gd.config['bot_id']
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, delete))


def delete(bot, update):
    post_id = update.message.reply_to_message.message_id
    print(update.message.reply_to_message)
    if update.message.reply_to_message.from_user.id == bot_id:
        bot.delete_message(update.message.chat_id, post_id)


