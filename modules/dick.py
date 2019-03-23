from modules.logging import log_command
from datetime import datetime
from telegram.ext import CommandHandler
import random


def module_init(gd):
    global mu, sigma
    mu = gd.config['mu']
    sigma = gd.config['sigma']
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, gelbooru_search, pass_args=True))

def gelbooru_search(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    random.seed(update.message.from_user.id)
    size = random.gauss(mu, sigma)
    msg_text = 'Длина Вашего члена {} см.'.format(size)
    update.message.reply_text(msg_text, parse_mode="Markdown")
    print(current_time, ">", "/dick", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "dick")