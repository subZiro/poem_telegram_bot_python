#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
import logging

from random import randint
from datetime import datetime

# create db
import create_db

# read txt book
import read_txt


logging.basicConfig(
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', 
    level = logging.INFO)


def f_db_table():
    """
    получение списка всех таблиц бд

    :return список таблиц бд: list
    """
    sql = """
        SELECT name FROM sqlite_master 
        WHERE type='table'
        ORDER BY name;"""
    cursor.execute(sql)
    records = cursor.fetchall()
    result = [str(elem)[2:-3] for elem in records]
    return result


def f_user_in_table(user_id):
    """
    регистрация пользователя при нажитии на кнопку start

    :param user_id: id пользователя: int
    :return flg: результат проверки зареган ли пользователь:bool
    """
    flg = False
    user_table = f_select_all_db('users')
    # user_id_table = [elem[1] for elem in user_table]
    if user_id in [elem[1] for elem in user_table]:
        flg = True
    return flg
        

def f_reg_user(user_id:int):
    """
    внесение нового пользователя в таблицу

    :param user_id: id пользователя: int
    """
    sql = """
        INSERT INTO users 
        VALUES (?, ?);"""
    cursor.execute(sql, (None, user_id))
    conn.commit()
    logging.info('пользователь зарегистрирован!')


def f_select_all_db(name_table):
    """
    выборка из базы, возвращает список из всех записей из таблицы name_table
    
    :param name_table: название таблицы: str
    :return records: список записей из таблицы: list
    """
    if name_table not in f_db_table():
        logging.warning('такой таблицы не существуют')
        return False
    else:
        sql = f"""SELECT * FROM {name_table};"""
        cursor.execute(sql)
        records = cursor.fetchall()
        conn.commit()
        logging.info('список всех записей таблицы {} получен'.format(name_table))
        return records


def f_get_poem(index=None):  # TODO изменить логику выборки одной записи
    """
    получение стихотворения, если индекс не передан то возвращается случайное стихотворение

    :param index: номер стихотворения: int
    :return: одну строку таблицы poems: list
    """
    db = f_select_all_db('poems')
    if not index:
        index = randint(1, len(db))
    logging.info('стихотворение получено')
    return db[index-1]


def f_get_next(user_id):
    """
    запрос следующего стихотворениея
    получение индекса крайнего прочитанного сообщения и отправка следующего

    :param user_id: id пользователя: int
    :return: одну строку таблицы poems: list
    """
    poem_list = f_select_read(user_id)
    if not poem_list[-1]:
        logging.info('получено первое стихотворение, тк ранее небыло прочитанных стихотворений')
        return f_get_poem(1)
    logging.info('получено следующее стихотворение')
    return f_get_poem(int(poem_list[-1][0]) + 1)
   
    
def f_select_read(user_id):
    """
    получение полученых стихотворений по пользователю

    :param user_id: id пользователя: int    
    :return r: все записи по пользователю: list
    """
    sql = f"""
        SELECT received_poem_id, received_author, received_date
        FROM usersreceived
        WHERE user_id == {user_id}"""
    cursor.execute(sql)
    r = cursor.fetchall()
    conn.commit()
    logging.info('получен список прочитанных стихотворений')
    return r


def f_select_poem_by_author():  # TODO
    """
    получение стихотворений выбранного автора

    :param args: tuple:
    :return kwargs: dict:
    """
    pass


def f_insert_db(data):
    """
    вставка новых данных

    :param data: список стихотворений: list
    """
    k = j = 0
    for line in data:
        # --извлечение отделного элемента из списка и создание списка элементов в базе данных--#
        stih = line[3]
        db_stih_list = [row[4] for row in f_select_all_db('poems')]
        # --если такой записи нет дабавляем всю линию--#
        if stih not in db_stih_list:
            k += 1
            cursor.execute("""
                INSERT INTO poems (book, author, title_stih, stih, date_stih) 
                VALUES (?,?,?,?,?);""", 
                (line[0], line[1], line[2], line[3], line[4])
                )
        conn.commit()
    logging.info(u'[{}] новых стихотворений добавлены'.format(k))

       
def f_update_read_user(user_id, poem_id, author): 
    """
    обновление списка полученных стихотворений

    :param user_id: id пользователя: int
    :param poem_id: id стихотворния из бд: int
    :param author: имя автора стихотворения: str
    """
    sql = """
        INSERT INTO usersreceived (user_id, received_poem_id, received_author, received_date) 
        VALUES (?, ?, ?, ?);
        """
    dt_now = datetime.now().strftime('%Y-%M-%d %H:%M:%S')  
    cursor.execute(sql, (user_id, poem_id, author, dt_now))
    conn.commit()
    logging.info('стихотворение добавлено с список просмотренных')

    
def f_info_about_book(user_id):
    """
    получение информации о хранимых в бд стихотворениях и авторах

    :param user_id: id пользователя: int
    :return result_text: строку с информацие о базе: str
    """
    db = f_select_all_db('poems')
    author = [a[2] for a in db]
    author_set = list(set(author))
    # --форматирование строки вывода сообщения-- #
    result_text = f'В базе храниться {len(db)} стихотворений' + '\n'
    for i in range(len(author_set)):
        result_text += f'Из них {author.count(author_set[i])} авторства "{author_set[i]}"' + '\n'
    logging.info('получена информация об авторах')
    return result_text[:-1]


def f_info_about_u_read(user_id):
    """
    статистика о полученых пользователем стихотворений

    :param user_id: id пользователя: int
    :return result_text: строку с информацией о прочитаных пользоватых стихов: str
    """
    poems_list = f_select_read(user_id)
    if not poems_list:
        return 'Ваш список просмотров пуст'
    # --словарь по авторам-- #
    ap_dict = {}
    for x in poems_list:
        if x[1] not in ap_dict:
            ap_dict[x[1]] = 1
        else:
            ap_dict[x[1]] += 1
    # --форматирование строки вывода сообщения-- #
    result_text = f'Вы получили {len(poems_list)} стихотворений' + '\n'
    for k, v in ap_dict.items():
        result_text += f'Из них {k} написал {v}' + '\n'
    logging.info('получена информация о просмотрах')
    return result_text[:-1]

    
def f_delete_user(tablename, user_id):
    """
    удаление пользователя из базы

    :param tablename: название таблицы: str
    :param user_id: id пользователя: int
    """
    sql = f"""DELETE FROM {tablename} WHERE user_id == {user_id};"""
    cursor.execute(sql)
    conn.commit()
    s = 'удален' if tablename == 'users' else 'сбросил статистику просмотров'
    logging.info(u'пользователь-[{}], {}'.format(user_id, s))
    

def f_clear_poem_table_db():
    """
    detele and create new table
    """
    cursor.executescript("""
        DROP TABLE IF EXISTS poems;
        CREATE TABLE poems
                (poem_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                book text, 
                author text, 
                title_stih text, 
                stih text, 
                date_stih text);"""
        )
    conn.commit()
    logging.info('таблица со стихотворениями пересоздана')


def f_clear_user_table_db():
    """
    detele and create new table
    """
    cursor.executescript("""
        DROP TABLE IF EXISTS users;
        CREATE TABLE users(
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id int);"""
        )
    conn.commit()
    logging.info('таблица пользователей пересоздана')

def f_clear_userreceived_table_db():
    """
    detele and create new table
    """
    cursor.executescript("""
        DROP TABLE IF EXISTS usersreceived;
        CREATE TABLE usersreceived(
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id int,
            received_poem_id int,
            received_author text,
            received_date timestamp);"""
        )
    conn.commit()
    print('таблица просмотров стихотворений пересоздана')


def check_new_poem_in_dir(admin_id):
    """
    проверка и добавление новых стихотворений в каталоге
    """
    # --чтение txt файлов в папке--#
    d = read_txt.dataset
    if d:
        # --подключение к базеданных--#
        conn = sqlite3.connect(create_db.file_db, check_same_thread=False)
        with conn:
            cursor = conn.cursor()
            f_insert_db(d)
            conn.commit()
    else:
        logging.info('новых стихотворений не найдено')
 

if __name__ == '__main__':
    print('(-_-)')
else:
    conn = sqlite3.connect(create_db.file_db, check_same_thread=False)
    with conn:
        cursor = conn.cursor()
        conn.commit()

