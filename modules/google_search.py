from azure.cognitiveservices.search.imagesearch import ImageSearchAPI
from msrest.authentication import CognitiveServicesCredentials
from modules.logging import log_command
from telegram import ChatAction
from telegram.ext import CommandHandler
import requests
import random
from datetime import datetime


def module_init(gd):
    global subscription_key, safe_search, search_depth
    commands = gd.config["commands"]
    subscription_key = gd.config['subscription_key']
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, google_search, pass_args=True))


def google_search(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = ' '.join(args)
    if not query:
        update.message.reply_text("You need a query to search!")
        return
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
    print(current_time, ">", "/g", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "g")


def get_image(query):
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
    values = search_results['webPages']['value']
    link = values[0]['url']
    return link

