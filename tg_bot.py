#!/usr/bin/python
# -*- coding: utf-8 -*-
# v 1.31

import telebot
from telebot import apihelper
import sqlite3
import logging

from time import sleep

import os
import sys

# sys.path.append("../dataset_for_poem_TG_bot_python")
# sys.path.append("dataset_for_poem_TG_bot_python")
import db
from config import Config


COMMANDS = Config.commands
AMD_COMMANDS = Config.admin_commands
TG_PROXY_URL = Config.TG_PROXY_URL
TG_TOKEN = Config.TG_TOKEN
TG_ADMIN_ID = Config.TG_ADMIN_ID

apihelper.proxy = {'https': TG_PROXY_URL}
bot = telebot.TeleBot(TG_TOKEN)


LOG_DIR = Config.LOG_DIR
LOG_FILE = Config.LOG_FILE
LOG_FORMAT = Config.LOG_FORMAT
LOG_STR_USR = u'пользователь: [{}]'
LOG_STR_USR_DO = LOG_STR_USR + ', выполнил: {} - {}'
LOG_STR_ADM_DO = u'администратор: [{}], выполнил: {} - {}'

if not os.path.exists(LOG_DIR):
    # создание каталога и файла для логирования
    os.makedirs(LOG_DIR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter(LOG_FORMAT)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(fh)


def auth(func):
    """обертка, проверка авторизации пользователей"""
    def wrapper(message):
        user_id = message.chat.id
        if db.f_user_in_table(user_id):
            return func(message)
        else:
            bot.send_message(user_id, f'{message.chat.first_name}, У вас нет доступа.\n' +
                'Введите команду /start для начала работы')
            return False
    return wrapper


def is_admin(func):
    """обертка, проверка является ли пользователь администратором"""
    def wrapper_f(message):
        user_id = message.chat.id
        if user_id in TG_ADMIN_ID:
            return func(message)
        else:
            log_msg = LOG_STR_USR, u', пытается выполнить комманты администраторов'
            logger.info(log_msg.format(user_id))
            bot.send_message(user_id, f'{message.chat.first_name}, У вас нет доступа')
            return False
    return wrapper_f


# --start comand-- #
@bot.message_handler(commands=['start'])
def welcome(message):
    """обработка команды /start"""
    user_id = message.chat.id
    if not db.f_user_in_table(user_id):
        log_msg = LOG_STR_USR + u', запросил регистрацию'
        logger.info(log_msg.format(user_id))
        db.f_reg_user(user_id)
        bot.send_message(user_id, "Привет, как дела?\nСписок доступных команд /help")
    else:
        logger.info(LOG_STR_USR_DO.format(user_id, '/start', commands['start']))
        bot.send_message(user_id, "Привет, еще раз!")


# --help comand-- #
@bot.message_handler(commands=['help'])
@auth
def command_help(message):
    """обработка команды /help"""
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/help', COMMANDS['help']))
    help_text = "Доступны следующие команды: \n"
    for key in COMMANDS:  # generate help text out of the COMMANDS dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += COMMANDS[key] + "\n"
    bot.send_message(user_id, help_text)  # send the generated help page


# --random command-- #
@bot.message_handler(commands=['random'])
@auth
def command_random(message):
    """обработка команды /random"""
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/random', commands['random']))
    r_poem = db.f_get_poem()
    author = r_poem[2]
    title = r_poem[3]
    poem = title.center(40, '_') + '\n\n' + r_poem[4] + '\n' + author.rjust(40, '\x20')
    db.f_update_read_user(user_id, r_poem[0], author)
    bot.send_message(user_id, poem)
    

# --next command-- #
@bot.message_handler(commands=['next'])
@auth
def command_next(message):
    """обработка команды /next"""
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/next', COMMANDS['next']))
    n_poem = db.f_get_next(user_id)
    author = n_poem[2]
    title = n_poem[3]
    poem = title.center(40, '_') + '\n\n' + n_poem[4] + '\n' + author.rjust(40, '\x20')
    db.f_update_read_user(user_id, n_poem[0], author)
    bot.send_message(user_id, poem)


# --book command-- #
@bot.message_handler(commands=['book'])
@auth
def command_book(message):
    """
    обработка команды /book
    информация о стихотворениях в базе
    """
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/book', COMMANDS['book']))
    ib_text = db.f_info_about_book(user_id)
    bot.send_message(user_id, ib_text)


# --info command-- #
@bot.message_handler(commands=['info'])
@auth
def command_info(message):
    """
    обработка команды /info
    сколько получил пользователь стихотворений от бота
    """
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/info', COMMANDS['info']))
    inf_text = db.f_info_about_u_read(user_id)
    bot.send_message(user_id, inf_text)


# --restart command-- #
@bot.message_handler(commands=['restart'])
@auth
def command_restart(message):
    """
    обработка команды /restart
    сброс просмотров пользователя
    """
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/restart', COMMANDS['restart']))
    db.f_delete_user('usersreceived', user_id)
    bot.send_message(user_id, f'{message.chat.first_name}, ваши просмоты сброшены')


# --author command-- #
@bot.message_handler(commands=['author'])  # TODO
@auth
def command_author(message):
    """
    обработка команды /author
    выборка по автору
    """
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/author', COMMANDS['author']))
    bot.send_message(user_id, 'команда author пока в разработке')


# --reset command-- #
@bot.message_handler(commands=['reset_author'])  # TODO
@auth
def command_reset(message):
    """
    обработка команды /reset_author 
    сброс выбранного автора
    """
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/reset_author', COMMANDS['reset_author']))
    bot.send_message(user_id, 'команда reset пока в разработке')


# --end command-- #
@bot.message_handler(commands=['end'])
@auth
def command_end(message):
    """
    обработка команды /end
    удаление пользователя из бд
    """
    user_id = message.chat.id
    logger.info(LOG_STR_USR_DO.format(user_id, '/reset_author', COMMANDS['reset_author']))
    db.f_delete_user('usersreceived', user_id)
    db.f_delete_user('users', user_id)
    bot.send_message(user_id, 'Прощай, я буду скучать')


# --admin help comand-- #
@bot.message_handler(commands=['adminhelp'])
@is_admin
def admin_command_help(message):
    """обработка команды /adminhelp"""
    admin_id = message.chat.id
    logger.info(LOG_STR_ADM_DO.format(admin_id, '/adminhelp', AMD_COMMANDS['adminhelp']))
    help_text = "Доступны следующие команды: \n"
    for key in AMD_COMMANDS:  # generate help text out of the COMMANDS dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += AMD_COMMANDS[key] + "\n"
    bot.send_message(admin_id, help_text)  # send the generated help page


# --admin stat users command-- #
@bot.message_handler(commands=["statu"])
@auth
@is_admin
def admin_command_user_stat(message):
    """
    обработка команды /statu
    получение количества активных пользователей
    """
    admin_id = message.chat.id
    logger.info(LOG_STR_ADM_DO.format(admin_id, '/statu', AMD_COMMANDS['statu']))
    all_user = db.f_select_all_db('users')
    bot.send_message(admin_id, f'Всего активных пользователей: {len(all_user)}')


# --admin recreate users table-- #
@bot.message_handler(commands=["dcu"])
@auth
@is_admin
def admin_recreate_users_table(message):
    """
    обработка команды /dcu
    удаление и создание таблицы с пользователями
    """
    admin_id = message.chat.id
    logger.info(LOG_STR_ADM_DO.format(admin_id, '/dcu', AMD_COMMANDS['dcu']))
    db.f_clear_user_table_db()
    bot.send_message(admin_id, 'таблица пользователей удалена и создана')


# --admin recreate users received table-- #
@bot.message_handler(commands=["dcru"])
@auth
@is_admin
def admin_recreate_users_table(message):
    """
    обработка команды /dcru
    удаление и создание таблицы с просмотрами стихотворений
    """
    admin_id = message.chat.id
    logger.info(LOG_STR_ADM_DO.format(admin_id, '/dcru', AMD_COMMANDS['dcru']))
    db.f_clear_userreceived_table_db()
    bot.send_message(admin_id, 'таблица просмотров удалена и создана')


# --admin check new poem in directory-- #
@bot.message_handler(commands=["checkpoem"])  #TODO
@auth
@is_admin
def admin_recreate_users_table(message):
    """обработка команды /checkpoem """
    admin_id = message.chat.id
    logger.info(LOG_STR_ADM_DO.format(admin_id, '/checkpoem', AMD_COMMANDS['checkpoem']))
    cnt_new_poem = db.check_new_poem_in_dir(admin_id=admin_id)
    bot.send_message(admin_id, 'Новых стихотворений не найдено' if not cnt_new_poem else
        'Добавлено {} новых стихотворений'.format(cnt_new_poem))


# --any text message-- #
@bot.message_handler(content_types=["text"])
@auth
def send_text(message):
    """обработка сообщений от пользователей"""
    log_msg = LOG_STR_USR + u', написал: [{}]'
    logger.info(log_msg.format(message.chat.id, message.text))
    if message.text.lower() in ('привет', 'хай', 'даров', 'прив'):
        bot.send_message(message.chat.id, f'Приветствую тебя, {message.chat.first_name}!')
    elif message.text.lower() in ('пока', 'б', 'бай', 'поки', 'до завтра'):
        bot.send_message(message.chat.id, f'Пока, {message.chat.first_name}, заходи еще')
    else:
        bot.send_message(message.chat.id, 'Такой команды я не знаю =(.\n' +
                         'Посмотрите список всех команд "/help"')


if __name__ == '__main__':
    try:
        logger.info('запуск бота')
        bot.polling(timeout=30, none_stop=True)
        sleep(20)
        logger.warning('запуск бота, попытка 2')
        bot.polling(none_stop=True)
    except Exception as e:
        logger.critical(e.args)
        sleep(15)
        logger.warning('запуск бота, попытка 3')
        bot.polling(timeout=30)
