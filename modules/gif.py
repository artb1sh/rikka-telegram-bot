#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from modules.logging import log_command
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


def save_gif(bot, update):
    message = update.message
    storage_dir_path = os.path.join(path, str(message.chat.id))
    _, extension = os.path.splitext(message.animation.file_name)
    saved_file_name = message.animation.file_id + extension
    saved_file_path = os.path.join(storage_dir_path, saved_file_name)
    os.makedirs(storage_dir_path, exist_ok=True)
    bot.getFile(message.animation.file_id).download(saved_file_path)


@run_async
def gif(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    storage_dir_path = os.path.join(path, str(update.message.chat.id))
    if not os.path.exists(storage_dir_path):
        update.message.reply_text("I don't know any gifs!")
    files = os.listdir(storage_dir_path)
    result_path = os.path.join(storage_dir_path, random.choice(files))
    with open(result_path, "rb") as f:
        update.message.reply_document(f)
    log_command(bot, update, current_time, "gif")
