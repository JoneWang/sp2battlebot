#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from threading import Thread

from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler

import configs
from sp2bot.controller import Controller
from sp2bot.tasks import Task
import logging

if configs.DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


class Bot:

    # Bot
    def __init__(self):
        # Get token with configs
        token = configs.TELEGRAM_BOT_TOKEN

        # Create updater
        updater = Updater(token, use_context=True)
        dp = updater.dispatcher

        # Stop handle
        def stop_and_restart():
            updater.stop()
            os.execl(sys.executable, sys.executable, *sys.argv)

        # Restart handle
        def restart(update, context):
            update.message.reply_text('Bot is restarting...')
            Thread(target=stop_and_restart).start()

        # Stop sig handler
        def user_sig_handler(signum, frame):
            print('Stopped')
            pass

        updater.user_sig_handler = user_sig_handler

        # Create Task
        task = Task()

        # Set handlers
        controller = Controller(task)

        dp.add_handler(CommandHandler('restartbot',
                                      restart,
                                      filters=Filters.user(
                                          username=configs.ADMINISTRATOR_USERNAME
                                      )))
        dp.add_handler(CommandHandler('start', controller.start))
        dp.add_handler(CommandHandler('gettoken', controller.get_token))
        dp.add_handler(
            CommandHandler('settoken', controller.generate_iksm_and_set))
        dp.add_handler(CommandHandler('setsession', controller.set_session))
        dp.add_handler(CommandHandler('last', controller.last))
        dp.add_handler(CommandHandler('last50', controller.last50))
        dp.add_handler(CommandHandler('pushhere',
                                      controller.start_push,
                                      pass_job_queue=True))
        dp.add_handler(CommandHandler('startpush',
                                      controller.start_push,
                                      pass_job_queue=True))
        dp.add_handler(CommandHandler('stoppush', controller.stop_push))
        dp.add_handler(CommandHandler('resetpush', controller.reset_push))
        dp.add_handler(CommandHandler('help', controller.help))
        dp.add_handler(CallbackQueryHandler(controller.menu_actions))

        # Set task job
        task.job_queue = updater.job_queue

        # Run jobs in database
        task.load_and_run_all_push_job()

        # Run keep-alive jobs
        task.start_all_user_keep_alive_task()

        # Launch
        if configs.RUN_ENVIRONMENT == 'Heroku':
            updater.start_webhook(
                listen="0.0.0.0",
                port=int(configs.HEROKU_PORT),
                url_path=configs.TELEGRAM_BOT_TOKEN
            )
            updater.bot.setWebhook(
                configs.HEROKU_URL + configs.TELEGRAM_BOT_TOKEN
            )
        else:
            updater.start_polling()

        self.updater = updater

    def run(self):
        self.updater.idle()
