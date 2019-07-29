import logging
from alexa import alexa_resp
from helix import Twitch
from settings import Settings

config = Settings()
logger = logging.getLogger('app')
logger.setLevel(logging.getLevelName(config.log_level))


def lambda_handler(event, context):
    try:
        logger.info(event)
        intent = event['request']['intent']['name']
        if intent == 'Streaming':
            return check_live()
        elif intent == 'Followers':
            return check_followers()
        else:
            raise ValueError('Unknown Intent')
    except Exception as error:
        logger.exception(error)
        return alexa_resp('Error. {}'.format(error), 'Error')


def check_followers():
    twitch = Twitch(config.user_id, config.client_id)
    speech = '{} currently has {} followers.'.format(config.phonetic_name, twitch.get_followers())
    return alexa_resp(speech, 'Total Followers')


def check_live():
    twitch = Twitch(config.user_id, config.client_id)
    if twitch.is_live():
        speech = 'Yes {} has been streaming for {}.'.format(config.phonetic_name, twitch.get_uptime())
        return alexa_resp(speech, 'Stream Live')
    else:
        speech = 'Sorry {} is not currently streaming.'.format(config.phonetic_name)
        return alexa_resp(speech, 'Stream Offline')
