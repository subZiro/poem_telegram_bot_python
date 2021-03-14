#!/usr/bin/python
# -*- coding: utf-8 -*-
# v 1.34

import sqlite3
import os
import logging

from random import randint
from datetime import datetime

from sqlalchemy import select, or_, func, and_
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from config import Config
from model import User, UserActive, Poem, Author, Book


DB_FILE = Config.DB_DIR + '/' + Config.DB_FILE

logging.basicConfig(
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', 
    level = logging.INFO)


def get_user(user_id: int):
    """
    Возвращает пользователя из бд если он зарегистрирован, иначае false

    <User object>

    :param user_id: id пользователя: int
    :return flg: результат проверки зареган ли пользователь:bool
    """
    user = session.query(User).filter_by(user_id=user_id).first()
    return user if user is not None else None


def add_user(user_id: int, name: str = None):
    """
    Регистрация пользователя при нажитии на кнопку start

    :param user_id: id пользователя: int
    :return flg: результат проверки зареган ли пользователь:bool
    """

    user = User()
    user.user_id = user_id
    user.name = name
    user.date_connected = datetime.now()
    session.add(user)
    session.commit()
    logging.info(f'пользователь [{user_id}] зарегистрирован!')


def get_count_poems():
    """
    Возвращает количество стихотворений в бд

    <1000>

    :return: количество записей в poems: int
    """

    return session.query(Poem).count()


def get_poem(index: int): 
    """
    получение стихотворения, по индексу

    <(13, 'ЛЕТНИЙ ВЕЧЕР', 'Последние лучи заката ...', '19**', 'Александр Блок', 'СТИХОТВОРЕНИЯ, ...'))>

    :param index: номер стихотворения: int
    :return: одну строку таблицы poems: list
    """

    poem = session.query(Poem.id, Poem.title, Poem.text, Poem.create_date, Author.fullname, Book.name) \
        .select_from(Poem) \
        .join(Author, and_(Author.id == Poem.author_id, Poem.id == index)) \
        .join(Book, Book.id == Poem.book_id) \
        .first()
    return poem if poem is not None else None


def get_random_poem():
    """
    Возвращает одно случайное стихотворение

    <Poem object>
    
    :return: одну случайную строку таблицы poems: list
    """
    # TODO не получать стихотворение которое уже есть в просмотрах
    return get_poem(index=randint(1, get_count_poems()))


def get_next_poem(user_id: int):
    """
    Возвращает следующее стихотворение
    получение индекса крайнего прочитанного сообщения и отправка следующего

    <Poem object>
    
    :param user_id: id пользователя: int
    :return get_poem(): одну строку таблицы poems: basequery object
    """
    # получение крайго просмотра
    next_ = 1
    last_active = get_last_active_user(user_id=user_id).first()

    # если последий просмотр был крайняя запись то возвращаем первую
    if last_active is not None:
        if last_active.poem_id != get_count_poems():
            next_ = last_active.poem_id + 1
    return get_poem(index=next_)


def get_last_active_user(user_id: int):
    """
    Получение информации о крайнем просмотреном стихотворении

    <UserActive object>

    :param user_id: id пользователя: int
    :return last_active: одну строку таблицы user_active: object
    """
    return session.query(UserActive) \
        .filter_by(user_id=user_id) \
        .order_by(UserActive.date_view.desc())
    


def set_author(author: str):  # TODO
    """
    получение стихотворений выбранного автора

    :param user_id: id пользователя: int
    :return kwargs: dict:
    """
    pass


def add_new_poem(new_poem: dict):  # TODO
    """
    Добавление нового стихотворения

    """
    pass


def add_poem_in_useractive(user_id: int , poem_id: int): 
    """
    обновление списка полученных стихотворений

    :param user_id: id пользователя: int
    :param poem_id: id стихотворния из бд: int
    """
    author = session.query(Poem.author_id).filter_by(id=poem_id).first()
    book = session.query(Poem.book_id).filter_by(id=poem_id).first()


    new_active = UserActive()
    new_active.user_id = user_id
    new_active.author_id = author[0] if author is not None else None
    new_active.poem_id = poem_id
    new_active.book_id = book[0] if book is not None else None
    new_active.date_view = datetime.now()

    session.add(new_active)
    session.commit()
    logging.info(f'стихотворение {poem_id}добавлено с список просмотренных к пользователю {user_id}')


def get_info_about_book(type_info: str):
    """
    получение информации о хранимых в бд книгах

    :param type_info: тип запрашиваемой информации: str
    :return Poem object: количество или все записи таблицы: int or str
    """
    if type_info == 'count':
        return session.query(Poem).count()
    elif type_info == 'all':
        return session.query(Poem).all()
    else:
        return None


def get_info_about_author(type_info: str):
    """
    получение информации о хранимых в бд авторов прозведений

    :param type_info: тип запрашиваемой информации: str
    :return Author object: количество или все записи таблицы: str
    """
    authors = session.query(Author)
    if type_info == 'count':
        return 'В базе хранится произведения {} авторов'.format(authors.count())
    elif type_info == 'all':
        return 'В нашей базе имеются произведения {} авторов, а именно: {}'.format(
            authors.count(), ', '.join([a.fullname for a in authors]))
    else:
        return None


def get_info_about_poem(type_info: str):
    """
    получение информации о хранимых в бд авторов прозведений

    :param type_info: тип запрашиваемой информации: str
    :return Author object: количество или все записи таблицы: int or str
    """
    query = session.query(Poem.id, Poem.title, Poem.text, Poem.create_date, Author.fullname, Book.name) \
        .select_from(Poem) \
        .join(Author, Author.id == Poem.author_id) \
        .join(Book, Book.id == Poem.book_id)

    if type_info == 'count':
        return 'В базе хранится {} произведений'.format(query.count())
    elif type_info == 'all':
        return query
    else:
        return None
    # --форматирование строки вывода сообщения-- #
    # result_text = f'В базе храниться {len(db)} стихотворений' + '\n'
    # for i in range(len(author_set)):
    #     result_text += f'Из них {author.count(author_set[i])} авторства "{author_set[i]}"' + '\n'
    # logging.info('получена информация об авторах')
    # return result_text[:-1]


def get_info_about_useractive(user_id: int):
    """
    статистика о полученых пользователем стихотворений

    :param user_id: id пользователя: int
    :return result_text: строку с информацией о прочитаных пользоватых стихов: str
    """
    logging.info('получена информация о просмотрах')

    query = session.query(Author.fullname, UserActive.poem_id) \
        .select_from(UserActive) \
        .join(Author, and_(Author.id == UserActive.author_id, UserActive.user_id == user_id))


    if query.first() is None:
        return 'Ваш список просмотров пуст'
    # --словарь по авторам-- #
    ap_dict = {}
    for x in query:
        if x[0] not in ap_dict:
            ap_dict[x[0]] = 1
        else:
            ap_dict[x[0]] += 1
    # --форматирование строки вывода сообщения-- #
    result_text = f'Вы получили {query.count()} стихотворений' + '\n'
    for k, v in ap_dict.items():
        result_text += f'Из них {k} написал :{v}' + '\n'
    return result_text[:-1]

def get_info_about_usersread():
    """
    получение информации о хранимых в бд авторов прозведений

    :param type_info: тип запрашиваемой информации: str
    :return Author object: количество или все записи таблицы: str
    """
   
    # query = session.query(Author.fullname, UserActive.poem_id) \
    #     .select_from(UserActive) \
    #     .join(Author, and_(Author.id == UserActive.author_id, UserActive.user_id == user_id))

    query = session.query(UserActive.user_id, UserActive.poem_id) \
        .order_by(UserActive.id.asc()) 

    if query.first() is None:
        return ''

    # --словарь по прочтениям-- #
    r_dict = {}
    for x in query:
        if x[0] not in r_dict:
            r_dict[x[0]] = 1
        else:
            r_dict[x[0]] += 1    

    # --форматирование строки вывода сообщения-- #
    result_text = ''
    for k, v in r_dict.items():
        result_text += f'Пользователь id: {k}, просмотрел: {v} стихотворений' + '\n'
    
    return result_text[:-1]

def restart_useractive(user_id: int):
    """
    очистка просмотров пользователя (users_active)

    :param user_id: id пользователя: int
    """

    logging.info(f'пользователь-[{user_id}], сбросил статистику просмотров')
    session.query(UserActive).filter_by(user_id=user_id).delete()
    session.commit()
  

def delete_user(user_id: int):
    """
    удаление пользователя из таблицы users

    :param user_id: id пользователя: int
    """
  
    logging.info(f'пользователь-[{user_id}], удален')
    session.query(User).filter_by(user_id=user_id).delete()
    session.commit()


def get_count_active_users():
    """
    Получение количества всех зарегистрированных пользователей

    """
    return session.query(User).count()




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




def check_new_poem_in_dir(admin_id):  # TODO
    """
    проверка и добавление новых стихотворений в каталоге
    """
    # --чтение txt файлов в папке--#
    d = read_txt.dataset
    if d:
        # --добавление новых стихотворений в бд--#
        logging.info('найдено {} новых стихотворений, но они не были добавлены')
        return len(d)
    else:
        logging.info('новых стихотворений не найдено')
        return 0 


# def f_db_table():
#     """
#     получение списка всех таблиц бд
#     :return список таблиц бд: list
#     """
#     sql = """
#         SELECT name FROM sqlite_master 
#         WHERE type='table'
#         ORDER BY name;"""
#     cursor.execute(sql)
#     records = cursor.fetchall()
#     result = [str(elem)[2:-3] for elem in records]
#     return result

# def f_user_in_table(user_id):
#     """
#     регистрация пользователя при нажитии на кнопку start
#     :param user_id: id пользователя: int
#     :return flg: результат проверки зареган ли пользователь:bool
#     """
#     flg = False
#     user_table = f_select_all_db('users')
#     # user_id_table = [elem[1] for elem in user_table]
#     if user_id in [elem[1] for elem in user_table]:
#         flg = True
#     return flg
        

# def f_reg_user(user_id:int):
#     """
#     внесение нового пользователя в таблицу

#     :param user_id: id пользователя: int
#     """
#     sql = """
#         INSERT INTO users 
#         VALUES (?, ?);"""
#     cursor.execute(sql, (None, user_id))
#     conn.commit()
#     logging.info('пользователь зарегистрирован!')


# def f_select_all_db(name_table):
#     """
#     выборка из базы, возвращает список из всех записей из таблицы name_table
    
#     :param name_table: название таблицы: str
#     :return records: список записей из таблицы: list
#     """
#     if name_table not in f_db_table():
#         logging.warning('такой таблицы не существуют')
#         return False
#     else:
#         sql = f"""SELECT * FROM {name_table};"""
#         cursor.execute(sql)
#         records = cursor.fetchall()
#         conn.commit()
#         logging.info('список всех записей таблицы {} получен'.format(name_table))
#         return records


# def f_get_poem(index=None):  # TODO изменить логику выборки одной записи
#     """
#     получение стихотворения, если индекс не передан то возвращается случайное стихотворение
#     :param index: номер стихотворения: int
#     :return: одну строку таблицы poems: list
#     """
#     db = f_select_all_db('poems')
#     if not index:
#         index = randint(1, len(db))
#     logging.info('стихотворение получено')
#     return db[index-1]


# def f_get_next(user_id):
#     """
#     запрос следующего стихотворениея
#     получение индекса крайнего прочитанного сообщения и отправка следующего
#     :param user_id: id пользователя: int
#     :return: одну строку таблицы poems: list
#     """
#     poem_list = f_select_read(user_id)
#     if not poem_list[-1]:
#         logging.info('получено первое стихотворение, тк ранее небыло прочитанных стихотворений')
#         return f_get_poem(1)
#     logging.info('получено следующее стихотворение')
#     return f_get_poem(int(poem_list[-1][0]) + 1)
   
    
# def f_select_read(user_id):
#     """
#     получение полученых стихотворений по пользователю
#     :param user_id: id пользователя: int    
#     :return r: все записи по пользователю: list
#     """
#     sql = f"""
#         SELECT received_poem_id, received_author, received_date
#         FROM usersreceived
#         WHERE user_id == {user_id}"""
#     cursor.execute(sql)
#     r = cursor.fetchall()
#     conn.commit()
#     logging.info('получен список прочитанных стихотворений')
#     return r


# def f_select_poem_by_author():  # TODO
#     """
#     получение стихотворений выбранного автора

#     :param args: tuple:
#     :return kwargs: dict:
#     """
#     pass


# def f_insert_db(data):
#     """
#     вставка новых данных
#     :param data: список стихотворений: list
#     """
#     k = j = 0
#     for line in data:
#         # --извлечение отделного элемента из списка и создание списка элементов в базе данных--#
#         stih = line[3]
#         db_stih_list = [row[4] for row in f_select_all_db('poems')]
#         # --если такой записи нет дабавляем всю линию--#
#         if stih not in db_stih_list:
#             k += 1
#             cursor.execute("""
#                 INSERT INTO poems (book, author, title_stih, stih, date_stih) 
#                 VALUES (?,?,?,?,?);""", 
#                 (line[0], line[1], line[2], line[3], line[4])
#                 )
#         conn.commit()
#     logging.info(u'[{}] новых стихотворений добавлены'.format(k))

       
# def f_update_read_user(user_id, poem_id, author): 
#     """
#     обновление списка полученных стихотворений
#     :param user_id: id пользователя: int
#     :param poem_id: id стихотворния из бд: int
#     :param author: имя автора стихотворения: str
#     """
#     sql = """
#         INSERT INTO usersreceived (user_id, received_poem_id, received_author, received_date) 
#         VALUES (?, ?, ?, ?);
#         """
#     dt_now = datetime.now().strftime('%Y-%M-%d %H:%M:%S')  
#     cursor.execute(sql, (user_id, poem_id, author, dt_now))
#     conn.commit()
#     logging.info('стихотворение добавлено с список просмотренных')

    
# def f_info_about_book(user_id):
#     """
#     получение информации о хранимых в бд стихотворениях и авторах
#     :param user_id: id пользователя: int
#     :return result_text: строку с информацие о базе: str
#     """
#     db = f_select_all_db('poems')
#     author = [a[2] for a in db]
#     author_set = list(set(author))
#     # --форматирование строки вывода сообщения-- #
#     result_text = f'В базе храниться {len(db)} стихотворений' + '\n'
#     for i in range(len(author_set)):
#         result_text += f'Из них {author.count(author_set[i])} авторства "{author_set[i]}"' + '\n'
#     logging.info('получена информация об авторах')
#     return result_text[:-1]


# def f_info_about_u_read(user_id):
#     """
#     статистика о полученых пользователем стихотворений
#     :param user_id: id пользователя: int
#     :return result_text: строку с информацией о прочитаных пользоватых стихов: str
#     """
#     poems_list = f_select_read(user_id)
#     if not poems_list:
#         return 'Ваш список просмотров пуст'
#     # --словарь по авторам-- #
#     ap_dict = {}
#     for x in poems_list:
#         if x[1] not in ap_dict:
#             ap_dict[x[1]] = 1
#         else:
#             ap_dict[x[1]] += 1
#     # --форматирование строки вывода сообщения-- #
#     result_text = f'Вы получили {len(poems_list)} стихотворений' + '\n'
#     for k, v in ap_dict.items():
#         result_text += f'Из них {k} написал {v}' + '\n'
#     logging.info('получена информация о просмотрах')
#     return result_text[:-1]

    
# def f_delete_user(tablename, user_id):
#     """
#     удаление пользователя из базы
#     :param tablename: название таблицы: str
#     :param user_id: id пользователя: int
#     """
#     sql = f"""DELETE FROM {tablename} WHERE user_id == {user_id};"""
#     cursor.execute(sql)
#     conn.commit()
#     s = 'удален' if tablename == 'users' else 'сбросил статистику просмотров'
#     logging.info(u'пользователь-[{}], {}'.format(user_id, s))
    

 

if __name__ == '__main__':
    print('(-_-)')

else:
    #коннект к новой бд
    engine_new = create_engine(
        f'sqlite:///{DB_FILE}', 
        connect_args={'check_same_thread': False}, 
        poolclass=StaticPool)
    Session = sessionmaker(bind=engine_new)
    session = Session()
    

       
    
