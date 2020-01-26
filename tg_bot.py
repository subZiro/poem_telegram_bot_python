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
    'next': 'Получить следующее стихотворение',
    'book': 'Получить информацию о хранимых ситхотворениях',
    'info': 'Получить статистику по прочитанным стихотворениям',
    'restart': 'Сброс всей статистии',
    'end': 'Удаление бота, завершение работы с ботом',
    # 'author': 'Выбрать автора',
    # 'reset': 'Сброс выборки по авторам'
}


def auth(func):
    def wrapper(message):
        user = message.chat.id
        if db.f_user_in_table(user):
            return func(message)
        else:
            bot.send_message(user, f'{message.chat.first_name}, У вас нет доступа.\n' +
                'Введите команду /start для начала работы')
            return False
    return wrapper


# --start comand-- #
@bot.message_handler(commands=['start'])
def welcome(message):
    user = message.chat.id
    if not db.f_user_in_table(user):
        db.f_reg_user(user)
        bot.send_message(user, "Привет, как дела?\nСписок доступных команд /help")
    else:
        bot.send_message(user, "Привет, еще раз!")


# --help comand-- #
@bot.message_handler(commands=['help'])
@auth
def command_help(message):
    user_id = message.chat.id
    help_text = "Доступны следующие команды: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(user_id, help_text)  # send the generated help page


# --random command-- #
@bot.message_handler(commands=['random'])
@auth
def command_random(message):
    user = message.chat.id
    r_poem = db.f_get_poem()
    author = r_poem[2]
    title = r_poem[3]
    poem = title.center(40, '_') + '\n\n' + r_poem[4] + '\n' + author.rjust(40, '\x20')
    db.f_update_read_user(user, r_poem[0], author)
    bot.send_message(user, poem)


# --author command-- #
@bot.message_handler(commands=['author'])
@auth
def command_author(message):
    # выборка по автору
    user = message.chat.id
    bot.send_message(user, 'команда author пока в разработке')


# --next command-- #
@bot.message_handler(commands=['next'])
@auth
def command_next(message):
    user = message.chat.id
    n_poem = db.f_get_next(user)
    author = n_poem[2]
    title = n_poem[3]
    poem = title.center(40, '_') + '\n\n' + n_poem[4] + '\n' + author.rjust(40, '\x20')
    db.f_update_read_user(user, n_poem[0], author)
    bot.send_message(user, poem)


# --book command-- #
@bot.message_handler(commands=['book'])
@auth
def command_book(message):
    # информация о стихотворениях в базе
    user = message.chat.id
    ib_text = db.f_info_about_book(user)
    bot.send_message(user, ib_text)


# --info command-- #
@bot.message_handler(commands=['info'])
@auth
def command_info(message):
    # сколько получил пользователь стихотворений от бота
    user = message.chat.id
    inf_text = db.f_info_about_u_read(user)
    if not inf_text:
        inf_text = 'Ваш список просмотров пуст'
    bot.send_message(user, inf_text)


# --restart command-- #
@bot.message_handler(commands=['restart'])
@auth
def command_restart(message):
    # сброс просмотров
    user = message.chat.id
    db.f_delete_user(user)
    db.f_reg_user(user)
    bot.send_message(user, f'{message.chat.first_name}, ваши просмоты сброшены')


# --reset command-- #
@bot.message_handler(commands=['reset'])
@auth
def command_reset(message):
    # сброс выбранного автора
    user = message.chat.id
    bot.send_message(user, 'команда reset пока в разработке')


# --end command-- #
@bot.message_handler(commands=['end'])
@auth
def command_end(message):
    # удаление пользователя из бд
    user = message.chat.id
    db.f_delete_user(user)
    bot.send_message(user, 'Прощай, я буду скучать')


# --any text message-- #
@bot.message_handler(content_types=["text"])
@auth
def send_text(message):
    # --обработка других сообщений-- #
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Приветствую тебя, {message.chat.first_name}!')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, f'Пока, {message.chat.first_name}, заходи еще')
    else:
        bot.send_message(message.chat.id, 'Такой команды я не знаю =(.\n' +
                         'Посмотрите список всех команд "/help"')


if __name__ == '__main__':
    try:
        print('start_bot')
        bot.polling(timeout=30, none_stop=True)
        sleep(20)
        print('start_bot_2')
        bot.polling(none_stop=True)
    except Exception as e:
        print(e.args)
        sleep(15)
        print('start_bot_3')
        bot.polling(timeout=30)
