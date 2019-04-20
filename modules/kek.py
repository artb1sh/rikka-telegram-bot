#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image
from telegram.ext import CommandHandler, MessageHandler
from modules.logging import log_command
from telegram import ChatAction
from datetime import datetime
import subprocess
import os
from PIL import Image, ImageOps


def module_init(gd):
    global path, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), kek))
        gd.dp.add_handler(CommandHandler(command, kek))


# get image, pass parameter
def kek(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    if update.message.reply_to_message is not None:
        kek_param = "".join(update.message.text[5:7])
    elif update.message.caption is not None:
        kek_param = "".join(update.message.caption[5:7])
    else:
        update.message.reply_text("You need an image for that!")
        return
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return False
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    result = kekify(update, kek_param, filename, extension)
    send_image(update, path, result, extension)
    os.remove(path+result+extension)
    os.remove(path+filename+extension)
    print(current_time, ">", "/kek", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "kek")


# kek process + send
def kekify(update, kek_param, basename, extension):
    if kek_param == "-m":
        result = multikek(update, basename, extension)
        return result
    filename = os.path.join(path, basename+extension)
    img = Image.open(filename)
    width, height = img.size
    if kek_param in ['-l', '']:
        half = img.crop((0, 0, width//2, height))
        mirrored_copy = ImageOps.mirror(half)
        result = horizontal_concat(half, mirrored_copy)
    elif kek_param == '-r':
        half = img.crop((width//2, 0, width, height))
        mirrored_copy = ImageOps.mirror(half)
        result = horizontal_concat(mirrored_copy, half)
    elif kek_param == '-t':
        half = img.crop((0, 0, width, height//2))
        mirrored_copy = ImageOps.flip(half)
        result = vertical_concat(half, mirrored_copy)
    elif kek_param == '-b':
        half = img.crop((0, height//2, width, height))
        mirrored_copy = ImageOps.flip(half)
        result = vertical_concat(mirrored_copy, half)
    else:
        update.message.reply_text(
            "Unknown kek parameter.\nUse -l, -r, -t, -b or -m")
        return
    result_basename = 'file_to_send'
    result_filepath = os.path.join(path, result_basename + extension)
    result.save(result_filepath)
    return result_basename


def multikek(update, filename, extension):
    kekify(update, "-l", filename, extension)
    kekify(update, "-r", filename, extension)
    kekify(update, "-t", filename, extension)
    kekify(update, "-b", filename, extension)
    append_lr = "convert " + path + filename+ "-kek-left" + extension + " " + path + filename + "-kek-right" + extension + " +append " + path +  filename + "-kek-lr-temp" + extension
    subprocess.run(append_lr, shell=True)
    append_tb = "convert " + path + filename + "-kek-top" + extension + " " + path + filename + "-kek-bot" + extension + " +append " + path + filename + "-kek-tb-temp" + extension
    subprocess.run(append_tb, shell=True)
    append_all = "convert " + path + filename + "-kek-lr-temp" + extension + " " + path + filename + "-kek-tb-temp" + extension + " -append " + path + filename + "-multikek" + extension
    subprocess.run(append_all, shell=True)
    result = filename + "-multikek"
    os.remove(path+filename+"-kek-left"+extension)
    os.remove(path+filename+"-kek-right"+extension)
    os.remove(path+filename+"-kek-top"+extension)
    os.remove(path+filename+"-kek-bot"+extension)
    os.remove(path+filename+"-kek-lr-temp"+extension)
    os.remove(path+filename+"-kek-tb-temp"+extension)
    return result


def vertical_concat(top, bottom):
    top_width, top_height = top.size
    bottom_width, bottom_height = bottom.size
    if top_width == bottom_width:
        width = bottom_width
    else:
        raise ValueError()
    result_size = (width, top_height+bottom_height)
    if top.mode == bottom.mode:
        mode = top.mode
    else:
        raise ValueError()
    result = Image.new(mode, result_size)
    result.paste(top, (0, 0))
    result.paste(bottom, (0, top_height))
    return result


def horizontal_concat(left, right):
    left_width, left_height = left.size
    right_width, right_height = right.size
    if left_height == right_height:
        height = left_height
    else:
        raise ValueError()
    result_size = (left_width+right_width, height)
    if left.mode == right.mode:
        mode = left.mode
    else:
        raise ValueError()
    result = Image.new(mode, result_size)
    result.paste(left, (0, 0))
    result.paste(right, (left_width, 0))
    return result
