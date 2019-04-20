from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler
from modules.logging import logging_decorator
from telegram import ChatAction
from random import randint
import os


def module_init(gd):
    global path, files, filecount
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, nya))
    files = os.listdir(path)
    filecount = len(files)
    print("Nya images: ", filecount)


@run_async
@logging_decorator('nya')
def nya(bot, update):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    rand = randint(0, filecount-1)
    result = files[rand]
    with open(path+"/"+str(result), "rb") as f:
        update.message.reply_photo(f)
