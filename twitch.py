from datetime import datetime
import os
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Twitch(object):
    def __init__(self, user_id):
        self.version = 'helix'
        self.user_id = user_id
        self.client_id = os.environ.get('client_id')
        self.base_url = 'https://api.twitch.tv/helix'
        self.headers = {'Client-ID': self.client_id}
        self.channel = {}
        self.stream = {}
        self.user = {}
        self.followers = {}
        self.name = ''
        self.display_name = ''

    def is_live(self):
        self._get_stream()
        return True if self.stream else False

    def get_user(self):
        self._get_user()
        return self.user

    def get_stream(self):
        self._get_stream()
        return self.stream

    def get_followers(self, only_total=True):
        self._get_followers()
        if only_total:
            return self.followers['total']
        else:
            return self.followers

    def get_uptime(self, human=True):
        self._get_stream()
        if self.stream:
            stream_created_at = self.stream['started_at']
            stream_created_date = datetime.strptime(
                stream_created_at, '%Y-%m-%dT%H:%M:%SZ'
            )
            stream_uptime = datetime.utcnow() - stream_created_date
            if human:
                return sec_to_human(stream_uptime.seconds)
            else:
                return stream_uptime.seconds
        else:
            return 'Offline' if human else None

    def _get_followers(self):
        if not self.followers:
            params = {'to_id': self.user_id}
            url = '{}/users/follows'.format(self.base_url)
            r = requests.get(url, params=params, headers=self.headers)
            d = r.json()
            self.followers = d

    def _get_user(self):
        if not self.user:
            params = {'id': self.user_id}
            url = '{}/users'.format(self.base_url)
            r = requests.get(url, params=params, headers=self.headers)
            d = r.json()
            if d['data']:
                self.stream = d['data'][0]
                self.user = d['data'][0]['login']
                self.display_name = d['data'][0]['display_name']

    def _get_stream(self):
        if not self.stream:
            params = {'user_id': self.user_id}
            url = '{}/streams'.format(self.base_url)
            r = requests.get(url, params=params, headers=self.headers)
            d = r.json()
            self.stream = d['data'][0] if d['data'] else None


def sec_to_human(seconds):
    try:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h < 1:
            ms = 's' if m > 1 else ''
            o = '{} minute{}'.format(m, ms)
        else:
            hs = 's' if h > 1 else ''
            ms = 's' if m > 1 else ''
            o = '{} hour{} and {} minute{}'.format(h, hs, m, ms)
        return o
    except Exception as error:
        logger.exception(error)
        return None
