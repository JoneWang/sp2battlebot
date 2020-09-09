#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import certifi
import telegram.vendor.ptb_urllib3.urllib3 as urllib3
from telegram.error import TimedOut, NetworkError, _lstrip_str


class APIAuthError(Exception):
    def __init__(self):
        super(APIAuthError, self).__init__('auth error')


class APIError(Exception):
    def __init__(self, message):
        super(APIError, self).__init__()

        msg = _lstrip_str(message, 'Error: ')
        msg = _lstrip_str(msg, '[Error]: ')
        msg = _lstrip_str(msg, 'Bad Request: ')
        if msg != message:
            # api_error - capitalize the msg...
            msg = msg.capitalize()
        self.message = msg

    def __repr__(self):
        return '%s' % self.message


class API:
    def __init__(self):
        self._con_pool = urllib3.PoolManager(num_pools=50,
                                             cert_reqs='CERT_REQUIRED',
                                             ca_certs=certifi.where())
        self._headers = {}

    def post(self, path, data=None):
        return self.request(path, 'POST', data=data)

    def get(self, path):
        return self.request(path, 'GET')

    def request(self, path, method, data=None):
        json_data = self._request(method, path, data=data)
        try:
            decoded_s = json_data.decode('utf-8')
            data = json.loads(decoded_s)
            return data
        except UnicodeDecodeError:
            logging.getLogger(__name__).debug(
                'Logging raw invalid UTF-8 response:\n%r', json_data)
            raise APIError(
                'Server response could not be decoded using UTF-8')
        except ValueError:
            raise APIError('Invalid server response')

    def _request(self, method, path, data=None):
        kwargs = {
            'method': method,
            'url': f"{self._base_url}{path}",
            'headers': self._headers,
            'fields': data,
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
            raise APIAuthError()
        else:
            message = 'Unknown HTTPError'
            raise NetworkError('{0} ({1})'.format(message, resp.status))
