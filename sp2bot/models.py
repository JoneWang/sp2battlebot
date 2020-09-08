#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import Chat

from sp2bot.splatoon2models import SP2Player
from sp2bot.utils.model import Model


class User(Model):

    @classmethod
    def from_tg_user(cls, tg_user):
        return User(tg_user.id,
                    tg_user.first_name,
                    username=tg_user.username,
                    last_name=tg_user.last_name,
                    )

    def __init__(self,
                 id,
                 first_name,
                 username=None,
                 last_name=None,
                 push=False,
                 iksm_session=None,
                 session_token=None,
                 sp2_principal_id=None,
                 sp2_nickname=None,
                 sp2_style=None,
                 sp2_species=None,
                 sp2_user=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.push = push
        self.iksm_session = iksm_session
        self.session_token = session_token

        if iksm_session and sp2_principal_id:
            self.sp2_user = SP2Player(sp2_principal_id,
                                      nickname=sp2_nickname,
                                      style=sp2_style,
                                      species=sp2_species,)
        else:
            self.sp2_user = sp2_user

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(User, cls).de_json(data)

        data['sp2_user'] = SP2Player.de_json(data.get('sp2_user'))

        return cls(**data)

    @property
    def display_name(self):
        return f'@{self.username}' if self.username else self.first_name


class BattlePoll(Model):

    def __init__(self,
                 user,
                 chat,
                 last_message_id=None,
                 last_battle_number=None,
                 last_battle_udemae=None,
                 last_battle_rule=None,
                 game_count=0,
                 game_victory_count=0):
        self.chat = chat
        self.user = user
        self.last_message_id = last_message_id
        self.last_battle_number = last_battle_number
        self.last_battle_udemae = last_battle_udemae
        self.last_battle_rule = last_battle_rule
        self.game_count = game_count
        self.game_victory_count = game_victory_count

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(BattlePoll, cls).de_json(data)

        data['user'] = User.de_json(data.get('user'))
        data['chat'] = Chat.de_json(data.get('chat'), None)
        data['last_battle_udemae'] = SP2Player.Udemae.de_json(data.get('last_battle_udemae', None))

        return cls(**data)
