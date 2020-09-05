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
	LOG_FORMAT = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'


if __name__ == '__main__':
	print('(-_-)')

