#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sp2bot import store
from sp2bot.botcontext import BotContext
from sp2bot.message import Message
from sp2bot.splatoon2 import Splatoon2


def check_session_handler(func):
    def wrapper(self, update, context, **optional_args):
        if not update.message:
            return

        bot_context = BotContext(update, context)
        user = bot_context.user
        if user and user.iksm_session:

            if not user.sp2_user:
                sp2_user = Splatoon2(user.iksm_session).get_user()
                if not sp2_user:
                    bot_context.send_message(
                        Message(bot_context).session_invalid)
                    return

                user.sp2_user = sp2_user.player
                store.update_user(user)

            if optional_args:
                return func(self, bot_context, **optional_args)
            else:
                return func(self, bot_context)
        else:
            bot_context.send_message(Message(bot_context).session_invalid)

    return wrapper


def handler(func):
    def wrapper(self, update, context):
        if not update.message:
            return

        bot_context = BotContext(update, context)
        return func(self, bot_context)

    return wrapper
