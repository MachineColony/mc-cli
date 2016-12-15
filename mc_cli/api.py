import os
import json
import requests
from httplib import HTTPException


class API():
    def __init__(self, url_key='mc_api_url'):
        conf_path = os.path.expanduser('~/.mc/config.json')
        if not os.path.exists(conf_path):
            raise IOError('No Machine Colony config found at ~/.mc/config.json')
        try:
            self.conf = json.load(open(conf_path, 'r'))
        except ValueError:
            raise ValueError('Couldn\'t parse Machine Colony config at ~/.mc/config.json. Malformed JSON?')
        self.base_url = self.conf[url_key]

    def _headers(self):
        return {
            'X-API-Key': self.conf.get('client_key'),
            'X-API-Secret': self.conf.get('client_secret')
        }

    def get(self, endpoint, **kwargs):
        resp = requests.get(
            '{}{}'.format(self.base_url, endpoint),
            headers=self._headers(),
            **kwargs)
        self._check_status(resp)
        return resp

    def post(self, endpoint, data, **kwargs):
        resp = requests.post(
            '{}{}'.format(self.base_url, endpoint),
            headers=self._headers(),
            json=data, **kwargs)
        self._check_status(resp)
        return resp

    def delete(self, endpoint):
        resp = requests.delete(
            '{}{}'.format(self.base_url, endpoint),
            headers=self._headers())
        self._check_status(resp)
        return resp

    def hook(self, key, data):
        resp = requests.post(
            '{}/{}'.format(self.conf['mc_hooks_url'], key),
            json=data)
        self._check_status(resp)
        return resp.json()

    def _check_status(self, resp):
        if resp.status_code != 200:
            raise HTTPException(
                'Non-200 status code: {} -> "{}"'.format(resp.status_code, resp.content))
