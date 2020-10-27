from azure.cognitiveservices.search.imagesearch import ImageSearchClient
from msrest.authentication import CognitiveServicesCredentials
from modules.logging import logging_decorator
from telegram import ChatAction
from telegram.ext import CommandHandler
import random


def module_init(gd):
    global subscription_key, safe_search, search_depth
    commands = gd.config["commands"]
    subscription_key = gd.config['subscription_key']
    safe_search = gd.config['safe_search']
    search_depth = gd.config['search_depth']
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, image_search, pass_args=True))


@logging_decorator('img')
def image_search(bot, update, args):
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


def get_image(query):
    client = ImageSearchClient(CognitiveServicesCredentials(subscription_key))
    image_results = client.images.search(query=query, safe_search=safe_search)
    if not image_results.value:
        return None
    result = random.choice(image_results.value[:search_depth])
    link = result.content_url
    return link

