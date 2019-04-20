from telegram.ext import CommandHandler
from modules.logging import logging_decorator
from random import random, seed


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, rate))


def ifint(number):
    if number.is_integer():
        number = int(number)
        return number
    else:
        return number


@logging_decorator('rate')
def rate(bot, update):
    if update.message.reply_to_message is not None:
        seed(update.message.reply_to_message.message_id)
    rng = random() * 10
    rounded = round(rng * 2) / 2
    rating = str(ifint(rounded))
    update.message.reply_text("🤔 I rate this "+rating+"/10")
