from modules.logging import log_command
from modules.utils import convert_2ch_post_to_telegram
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async
import requests
import threading
import sqlite3
import time
import logging
import re


class PostsObserver(threading.Thread):

    def __init__(self, bot, conn, interval=10, logger=None):
        super().__init__()
        self.conn = conn
        self.bot = bot
        self.interval = interval
        self.logger = logger if logger is not None else logging.getLogger()

    def add_thread(self, url, chat_id, timeout=3):
        board = re.search(r'\w+(?=/res/)', url).group(0)
        thread_num = int(re.search(r'\w+(?=\.html$)', url).group(0))
        api_url = 'https://2ch.hk/{}/res/{}.json'.format(board, thread_num)
        response = requests.get(api_url, timeout=timeout)
        response.raise_for_status()
        last_post = response.json()['threads'][0]['posts'][-1]['num']
        self.conn.execute(
            "INSERT INTO tracked (api_url, last_post, chat_id) VALUES (?,?,?)",
            (api_url, last_post, chat_id))
        self.conn.commit()

    def delete_thread(self, api_url, chat_id):
        query = 'DELETE FROM tracked WHERE api_url=? and chat_id=?'
        self.conn.execute(query, (api_url, chat_id))
        self.conn.commit()

    def get_new_posts(self, api_url, last_post):
        api_response = requests.get(api_url)
        if api_response.status_code == 404:
            self.logger.info(
                '404 responce for thread {}'.format(api_url))
            query = 'DELETE FROM tracked WHERE api_url=?'
            self.conn.execute(query, (api_url,))
            self.conn.commit()
            return None
        posts = api_response.json()['threads'][0]['posts']
        new_posts = [post for post in posts if post['num'] > last_post]
        return new_posts

    def run(self):
        while True:
            try:
                updates = False
                rows = self.conn.execute('SELECT * FROM tracked').fetchall()
                for row in rows:
                    api_url, last_post, chat_id = row
                    thread_url = api_url[:-4] + 'html'
                    new_posts = self.get_new_posts(api_url, last_post)
                    if new_posts is None:
                        self.delete_thread(api_url, chat_id)
                        message_text = ('Тред {} был удален и больше'
                                        ' не отслеживается!')
                        self.bot.send_message(chat_id,
                                              message_text.format(thread_url))
                        continue
                    for post in new_posts:
                        message_text = convert_2ch_post_to_telegram(
                            post,
                            thread_link=thread_url,
                        )
                        try:
                            self.bot.send_message(chat_id, message_text, parse_mode='Markdown')
                        except Exception as e:
                            self.logger.error(
                                'Cannot send message:\n~~~\n{}\n~~~'.format(message_text),
                                exc_info=True)
                if not updates:
                    time.sleep(self.interval)
            except Exception as e:
                self.logger.error('Unhandled exception', exc_info=True)
                time.sleep(self.interval)


def module_init(gd):
    global c, conn, db_lock, dp, observer
    db_lock = threading.Lock()
    dp = gd.dp
    path = gd.config["path"]
    conn  = sqlite3.connect(path+"rikka.db", check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS tracked (api_url text, last_post integer, chat_id integer, UNIQUE (api_url, chat_id))')
    c = conn.cursor()
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(
            CommandHandler(command, track, pass_args=True))
    logger = logging.getLogger('track')
    logger.setLevel(logging.DEBUG)
    error_fh = logging.FileHandler('track.error.log')
    error_fh.setLevel(logging.ERROR)
    debug_fh = logging.FileHandler('track.debug.log')
    debug_fh.setLevel(logging.DEBUG)
    logger.addHandler(error_fh)
    logger.addHandler(debug_fh)
    observer = PostsObserver(dp.bot, conn, logger=logger)
    observer.start()


@run_async
def track(bot, update, args):
    chat_id = update.effective_message.chat_id
    user_id = update.effective_user.id
    if not args:
        query = 'SELECT api_url FROM tracked WHERE chat_id=?'
        json_urls = c.execute(query, (chat_id,)).fetchall()
        tracked_urls = map(lambda json_url: json_url[0][:-4]+'html', json_urls)
        message_text = 'Отслеживаемые треды:\n{}'.format('\n'.join(tracked_urls))
        update.message.reply_text(message_text)
        return
    if (update.effective_chat.type != 'private'
            and update.effective_chat.get_member(user_id).status not in ['administrator', 'creator']):
        update.message.reply_text('Вы не администратор, чтобы указывать мне!')
        return
    url = args[0]
    try:
        board = re.search(r'\w+(?=/res/)', url).group(0)
        thread_num = int(re.search(r'\w+(?=\.html$)', url).group(0))
        api_url = 'https://2ch.hk/{}/res/{}.json'.format(board, thread_num)
        response = requests.get(api_url)
        assert response.ok
    except Exception as e:
        update.message.reply_text('Тред не найден!')
        return
    last_post = response.json()['threads'][0]['posts'][-1]['num']
    try:
        c.execute("INSERT INTO tracked (api_url, last_post, chat_id) VALUES (?,?,?)", (api_url, last_post, chat_id))
        conn.commit()
        update.message.reply_text('Тред начал отслеживаться!')
    except sqlite3.IntegrityError as e:
        query = 'DELETE FROM tracked WHERE api_url=? and chat_id=?'
        c.execute(query, (api_url, chat_id))
        conn.commit()
        update.message.reply_text('Теперь тред не отслеживается!')
