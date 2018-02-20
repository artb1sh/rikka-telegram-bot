#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
from random import randint
import importlib
import datetime
import logging
import yaml
import os
import re


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("telegram.utils.promise").propagate = False

class Globals:
    def __init__(self, updater, dp, config):
        self.updater = updater
        self.dp = dp
        self.config = config
        


# Import logo from a text file
with open("resources/logo.txt", "r", encoding="UTF-8") as logo_file:
    logo = logo_file.read()
    print(logo)

# Load configs & create folders
with open("config.yml", "r") as f:
    config = yaml.load(f)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
key = config["keys"]["telegram_token"]
updater = Updater(token=key)
dp = updater.dispatcher

for feature in config["features"]:
    if "path" in config["features"][feature]:
        path = config["features"][feature]["path"]
        if not os.path.exists(path):
            os.makedirs(path)
    if config["features"][feature]["enabled"] is True:
        module_config = config["features"][feature]
        global_data = gd = Globals(updater, dp, module_config)
        module = importlib.import_module("modules." + feature).module_init(gd)
        print(feature)


# Import /help from a text file
with open("resources/help.txt", "r", encoding="UTF-8") as helpfile:
    help_text = helpfile.read()
    print("Help textfile imported")


# Start feature
def start(bot, update):
    if update.message.chat.type != "private":
        return
    with open("resources/hello.webp", "rb") as hello:
        update.message.reply_sticker(hello, quote=False)
    personname = update.message.from_user.first_name
    update.message.reply_text("Konnichiwa, " + personname + "! \nMy name is Takanashi Rikka desu! \
                              \nUse /help to see what I can do! :3", quote=False)
    print(datetime.datetime.now(), ">>>", "Done /start", ">>>", update.message.from_user.username)
dp.add_handler(CommandHandler("start", start))


# Show help
def help(bot, update):
    bot.send_message(update.message.chat_id, help_text, parse_mode="Markdown")
    print(datetime.datetime.now(), ">>>", "Done /help", ">>>", update.message.from_user.username)
dp.add_handler(CommandHandler("help", help))


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)
dp.add_error_handler(error)

# Starting bot
updater.start_polling(clean=True, bootstrap_retries=4, read_latency=2.0)
# Run the bot until you presses Ctrl+C
print("=====================\nUp and running!\n")
#Idle
updater.idle()
