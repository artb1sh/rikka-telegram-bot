from modules.logging import logging_decorator
from .utils import convert_2ch_post_to_telegram
from telegram.ext import CommandHandler
import requests
import random


def module_init(gd):
    global default_board, cookies
    cookies = gd.config.get('cookies')
    default_board = gd.config['default_board']
    commands = gd.config['commands']
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, get_2ch_post, pass_args=True))


@logging_decorator('2ch')
def get_2ch_post(bot, update, args):
    board = args[0] if args else default_board
    threads_response = requests.get(
        'https://2ch.hk/{}/threads.json'.format(board),
        cookies=cookies,
    )
    if not threads_response.ok:
        update.message.reply_text('Доска недоступна!')
        return
    top_thread_num = threads_response.json()['threads'][0]['num']
    top_thread_response = requests.get(
        'https://2ch.hk/{}/res/{}.json'.format(board, top_thread_num),
        cookies=cookies,
    )
    posts_list = top_thread_response.json()['threads'][0]['posts']
    post = random.choice(posts_list)
    thread_link = 'https://2ch.hk/{}/res/{}.html'.format(board, top_thread_num)
    message_text = convert_2ch_post_to_telegram(post, thread_link=thread_link)
    has_files = message_text.startswith('[file](')
    update.message.reply_text(
        message_text,
        parse_mode='Markdown',
        disable_web_page_preview=(not has_files),
    )


@logging_decorator('2ch')
def send_2ch_post(bot, update, args):
    post_text = None