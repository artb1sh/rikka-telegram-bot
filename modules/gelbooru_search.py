from modules.logging import logging_decorator
from telegram import ChatAction
from telegram.ext import CommandHandler
import requests
import random
import tempfile
import os
import subprocess


def module_init(gd):
    global default_rating
    default_rating = gd.config['default_rating']
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, gelbooru_search, pass_args=True))


@logging_decorator('gel')
def gelbooru_search(bot, update, args):
    #if not any(arg.startswith('rating:') for arg in args):
    #    args = args + ['rating:{}'.format(default_rating)]
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
    msg_text = "[img]({}) [post]({})".format(final_img, post_link)
    base, ext = os.path.splitext(final_img)
    filename = 'gelbooru' + ext
    print(final_img)
    print(filename)
    with open(filename, 'wb') as tf:
        r = requests.get(final_img, stream=True)
        for chunk in r:
            tf.write(chunk)
        print(r.status_code)
        print(r.headers['content-type'])
        print(r.encoding)
    if ext in ['.gif', '.webm']:
        subprocess.call(['ffmpeg', '-i', filename, '-y', '-vf', "scale='min(100,iw)':'-1'", 'gelbooru.mp4'])
        filename = 'gelbooru.mp4'
        ext = '.mp4'
    with open(filename, 'rb') as tf:
        if ext == '.mp4':
            update.message.reply_document(tf)
            update.message.reply_text(msg_text, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            update.message.reply_photo(tf, caption=msg_text, parse_mode="Markdown")


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
