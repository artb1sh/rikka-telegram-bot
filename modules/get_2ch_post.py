from modules.logging import log_command
from datetime import datetime
from telegram.ext import CommandHandler
from html2text import html2text
import requests
import random


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, get_2ch_post, pass_args=True))


def get_2ch_post(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    print(current_time, ">", "/2ch", ">", update.message.from_user.username)
    board = 'b'
    if args:
        board = args[0]
    threads_response = requests.get('https://2ch.hk/{}/threads.json'.format(board))
    if not threads_response.ok:
        update.message.reply_text('Доска недоступна!')
        return
    top_thread_num = threads_response.json()['threads'][0]['num']
    top_thread_response = requests.get(
        'https://2ch.hk/{}/res/{}.json'.format(board, top_thread_num)
    )
    posts_list = top_thread_response.json()['threads'][0]['posts']
    post = random.choice(posts_list)
    files = post['files']
    comment_text = html2text(post['comment'])
    links = map(lambda file: "[file](https://2ch.hk{})".format(file['path']), files)
    message_text = '{}\n\n{}'.format(' '.join(links), comment_text)
    update.message.reply_text(message_text, parse_mode='Markdown')
    log_command(bot, update, current_time, "2ch")
