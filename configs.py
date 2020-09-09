#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

# Debug
DEBUG = os.environ.get('DEBUG', False)

# Run environment: None or Heroku
# Heroku
RUN_ENVIRONMENT = os.environ.get('RUN_ENVIRONMENT')

# Your bot token
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Bot administrator username, example: @Jone
ADMINISTRATOR_USERNAME = os.environ.get('ADMINISTRATOR_USERNAME')

# Database
DATABASE_URI = os.environ.get('DATABASE_URL')

# Heroku PORT
HEROKU_PORT = os.environ.get('PORT')

# Heroku url
HEROKU_URL = os.environ.get('HEROKU_URL')

# Sp2Battle API Token
SP2BATTLE_API_TOKEN = os.environ.get('SP2BATTLE_API_TOKEN')
