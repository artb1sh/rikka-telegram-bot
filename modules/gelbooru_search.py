from modules.logging import log_command
from telegram import ChatAction
from telegram.ext import CommandHandler
import requests
import random
from datetime import datetime


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, gelbooru_search, pass_args=True))


def gelbooru_search(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = ' '.join(args)
    try:
        final_img = get_image(query)
    except:
        update.message.reply_text("Sorry, случилась какая-то жопа!")
        return
    if final_img is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[link]({})".format(final_img)
    update.message.reply_text(msg_text, parse_mode="Markdown")
    print(current_time, ">", "/gel", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "gel")


def get_image(query):
    params = {
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'json': '1',
        'tags': query,
    }
    response = requests.get('https://gelbooru.com/index.php', params=params)
    result_list = response.json()
    if not result_list:
        return None
    post = random.choice(result_list)
    link = post.get('file_url')
    return link
