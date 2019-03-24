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
    safe_search = gd.config['safe_search']
    search_depth = gd.config['search_depth']
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, gelbooru_search, pass_args=True))


def gelbooru_search(bot, update, args):
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
    print(current_time, ">", "/img", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "img")


def get_image(query):
    client = ImageSearchAPI(CognitiveServicesCredentials(subscription_key))
    image_results = client.images.search(query=query, safe_search=safe_search)
    if not image_results.value:
        return None
    result = random.choice(image_results.value[:search_depth])
    link = result.content_url
    return link

