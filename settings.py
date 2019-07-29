import os


class Settings(object):
    phonetic_name = os.environ.get('phonetic_name')
    user_id = os.environ.get('user_id')
    client_id = os.environ.get('client_id')
    log_level = 'DEBUG'
