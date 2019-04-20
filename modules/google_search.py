from modules.logging import logging_decorator
from telegram.ext import CommandHandler
import requests


def module_init(gd):
    global subscription_key
    commands = gd.config["commands"]
    subscription_key = gd.config['subscription_key']
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, web_search, pass_args=True))


@logging_decorator('g')
def web_search(bot, update, args):
    query = ' '.join(args)
    if not query:
        update.message.reply_text("You need a query to search!")
        return
    try:
        result_link = get_first_result(query)
    except:
        update.message.reply_text("Sorry, случилась какая-то жопа!")
        return
    if result_link is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[link]({})".format(result_link)
    update.message.reply_text(msg_text, parse_mode="Markdown")


def get_first_result(query):
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {
        "q": query,
        "textDecorations": False,
        "textFormat": "Raw",
    }
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    if 'webPages' not in search_results:
        return None
    values = search_results['webPages']['value']
    link = values[0]['url']
    return link
