from modules.logging import log_command
from modules.utils import convert_2ch_post_to_telegram
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async
import requests
import threading
import sqlite3
import time
from datetime import datetime
import re


class PostsObserver(threading.Thread):

    def __init__(self, bot, conn, interval=10):
        super().__init__()
        self.conn = conn
        self.bot = bot
        self.interval = interval

    def run(self):
        while True:
            updates = False
            for row in self.conn.execute('SELECT * FROM tracked').fetchall():
                api_url, last_post, chat_id = row
                api_response = requests.get(api_url)
                if api_response.status_code == 404:
                    query = 'DELETE FROM tracked WHERE api_url=?'
                    self.conn.execute(query, (api_url,))
                    self.conn.commit()
                    continue
                try:
                    posts = api_response.json()['threads'][0]['posts']
                    if posts[-1]['num'] <= last_post:
                        continue
                    updates = True
                    thread_url = api_url[:-4] + 'html'
                    new_posts = [post for post in posts if post['num'] > last_post]
                    for post in new_posts:
                        message_text = convert_2ch_post_to_telegram(
                            post,
                        )
                        self.bot.send_message(chat_id, message_text, parse_mode='Markdown')
                    last_post = posts[-1]['num']
                    query =  'UPDATE tracked SET last_post=? WHERE api_url=? and chat_id=?'
                    self.conn.execute(query, (last_post, api_url, chat_id))
                    self.conn.commit()
                except Exception as e:
                    continue
            if not updates:
                time.sleep(self.interval)


def module_init(gd):
    global c, conn, db_lock, dp
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
    observer = PostsObserver(dp.bot, conn)
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
        update.message.reply_text('Вы не администратор, чтобы указзывать мне!')
        return
    url = args[0]
    try:
        board = re.search(r'\w+(?=/res/)', url).group(0)
        thread_num = int(re.search(r'\w+(?=\.html$)', url).group(0))
        api_url = 'https://2ch.hk/{}/res/{}.json'.format(board, thread_num)
        response = requests.get(api_url, timeout=3)
        assert response.ok
    except:
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
