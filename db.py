#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os
from random import randint

# create db
import create_db

# read txt book
import read_txt


def f_select_all_db():
    # выборка из базы, возвращает кортеж из всех записей
    sql = """SELECT * from poems"""
    cursor.execute(sql)
    records = cursor.fetchall()
    con.commit()

    return records


def f_insert_db(data):
    for line in data:
        # --извлечение отделного элемента из списка и создание списка элементов в базе данных--#
        stih = line[3]
        db_stih_list = [row[4] for row in f_select_all_db()]
        # --если такой записи нет дабавляем всю линию--#
        if stih not in db_stih_list:
            cursor.execute("""INSERT INTO poems (book, author, title_stih, stih, date_stih) 
                            VALUES (?,?,?,?,?)""", (line[0], line[1], line[2], line[3], line[4])
                           )
            print('данные добавлены')
        else:
            print('данные уже существуют в базе')


def f_select_random_poem() -> object:
    # get random poem
    db = f_select_all_db()
    db_poem = [row[4] for row in db]
    r = randint(0, len(db_poem))

    return db_poem[r]


def f_delete_table_db():
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


def f_update_db():
    #
    pass


# --чтение txt файлов в папке--#
d = read_txt.dataset

# --подключение к базеданных--#
con = sqlite3.connect(create_db.file_db, check_same_thread=False)

# --работа с базой данных--#
with con:
    cursor = con.cursor()

    if d:
        f_insert_db(d)
    # ---delete and create db--- #
    # f_delete_table_db()
    con.commit()

'''
    db_list = f_select_all_db()
    db_author_list = [row[1] for row in db_list]
    for row in db_list:
        print(row[3], end='\n')
'''
