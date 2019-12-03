from telegram.ext import CommandHandler
from modules.logging import logging_decorator
from random import randint, seed
import random
import re

choices = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
           "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
           "Yes", "Signs point to yes", "Reply hazy try again", "Ask again later",
           "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
           "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
           "Very doubtful"]

splitter_ru = " или "
splitter_en = " or "
splitters = [" or ", " или "]


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, roll, pass_args=True))


def mysteryball(update, string):
    seed() if string == "" else seed(string)
    answer = randint(0, len(choices)-1)
    update.message.reply_text("🎱 " + choices[answer])


def splitter_check(update, text):
    for splitter in splitters:
        if splitter in text:
            return splitter


def rolling_process(update, split_text):
    randoms = tuple(sorted(split_text))
    seed(randoms)
    answer = random.choice(split_text)
    update.message.reply_text(answer)


def numbers_check(update, text):
    try:
        rng_end = int(text)
        return 0, rng_end
    except ValueError:
        pass
    if "-" in text:
        numbers = text.split("-")
        try:
            rng_start = int(numbers[0])
            rng_end = int(numbers[1])
            return rng_start, rng_end
        except:
            return None, None
    else:
        return None, None


def dice(update, number1, number2):
    if number1 is not None and number2 is not None:
        number1, number2 = sorted([number1, number2])
        random_number = randint(number1, number2)
        update.message.reply_text("🎲 {}".format(random_number))
        return True


@logging_decorator('roll')
def roll(bot, update, args):
    full_text = ' '.join(args)
    rng_start, rng_end = numbers_check(update, full_text)
    if dice(update, rng_start, rng_end):
        return
    splitter = splitter_check(update, full_text)
    if splitter:
        split_text = full_text.split(splitter)
        rolling_process(update, full_text, split_text)
    else:
        mysteryball(update, full_text)
