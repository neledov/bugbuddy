#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import requests
from google import standard_search


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram



def gettitle(bugid):
    page = requests.get("https://quickview.cloudapps.cisco.com/quickview/bug/" + bugid)

    retitle = re.compile(r'<title>Cisco Bug: .{13}([\S\s]*?)</title>', re.MULTILINE)
    title = re.findall(retitle, page.text)
    # print title
    final = []
    if not title:
        final.insert(0, " - Oops! No information avaliable externally")
    else:
        final = list(filter(None, title))
        print final[0]
    print "gettitle"
    return final[0]


def fstr(sourcelist):
    return '\n'.join(str(p) for p in sourcelist)


def findingoogle(usertext):
    search = re.compile(r'(?=CSC[\S\s]).{10}', re.MULTILINE)
    a = standard_search.search("""Cisco Bug """ + usertext )
    print a
    answer = re.findall(search, fstr(a))
    if answer:
        ##answer.insert(0, "*Possible bugs for your request* : ")
        print answer
    else:
        answer.insert(0, "Nothing found, please be more exact")
    print "findingoogle"
    return answer[:10]


def getdescr(bugid):
    page = requests.get("https://quickview.cloudapps.cisco.com/quickview/bug/" + bugid)
    retitle = re.compile(r'<title>Cisco Bug: ([\S\s]*?)</title>', re.MULTILINE)
    resymptom = re.compile(r'<B>Symptom:</B>([\S\s]*?)<B>Conditions:</B>', re.MULTILINE)
    recondition = re.compile(r'<B>Conditions:</B>([\S\s]*?)</pre>', re.MULTILINE)
    symptom = re.findall(resymptom, page.text)
    condition = re.findall(recondition, page.text)
    title = re.findall(retitle, page.text)
    final = []
    if not symptom:
        final.insert(0, "No information avaliable")
    else:
        print "bug found " + bugid
        symptom.insert(0, "Title : " + title[0])
        symptom.insert(1, "Quickview URL : https://quickview.cloudapps.cisco.com/quickview/bug/" + bugid)
        symptom.insert(2,
                       "Symptoms of " + bugid + " :")

        condition.insert(0, "Condition :")
        result = symptom + condition
        final = list(filter(None, result))
        print "getdescr"
        print final
    return final

updater = Updater(token='545637489:AAHnsdp3vUEg_s71CK3RavN5e351Hm8VB0Q')  # Токен API к Telegram
dispatcher = updater.dispatcher


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Hello, I am bug bot, please enter bug id to get brief description or state symptom')


def textMessage(bot, update):
    if update.message.text.startswith("CSC"):
        bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        scrapper = fstr(getdescr(update.message.text))
        bot.send_message(chat_id=update.message.chat_id, text=scrapper)
    else:
        bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        a = findingoogle(update.message.text)
        a = list(dict.fromkeys(a))
        buttons = [telegram.KeyboardButton(s) for s in a]
        ##del a[0]
        my_new_list = [x + " : " + gettitle(x) for x in a]
        ##my_new_list.insert(0, "*Possible bugs for your request* :")
        my_new_list = fstr(my_new_list).encode("utf-8")
        reply_markup = telegram.ReplyKeyboardMarkup(build_menu(buttons, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id, text=my_new_list, parse_mode=telegram.ParseMode.MARKDOWN,
                         reply_markup=reply_markup)


start_command_handler = CommandHandler('start', startCommand)
text_message_handler = MessageHandler(Filters.text, textMessage)
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(text_message_handler)
updater.start_polling(clean=True)
updater.idle()

