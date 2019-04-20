from telegram.ext import CommandHandler
from modules.logging import logging_decorator
from telegram import ChatAction
from datetime import datetime
from gtts import gTTS
import os


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, tts, pass_args=True))


@logging_decorator('say')
def tts(bot, update, args):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    reply = update.message.reply_to_message
    lang = 'ru'
    if reply is None:
        text = " ".join(args)
    elif reply.text is not None:
        text = reply.text
        if args:
            lang = args[0]
        elif text.startswith('-'):
            splited = text.split(maxsplit=2)
            if len(splited)==2:
                lang = splited[0][1:]
                text = splited[1]
    else:
        return
    if len(text) == 0:
        update.message.reply_text("Type in some text ^^")
        return
    if text.startswith('-'):
        splited = text.split(maxsplit=2)
        if len(splited)==2:
            lang = splited[0][1:]
            text = splited[1]
    update.message.chat.send_action(ChatAction.RECORD_AUDIO)
    tts = gTTS(text, lang)
    tts.save(path + filename + ".mp3")
    with open(path + filename + ".mp3", "rb") as f:
        linelist = list(f)
        linecount = len(linelist)
    if linecount == 1:  # wtf
        update.message.chat.send_action(ChatAction.RECORD_AUDIO)
        lang = "ru"
        tts = gTTS(text, lang)
        tts.save(path + filename + ".mp3")
    with open(path + filename + ".mp3", "rb") as speech:
        update.message.reply_voice(speech, quote=False)
    os.remove(path+filename+".mp3")
