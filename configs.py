#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

# Debug
DEBUG = os.environ.get('DEBUG', False)

# Your bot token
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Bot administrator username, example: @Jone
ADMINISTRATOR_USERNAME = os.environ.get('ADMINISTRATOR_USERNAME')

# Database url
# SQLite, Postgresql, MySQL, Oracle, MS-SQL, Firebird, Sybase...
# More info: https://docs.sqlalchemy.org/en/13/dialects/
DATABASE_URI = os.environ.get('DATABASE_URL')

# imink API Token
SP2BATTLE_API_TOKEN = os.environ.get('SP2BATTLE_API_TOKEN')

# imink API address
SP2BATTLE_API_ADDRESS = os.environ.get('SP2BATTLE_API_ADDRESS')

# Webhook
# Enable webhook mode.
# Default is false.
# If you use webhook you must set the WEBHOOK_PORT and WEBHOOK_URL
# About webhook: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks
WEBHOOK_MODE = os.environ.get('WEBHOOK_MODE', False)

# Listen address
WEBHOOK_LISTEN = os.environ.get('WEBHOOK_LISTEN', '127.0.0.1')

# Webhook port
# Default is 5000.
WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT', 5000)

# Webhook port
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
