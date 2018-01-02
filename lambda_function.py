import os
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CHANNEL = 'smashed926'
PHONETIC = 'smashed nine two six'
HEADERS = {
    'Client-ID': os.environ.get('client_id'),
    'Accept': 'application/vnd.twitchtv.v5+json',
}


def build_speech_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_alexa_response(session_attributes, speech_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speech_response
    }


def alexa_resp(speech, title, reprompt=None, session_end=True):
    alexa = build_alexa_response(
        {}, build_speech_response(title, speech, reprompt, session_end)
    )
    return alexa


def get_user():
    url = 'https://api.twitch.tv/kraken/users?login={}'.format(CHANNEL)
    r = requests.get(url, headers=HEADERS)
    d = r.json()
    for user in d['users']:
        if user['name'].lower() == CHANNEL:
            return user
    raise ValueError('Unable to locate user.')


def get_stream(channel_id):
    url = 'https://api.twitch.tv/kraken/streams/{}'.format(channel_id)
    r = requests.get(url, headers=HEADERS)
    return r.json()


def check_live(event):
    logger.info('Streaming')
    user = get_user()
    logger.info('user: {}'.format(user))
    stream = get_stream(user['_id'])
    logger.info('stream: {}'.format(stream))
    if stream['stream']:
        speech = 'Yes, {} is streaming right now.'.format(PHONETIC)
        return alexa_resp(speech, 'Stream Live')
    else:
        speech = 'No, {} is not currently streaming.'.format(PHONETIC)
        return alexa_resp(speech, 'Stream Offline')


def lambda_handler(event, context):
    try:
        logger.info(event)
        intent = event['request']['intent']['name']
        if intent == 'Streaming':
            return check_live(event)
        else:
            raise ValueError('Unknown Intent')
    except Exception as error:
        logger.exception(error)
        return alexa_resp('Error. {}'.format(error), 'Error')
