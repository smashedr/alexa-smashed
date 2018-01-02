from datetime import datetime
import os
import logging
import requests
from alexa import alexa_resp

logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_ID = '22193985'
CHANNEL = 'smashed926'
PHONETIC = 'smashed nine two six'
HEADERS = {
    'Client-ID': os.environ.get('client_id'),
}


def get_user():
    params = {'id': USER_ID}
    url = 'https://api.twitch.tv/helix/users'
    r = requests.get(url, params=params, headers=HEADERS)
    d = r.json()
    return d['data'][0] if d['data'] else None


def get_stream():
    params = {'user_id': USER_ID}
    url = 'https://api.twitch.tv/helix/streams'
    r = requests.get(url, params=params, headers=HEADERS)
    d = r.json()
    return d['data'][0] if d['data'] else None


def convert_time(seconds):
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


def get_uptime(stream=None):
    if not stream:
        stream = get_stream()
    if stream:
        stream_created_at = stream['started_at']
        stream_created_date = datetime.strptime(stream_created_at, '%Y-%m-%dT%H:%M:%SZ')
        stream_uptime = datetime.utcnow() - stream_created_date
        return stream_uptime.seconds
    else:
        return None


def check_live():
    logger.info('Streaming')
    stream = get_stream()
    logger.info('stream: {}'.format(stream))
    if stream:
        uptime = convert_time(get_uptime(stream))
        speech = 'Yes, {} has been streaming for {}.'.format(
            PHONETIC, uptime
        )
        return alexa_resp(speech, 'Stream Live')
    else:
        speech = 'No, {} is not currently streaming.'.format(PHONETIC)
        return alexa_resp(speech, 'Stream Offline')


def lambda_handler(event, context):
    try:
        logger.info(event)
        intent = event['request']['intent']['name']
        if intent == 'Streaming':
            return check_live()
        else:
            raise ValueError('Unknown Intent')
    except Exception as error:
        logger.exception(error)
        return alexa_resp('Error. {}'.format(error), 'Error')
