#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json


BASEDIR = os.path.abspath(os.path.dirname(__file__))
with open(BASEDIR + '/config.json', 'r') as f:
	config_json = json.load(f)
		
class Config:
	"""Конфигурационные параметры преложения"""

	TG_PROXY_URL = config_json['TG_PROXY_URL']
	TG_ADMIN_ID = config_json['TG_ADMIN_ID']

	# deploy
	# TG_NAME = config_json['TG_NAME']
	# TG_TOKEN = config_json['TG_TOKEN']
	
	# test
	TG_NAME = config_json['TG_NAME_D']
	TG_TOKEN = config_json['TG_TOKEN_D']


	LOG_DIR = BASEDIR + '/log'
	LOG_FILENAME = 'filelog.log'
	LOG_FILE = LOG_DIR + '/' + LOG_FILENAME
	LOG_FORMAT = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-3s [%(asctime)s]  %(message)s'

	# --commands for user--#
	commands = {  
	    # command description used in the "help" command
	    'start': 'Начало использования бота',
	    'help': 'Информация о доступных командах',
	    'random': 'Получить случайное стихотворение',
	    'next': 'Получить следующее стихотворение',
	    'book': 'Получить информацию о хранимых стихотворениях',
	    'info': 'Получить статистику по прочитанным стихотворениям',
	    'restart': 'Сброс всей статистии',
	    'end': 'Удаление бота, завершение работы с ботом',
	    'author': 'Выбрать автора',  #TODO
	    'reset_author': 'Сброс выборки по авторам',  #TODO
	}

	# --commands for admin--#
	admin_commands = {
	    # admin command desc used in the "adminhelp" command
	    'adminhelp': 'Информация о доступных командах',
	    'statu': 'Количество активных пользователей',
	    'staturd': 'Статистика чтений пользователей',
	    'toppoem': 'Топ просмотреных стихотворений N-int(дефолт 5)',
	    'topauthor': 'Топ просмотреных стихотворений N-int(дефолт 1)',
	    'dcu': 'Пересоздать таблицу пользователей',
	    'dcru': 'Пересоздать таблицу просмотров пользователей',
	    'checkpoem': 'Проверка и добавление новых стихотворений', #TODO
	}

if __name__ == '__main__':
	print('(-_-)')

'''
телеграм прокси проверить на пригодность для бота 
