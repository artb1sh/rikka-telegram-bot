from modules.logging import logging_decorator
from telegram import ChatAction
from telegram.ext import CommandHandler
import requests
import random


def module_init(gd):
    global default_rating
    default_rating = gd.config['default_rating']
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, gelbooru_search, pass_args=True))


@logging_decorator('gel')
def gelbooru_search(bot, update, args):
    if not any(arg.startswith('rating:') for arg in args):
        args = args + ['rating:{}'.format(default_rating)]
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = ' '.join(args)
    try:
        final_img, id_ = get_image(query)
    except:
        update.message.reply_text("Sorry, случилась какая-то жопа!")
        raise
    if final_img is None:
        update.message.reply_text("Nothing found!")
        return
    post_link = 'https://gelbooru.com/index.php?page=post&s=view&id={}'.format(id_)
    msg_text = "[img]({})\n\n[post]{}".format(final_img, post_link)
    update.message.reply_text(msg_text, parse_mode="Markdown")


def get_image(query):
    params = {
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'json': '1',
        'tags': query,
    }
    response = requests.get('https://gelbooru.com/index.php', params=params)
    if not response.text:
        return None, None
    result_list = response.json()
    if not result_list:
        return None, None
    post = random.choice(result_list)
    link = post.get('file_url')
    id_ = post.get('id')
    return link, id_
