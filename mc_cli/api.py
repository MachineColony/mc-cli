import os
import json
import requests
from httplib import HTTPException


class API():
    def __init__(self):
        conf_path = os.path.expanduser('~/.mc')
        if not os.path.exists(conf_path):
            raise IOError('No Machine Colony config found at ~/.mc')
        try:
            self.conf = json.load(open(conf_path, 'r'))
        except ValueError:
            raise ValueError('Couldn\'t parse Machine Colony config at ~/.mc. Malformed JSON?')

    def post(self, endpoint, data, **kwargs):
        headers = {'Authorization': self.conf['auth_token']}
        resp = requests.post(
            '{}{}'.format(self.conf['mc_url'], endpoint),
            headers=headers,
            json=data, **kwargs)
        self._check_status(resp)
        return resp

    def delete(self, endpoint):
        headers = {'Authorization': self.conf['auth_token']}
        resp = requests.delete(
            '{}{}'.format(self.conf['mc_url'], endpoint),
            headers=headers)
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
