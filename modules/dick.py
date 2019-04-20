from modules.logging import logging_decorator
from telegram.ext import CommandHandler
import random


def module_init(gd):
    global mu, sigma
    mu = gd.config['mu']
    sigma = gd.config['sigma']
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, get_dick_size))


@logging_decorator('dick')
def get_dick_size(bot, update):
    random.seed(update.message.from_user.id)
    size = random.gauss(mu, sigma)
    msg_text = 'Длина Вашего члена {} см.'.format(size)
    update.message.reply_text(msg_text)
