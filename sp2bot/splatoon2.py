#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

# import pycurl
# from io import BytesIO

import certifi
import telegram.vendor.ptb_urllib3.urllib3 as urllib3
from telegram.bot import log
from telegram.error import TimedOut, NetworkError, _lstrip_str

from sp2bot.splatoon2models import SP2User, SP2BattleOverview, SP2BattleResult


class Splatoon2SessionInvalid(Exception):
    def __init__(self):
        super(Splatoon2SessionInvalid, self).__init__('Session invalid')


class Splatoon2Error(Exception):
    def __init__(self, message):
        super(Splatoon2Error, self).__init__()

        msg = _lstrip_str(message, 'Error: ')
        msg = _lstrip_str(msg, '[Error]: ')
        msg = _lstrip_str(msg, 'Bad Request: ')
        if msg != message:
            # api_error - capitalize the msg...
            msg = msg.capitalize()
        self.message = msg

    def __repr__(self):
        return '%s' % self.message


class Splatoon2:

    def __init__(self, iksm_session):
        self.iksm_session = iksm_session
        self._base_url = 'https://app.splatoon2.nintendo.net'
        self._con_pool = urllib3.PoolManager(num_pools=50,
                                             cert_reqs='CERT_REQUIRED',
                                             ca_certs=certifi.where())

    @log
    def get_user(self):
        try:
            data = self.get('/api/records')
            user = SP2User.de_json(data)
            return user
        except Splatoon2SessionInvalid:
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

    def get(self, path):
        json_data = self._request('GET', path)
        try:
            decoded_s = json_data.decode('utf-8')
            data = json.loads(decoded_s)
            return data
        except UnicodeDecodeError:
            logging.getLogger(__name__).debug(
                'Logging raw invalid UTF-8 response:\n%r', json_data)
            raise Splatoon2Error(
                'Server response could not be decoded using UTF-8')
        except ValueError:
            raise Splatoon2Error('Invalid server response')

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

    def _request(self, method, path):
        kwargs = {
            'method': method,
            'url': f"{self._base_url}{path}",
            'headers': {
                'Cookie': f'iksm_session={self.iksm_session}; path=/; '
                          f'domain=.app.splatoon2.nintendo.net;',
                'Accept': 'application/json'
            }
        }

        try:
            resp = self._con_pool.request(**kwargs)
        except urllib3.exceptions.TimeoutError:
            raise TimedOut()
        except urllib3.exceptions.HTTPError as error:
            raise NetworkError('urllib3 HTTPError {0}'.format(error))

        if 200 <= resp.status <= 299:
            return resp.data
        elif resp.status == 403:
            raise Splatoon2SessionInvalid()
        else:
            message = 'Unknown HTTPError'
            raise NetworkError('{0} ({1})'.format(message, resp.status))
