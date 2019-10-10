#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.error import BadRequest

from sp2bot import store
from sp2bot.models import User


class BotContext:

    def __init__(self, telegram_update, telegram_context):
        self.telegram_update = telegram_update
        self.telegram_context = telegram_context

        tg_user = telegram_update.message.from_user
        user = store.select_user(tg_user.id)
        if user:
            self.user = user
        else:
            self.user = User.from_tg_user(tg_user)
        self._bot_user = None

    @property
    def bot_user(self):
        if not self._bot_user:
            self._bot_user = self.bot.get_me()

        return self._bot_user

    @property
    def bot(self):
        return self.telegram_context.bot

    @property
    def chat(self):
        if self.telegram_update.message:
            return self.telegram_update.message.chat
        return None

    @property
    def chat_id(self):
        return self.chat.id

    @property
    def message(self):
        return self.telegram_update.message

    @property
    def args(self):
        return self.telegram_context.args

    def send_message(self, message, chat_id=None):
        if not chat_id:
            chat_id = self.chat_id

        if type(message) == str:
            content = message
            message_type = None
        else:
            (content, message_type) = message
        parse_mode = message_type if message_type else None
        try:
            self.bot.send_message(chat_id,
                                  content,
                                  parse_mode=parse_mode)
        except BadRequest as e:
            # Resend
            self.bot.send_message(chat_id, content)
