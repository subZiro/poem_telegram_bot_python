#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
from random import randint

# create db
import create_db

# read txt book
import read_txt


def f_db_table():
    # получение списка всех таблиц бд
    
    sql = """SELECT name FROM sqlite_master 
        WHERE type='table'
        ORDER BY name;"""
    cursor.execute(sql)
    records = cursor.fetchall()
    result = [str(elem)[2:-3] for elem in records]
    return result


def f_user_in_table(user_id:int):
    # регистрация пользователя при нажитии на кнопку start
    flg = False
    user_table = f_select_all_db('users')
    user_id_table = [elem[0] for elem in user_table]
    if user_id in user_id_table:
        flg = True
    return flg
        

def f_reg_user(user_id:int):
    # внесение нового пользователя в таблицу
    sql = """INSERT INTO users VALUES (?, ?, ?)"""
    cursor.execute(sql, (user_id, '', ''))
    print(f'пользователь {user_id} - зарегистрирован')


def f_select_all_db(name_table):
    # выборка из базы, возвращает список из всех записей из таблицы name_table
    if name_table not in f_db_table():
        print('Такой таблицы не существуют')
        return False
    else:
        sql = f"""SELECT * FROM {name_table}"""
        cursor.execute(sql)
        records = cursor.fetchall()
        conn.commit()
        return records


def f_get_poem(index=None):
    # получение стихотворения, если инекс не передан то возвращается случайное стихотворение
    db = f_select_all_db('poems')
    if not index:
        index = randint(1, len(db))
    return db[index-1]


def f_get_next(user_id):
    # запрос следующего стихотворениея
    # получение индекса крайнего прочитанного сообщения и отправка следующего
    poem, author = f_select_read(user_id)
    poem = poem.split('*')
    author = author.split('*')
    print(f'пользователь {user_id} запросил следующее стихотворение')
    if not poem[0]:
        return f_get_poem(1)
    return f_get_poem(int(poem[-1]) + 1)
   
    
def f_select_read(user_id):
    # получение кортежа (str(poem_id), str(author)) стихотворений полученых пользователем
    sql = f"""SELECT received_poem_id, received_author 
                FROM users
                WHERE user_id == {user_id}"""
    cursor.execute(sql)
    r = cursor.fetchone()
    return r[0], r[1]


def f_select_poem_by_author():
    # получение стихотворений выбранного автора
    pass


def f_insert_db(data):
    # вставка новых данных
    k = 0
    for line in data:
        # --извлечение отделного элемента из списка и создание списка элементов в базе данных--#
        stih = line[3]
        db_stih_list = [row[4] for row in f_select_all_db('poems')]
        # --если такой записи нет дабавляем всю линию--#
        if stih not in db_stih_list:
            k += 1
            cursor.execute("""INSERT INTO poems (book, author, title_stih, stih, date_stih) 
                            VALUES (?,?,?,?,?)""", (line[0], line[1], line[2], line[3], line[4]))
    print('{} стихотворений добавлены'.format(k))

       
def f_update_read_user(user_id, p, a):
    # обновление списка полученных стихотворений
    poem, author = f_select_read(user_id)
    if poem:
        poem += '*' + str(p)
        author += '*' + a
    else:
        poem += str(p)
        author += a

    sql = """UPDATE users
            SET received_poem_id = ?, 
                received_author = ?
            WHERE user_id = ?"""
    cursor.execute(sql, (poem, author, user_id))
    print(f'пользователь {user_id} получил стихотворение {p}')

    
def f_info_about_book(user_id):
    # получение информации о хранимых в бд стихотворениях и авторах
    db = f_select_all_db('poems')
    author = [a[2] for a in db]
    author_set = list(set(author))
    # --форматирование строки вывода сообщения-- #
    result_text = f'В базе храниться {len(db)} стихотворений' + '\n'
    for i in range(len(author_set)):
        result_text += f'Из них {author.count(author_set[i])} авторства "{author_set[i]}"' + '\n'
    print(f'пользователь {user_id} запросил информацию по книге')
    return result_text[:-1]


def f_info_about_u_read(user_id):
    # статистика о полученых пользователем стихотворений
    print(f'пользователь {user_id} запросил статистику чтения')
    poem, author = f_select_read(user_id)
    if not poem:
        return False
    poem = poem.split('*')
    author = author.split('*')
    author_set = list(set(author))
    # --форматирование строки вывода сообщения-- #
    result_text = f'Вы получили {len(author)} стихотворений' + '\n'
    for i in range(len(author_set)):
        result_text += f'Из них {author.count(author_set[i])} написал {author_set[i]}' + '\n'

    return result_text[:-1]


def f_clear_poem_table_db():
    # detele and create new table
        cursor.executescript("""
            DROP TABLE IF EXISTS poems;
            CREATE TABLE poems
                    (poem_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    book text, 
                    author text, 
                    title_stih text, 
                    stih text, 
                    date_stih text);""")


def f_clear_user_table_db():
    # detele and create new table
        cursor.executescript("""
            DROP TABLE IF EXISTS users;
            CREATE TABLE users(
                user_id int,
                received_poem_id int,
                received_author text);""")


def f_delete_user(user_id:int):
    # удаление пользователя из базы
    sql = f"""DELETE FROM users WHERE user_id == {user_id}"""
    cursor.execute(sql)
    print('пользователь: {} - удален'.format(user_id))


# --чтение txt файлов в папке--#
d = read_txt.dataset
# --подключение к базеданных--#
conn = sqlite3.connect(create_db.file_db, check_same_thread=False)
# --работа с базой данных--#
with conn:
    cursor = conn.cursor()

    if d:
        f_insert_db(d)
    # ---delete and create db--- #
    # f_delete_table_db()
    conn.commit()
