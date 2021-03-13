#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

# import pycurl
# from io import BytesIO

import requests, sys
import uuid, time, random, string
import os, base64, hashlib
from telegram.bot import log

from sp2bot.api import APIAuthError, API
from sp2bot.splatoon2models import SP2User, SP2BattleOverview, SP2BattleResult


class Splatoon2(API):

    def __init__(self, iksm_session):
        super(Splatoon2, self).__init__()
        self.iksm_session = iksm_session
        self._base_url = 'https://app.splatoon2.nintendo.net'
        self._headers = {
            'Cookie': f'iksm_session={self.iksm_session}; path=/; '
                      f'domain=.app.splatoon2.nintendo.net;',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }

    @log
    def get_user(self):
        try:
            data = self.get('/api/records')
            user = SP2User.de_json(data)
            return user
        except APIAuthError:
            return None

    @log
    def get_user_info(self):
        try:
            return self.get('/api/records')
        except APIAuthError:
            return None

    @log
    def get_battle_overview(self):
        data = self.get('/api/results')
        battle_overview = SP2BattleOverview.de_json(data)
        return battle_overview

    @log
    def get_battle(self, battle_number):
        data = self.get(f'/api/results/{battle_number}')
        battle = SP2BattleResult.de_json(data)
        return battle

    @log
    def get_battle_share_url(self, battle_number):
        data = self.post(f'/api/share/results/{battle_number}')
        return data.get('url')

    # pycurl version
    # def _request_pycurl(self, method, path):
    #     buffer = BytesIO()
    #     c = pycurl.Curl()
    #     c.setopt(c.URL, f'{self._base_url}{path}')
    #     c.setopt(pycurl.COOKIE, f'iksm_session={self.iksm_session}; path=/; '
    #                             'domain=.app.splatoon2.nintendo.net;')
    #     c.setopt(c.WRITEDATA, buffer)
    #     c.setopt(c.CAINFO, certifi.where())
    #     c.perform()
    #     c.close()
    #
    #     return buffer.getvalue()


AUTH_CODE_VERIFIERS = {}


class Splatoon2Auth:

    def __init__(self, session_token=None):
        self.session_token = session_token
        self.version = '1.5.3'

    def get_login_url(self, user_id):
        return None

    def get_session_token(self, user_id, session_token_code):
        return None

    def get_cookie(self, session_token):
        return None

