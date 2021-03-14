#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime


Base = declarative_base()


class Poem(Base):
    """Модель для хранения стихотворений"""
    __tablename__ = 'poems'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    book_id = Column(Integer, nullable=True)
    author_id = Column(Integer, nullable=True)
    title = Column(String, nullable=True)
    text = Column(String, nullable=False)
    create_date = Column(String, nullable=True)

    def __repr__(self):
        return f'Poems {self.id}, {self.title}'


class Author(Base):
    """Модель для хранения авторов стихотворений"""
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    fullname = Column(String, nullable=False)
    aname = Column(String, nullable=True)
    fname = Column(String, nullable=True)
    
    def __repr__(self):
        return f'Author {self.fullname}'


class Book(Base):
    """Модель для хранения сборников стихотворений"""
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date_created = Column(String, nullable=True)
    
    def __repr__(self):
        return f'Book {self.name}'


class User(Base):
    """Модель для хранения пользователей"""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=False)
    name = Column(String, nullable=True)
    date_connected = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f'User {self.user_id}'


class UserActive(Base):
    """Модель для хранения активности просмотров пользователей"""
    __tablename__ = 'user_active'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    author_id = Column(Integer, nullable=True)
    poem_id = Column(Integer, nullable=False)
    book_id = Column(Integer, nullable=True)
    date_view = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f'UserActive {self.id}-{self.date_view}'


if __name__ == '__main__':
    print('(-_-)')
