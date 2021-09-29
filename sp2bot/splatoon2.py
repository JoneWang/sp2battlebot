#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

# import pycurl
# from io import BytesIO

import certifi
import requests, sys
import uuid, time, random, string
import os, base64, hashlib
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
    def get_user_info(self):
        try:
            return self.get('/api/records')
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

    @log
    def get_battle_share_url(self, battle_number):
        data = self.post(f'/api/share/results/{battle_number}')
        return data.get('url')

    def post(self, path):
        return self.request(path, 'POST')

    def get(self, path):
        return self.request(path, 'GET')

    def request(self, path, method):
        json_data = self._request(method, path)
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
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
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


AUTH_CODE_VERIFIERS = {}


class Splatoon2Auth:

    def __init__(self, session_token=None):
        self.session_token = session_token
        self.nso_version = '1.13.0'

    def get_login_url(self, user_id):
        session = requests.Session()

        auth_state = base64.urlsafe_b64encode(os.urandom(36))

        auth_code_verifier = base64.urlsafe_b64encode(os.urandom(32))
        print(f'auth_code_verifier {auth_code_verifier}')
        auth_cv_hash = hashlib.sha256()
        auth_cv_hash.update(auth_code_verifier.replace(b"=", b""))
        auth_code_challenge = base64.urlsafe_b64encode(auth_cv_hash.digest())

        AUTH_CODE_VERIFIERS[user_id] = auth_code_verifier

        app_head = {
            'Host': 'accounts.nintendo.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8n',
            'DNT': '1',
            'Accept-Encoding': 'gzip,deflate,br',
        }

        body = {
            'state': auth_state,
            'redirect_uri': 'npf71b963c1b7b6d119://auth',
            'client_id': '71b963c1b7b6d119',
            'scope': 'openid user user.birthday user.mii user.screenName',
            'response_type': 'session_token_code',
            'session_token_code_challenge': auth_code_challenge.replace(b"=",
                                                                        b""),
            'session_token_code_challenge_method': 'S256',
            'theme': 'login_form'
        }

        url = 'https://accounts.nintendo.com/connect/1.0.0/authorize'

        try:
            r = session.get(url, headers=app_head, params=body)
        except Exception as e:
            # TODO:
            print(e)
            return None

        post_login = r.history[0].url
        # TODO:
        return post_login

    def get_session_token(self, user_id, session_token_code):
        '''Helper function for log_in().'''
        session = requests.Session()

        try:
            auth_code_verifier = AUTH_CODE_VERIFIERS[user_id]
        except:
            # TODO:
            return None

        app_head = {
            'User-Agent': f'OnlineLounge/{self.nso_version} NASDKAPI Android',
            'Accept-Language': 'en-US',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '540',
            'Host': 'accounts.nintendo.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        body = {
            'client_id': '71b963c1b7b6d119',
            'session_token_code': session_token_code,
            'session_token_code_verifier': auth_code_verifier.replace(b"=", b"")
        }
        print(f'body {body}')

        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'

        try:
            r = session.post(url, headers=app_head, data=body)
        except Exception as e:
            print(e)
            return None

        # TODO:
        return json.loads(r.text)["session_token"]

    def get_cookie(self, session_token):
        '''Returns a new cookie provided the session_token.'''
        timestamp = int(time.time())
        guid = str(uuid.uuid4())

        app_head = {
            'Host': 'accounts.nintendo.com',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Language': 'en-US',
            'Content-Length': '439',
            'Accept': 'application/json',
            'Connection': 'Keep-Alive',
            'User-Agent': f'OnlineLounge/{self.nso_version} NASDKAPI Android'
        }

        body = {
            'client_id': '71b963c1b7b6d119',  # Splatoon 2 service
            'session_token': session_token,
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token'
        }

        url = "https://accounts.nintendo.com/connect/1.0.0/api/token"

        r = requests.post(url, headers=app_head, json=body)
        id_response = json.loads(r.text)

        # get user info
        try:
            app_head = {
                'User-Agent': f'OnlineLounge/{self.nso_version} NASDKAPI Android',
                'Accept-Language': 'en-US',
                'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(
                    id_response["access_token"]),
                'Host': 'api.accounts.nintendo.com',
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'gzip'
            }
        except:
            print(
                "Not a valid authorization request. Please delete config.txt and try again.")
            print("Error from Nintendo (in api/token step):")
            print(json.dumps(id_response, indent=2))
            # TODO:
            return None

        url = "https://api.accounts.nintendo.com/2.0.0/users/me"

        r = requests.get(url, headers=app_head)
        user_info = json.loads(r.text)

        nickname = user_info["nickname"]

        # get access token
        app_head = {
            'Host': 'api-lp1.znc.srv.nintendo.net',
            'Accept-Language': 'en-US',
            'User-Agent': f'com.nintendo.znca/{self.nso_version} (Android/7.1.2)',
            'Accept': 'application/json',
            'X-ProductVersion': self.nso_version,
            'Content-Type': 'application/json; charset=utf-8',
            'Connection': 'Keep-Alive',
            'Authorization': 'Bearer',
            'Content-Length': '1036',
            'X-Platform': 'Android',
            'Accept-Encoding': 'gzip'
        }

        body = {}
        try:
            idToken = id_response["access_token"]

            f = self.call_imink_api(idToken, guid, timestamp, "1")

            parameter = {
                'f': f,
                'naIdToken': idToken,
                'timestamp': timestamp,
                'requestId': guid,
                'naCountry': user_info["country"],
                'naBirthday': user_info["birthday"],
                'language': user_info["language"]
            }
        except:
            print("Error(s) from Nintendo:")
            print(json.dumps(id_response, indent=2))
            print(json.dumps(user_info, indent=2))
            # TODO:
            return None
        body["parameter"] = parameter

        url = "https://api-lp1.znc.srv.nintendo.net/v1/Account/Login"

        r = requests.post(url, headers=app_head, json=body)
        splatoon_token = json.loads(r.text)

        try:
            idToken = splatoon_token["result"]["webApiServerCredential"][
                "accessToken"]
            f = self.call_imink_api(idToken, guid, timestamp, "2")
        except:
            print("Error from Nintendo (in Account/Login step):")
            print(json.dumps(splatoon_token, indent=2))
            # TODO:
            return None

        # get splatoon access token
        try:
            app_head = {
                'Host': 'api-lp1.znc.srv.nintendo.net',
                'User-Agent': 'com.nintendo.znca/{self.nso_version} (Android/7.1.2)',
                'Accept': 'application/json',
                'X-ProductVersion': self.nso_version,
                'Content-Type': 'application/json; charset=utf-8',
                'Connection': 'Keep-Alive',
                'Authorization': 'Bearer {}'.format(
                    splatoon_token["result"]["webApiServerCredential"][
                        "accessToken"]),
                'Content-Length': '37',
                'X-Platform': 'Android',
                'Accept-Encoding': 'gzip'
            }
        except:
            print("Error from Nintendo (in Account/Login step):")
            print(json.dumps(splatoon_token, indent=2))
            # TODO:
            return None

        body = {}
        parameter = {
            'id': 5741031244955648,
            'f': f,
            'registrationToken': idToken,
            'timestamp': timestamp,
            'requestId': guid
        }
        body["parameter"] = parameter

        url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"

        r = requests.post(url, headers=app_head, json=body)
        splatoon_access_token = json.loads(r.text)

        # get cookie
        try:
            app_head = {
                'Host': 'app.splatoon2.nintendo.net',
                'X-IsAppAnalyticsOptedIn': 'false',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip,deflate',
                'X-GameWebToken': splatoon_access_token["result"][
                    "accessToken"],
                'Accept-Language': 'en-US',
                'X-IsAnalyticsOptedIn': 'false',
                'Connection': 'keep-alive',
                'DNT': '0',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
                'X-Requested-With': 'com.nintendo.znca'
            }
        except:
            print("Error from Nintendo (in Game/GetWebServiceToken step):")
            print(json.dumps(splatoon_access_token, indent=2))
            # TODO:
            return None

        url = "https://app.splatoon2.nintendo.net/?lang={}".format('en-US')
        r = requests.get(url, headers=app_head)
        return r.cookies["iksm_session"]

    def call_imink_api(self, id_token, guid, timestamp, hash_method):
        '''Passes in headers to the flapg API (Android emulator) and fetches the response.'''

        try:
            body = {
                'token': id_token,
                'timestamp': str(timestamp),
                'request_id': guid,
                'hash_method': hash_method
            }

            app_head = {
                'User-Agent': 'sp2battlebot/0.0.1',
            }

            url = 'https://api.imink.jone.wang/f'

            api_response = requests.post(url, headers=app_head, json=body)
            f = json.loads(api_response.text)["f"]
            return f
        except:
            try:  # if api_response never gets set
                if api_response.text:
                    print(u"Error from the imink API:\n{}".format(
                        json.dumps(json.loads(api_response.text), indent=2,
                                   ensure_ascii=False)))
                elif api_response.status_code == requests.codes.not_found:
                    print(
                        "Error from the imink API: Error 404 (offline or incorrect headers).")
                else:
                    print("Error from the imink API: Error {}.".format(
                        api_response.status_code))
            except:
                pass

            # TODO:
            return None
