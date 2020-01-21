#!/usr/bin/python
# -*- coding: utf-8 -*-
import telebot
from telebot import apihelper
import sqlite3

from time import sleep

import os
import sys

# sys.path.append("../dataset_for_poem_TG_bot_python")
# sys.path.append("dataset_for_poem_TG_bot_python")
import db
from config import TG_TOKEN, TG_PROXY_URL, TG_ADMIN_ID

apihelper.proxy = {'https': TG_PROXY_URL}
bot = telebot.TeleBot(TG_TOKEN)

# --commands for user--#
commands = {  # command description used in the "help" command
    'start': 'Начало использования бота',
    'help': 'Информация о доступных командах',
    'random': 'Получить случайное стихотворение',
    'author': 'Выбрать автора',
    'next': 'Получить следующее стихотворение',
    'book': 'Получить информацию о хранимых ситхотворениях',
    'info': 'Получить информацию о хранимых стихотворениях',
    'restart': 'Сброс всей статистии'
}


def auth(func):
    # на удаление
    def wrapper(message):
        if message.chat.id == TG_ADMIN_ID:
            return func(message)
        else:
            bot.send_message(message.chat.id, 'У вас нет доступа')
            return False

    return wrapper


# --start comand-- #
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Привет, отправь мне что-нибудь")
    user_id = message.chat.id


# --help comand-- #
@bot.message_handler(commands=['help'])
def command_help(message):
    user_id = message.chat.id
    help_text = "Доступны следующие команды: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(user_id, help_text)  # send the generated help page


# --random command-- #
@bot.message_handler(commands=['random'])
def command_random(message):
    user_id = message.chat.id
    d1 = db.f_select_random_poem()
    bot.send_message(user_id, d1)  # show the keyboard


# --author command-- #
@bot.message_handler(command=['author'])
def command_author(message):
    #
    pass


# --next command--#
@bot.message_handler(command=['next'])
def command_author(message):
    #
    pass


# --book command-- #
@bot.message_handler(command=['book'])
def command_author(message):
    #
    pass


# --info command-- #
@bot.message_handler(command=['info'])
def command_author(message):
    #
    pass


# --restart command-- #
@bot.message_handler(command=['restart'])
def command_author(message):
    #
    pass


# --any text message-- #
@bot.message_handler(content_types=["text"])
def send_text(message):
    # ---- #
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Приветствую тебя, {message.chat.first_name}!')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, но ты заходи хоть иногда')
    else:
        bot.send_message(message.chat.id, 'Такой команды я не знаю =(.\n' +
                         'Посмотрите список всех команд "/help"')


if __name__ == '__main__':
    try:
        print('start_bot')
        bot.polling(timeout=30)
    except Exception as e:
        print(e.args)
        sleep(10)
        print('start_bot_2')
        bot.polling(timeout=30)
