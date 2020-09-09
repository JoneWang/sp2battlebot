#!/usr/bin/env python
# -*- coding: utf-8 -*-
from configs import SP2BATTLE_API_TOKEN
from sp2bot.api import API, APIAuthError
from telegram.bot import log


class SP2BattleAPI(API):

    def __init__(self):
        super(SP2BattleAPI, self).__init__()
        self._base_url = 'https://sp2battleapi.herokuapp.com'
        self._headers = {'X-Access-Token': SP2BATTLE_API_TOKEN}

    @log
    def get_client_token(self, user_id, iksm_session):
        try:
            data = self.get(
                f'/client_token?user_id={user_id}&iksm_session={iksm_session}')
            if data['code'] == 0:
                return data['data']
            else:
                return None
        except:
            return None

    @log
    def reset_client_token(self, user_id, iksm_session):
        try:
            data = self.post(f'/reset_client_token',
                             data={
                                 'user_id': user_id,
                                 'iksm_session': iksm_session
                             })
            if data['code'] == 0:
                return data['data']
            else:
                return None
        except:
            return None
