from datetime import datetime
import requests


class Twitch(object):
    version = 'helix'
    base_url = 'https://api.twitch.tv/helix'

    def __init__(self, user_id, client_id):
        self.user_id = user_id
        self.client_id = client_id
        self.login = None
        self.display_name = None
        self.user = {}
        self.stream = {}
        self.followers = {}
        self.channel = {}
        self.headers = {'Client-ID': self.client_id}

    def __repr__(self):
        return 'Twitch API class version: {}'.format(self.version)

    def is_live(self):
        self._get_stream()
        return True if self.stream else False

    def get_user(self):
        self._get_user()
        return self.user

    def get_stream(self):
        self._get_stream()
        return self.stream

    def get_game_name(self, game_id):
        game = self._get_game(game_id)
        return game['name'] if game else None

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
            stream_created_date = datetime.strptime(stream_created_at, '%Y-%m-%dT%H:%M:%SZ')
            stream_uptime = datetime.utcnow() - stream_created_date
            if human:
                return self.sec_to_human(stream_uptime.seconds)
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
                self.user = d['data'][0]
                self.login = d['data'][0]['login']
                self.display_name = d['data'][0]['display_name']

    def _get_stream(self):
        if not self.stream:
            params = {'user_id': self.user_id}
            url = '{}/streams'.format(self.base_url)
            r = requests.get(url, params=params, headers=self.headers)
            d = r.json()
            self.stream = d['data'][0] if d['data'] else None

    def _get_game(self, game_id):
        # params['id'] = game_id if game_id else params['name'] = game_name
        params = {'id': game_id}
        url = '{}/games'.format(self.base_url)
        r = requests.get(url, params=params, headers=self.headers)
        d = r.json()
        return d['data'][0] if d['data'] else None

    @staticmethod
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
        except Exception:
            return None
