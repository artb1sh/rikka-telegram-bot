from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from modules.logging import logging_decorator
from datetime import datetime
import random
import os


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, gif, pass_args=True))
    gd.dp.add_handler(MessageHandler(Filters.animation, save_gif))


@run_async
def save_gif(bot, update):
    message = update.message
    storage_dir_path = get_storage_dir_path(message.chat.id)
    saved_file_name = message.animation.file_id + '.mp4'
    saved_file_path = os.path.join(storage_dir_path, saved_file_name)
    os.makedirs(storage_dir_path, exist_ok=True)
    bot.getFile(message.animation.file_id).download(saved_file_path)


def get_storage_dir_path(chat_id):
    return os.path.join(path, str(chat_id))


@run_async
@logging_decorator('gif')
def gif(bot, update, args):
    storage_dir_path = get_storage_dir_path(update.message.chat.id)
    if not os.path.exists(storage_dir_path):
        update.message.reply_text("I don't know any gifs!")
    files = os.listdir(storage_dir_path)
    result_path = os.path.join(storage_dir_path, random.choice(files))
    with open(result_path, "rb") as f:
        update.message.reply_document(f)
