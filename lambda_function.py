import logging
from alexa import alexa_resp
from settings import Settings
from twitch import Twitch

logger = logging.getLogger()
logger.setLevel(logging.INFO)

config = Settings()


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


def check_live():
    twitch = Twitch(config.user_id)
    if twitch.is_live():
        speech = 'Yes, {} has been streaming for {}.'.format(
            config.phonetic, twitch.get_uptime()
        )
        return alexa_resp(speech, 'Stream Live')
    else:
        speech = 'No, {} is not currently streaming.'.format(config.phonetic)
        return alexa_resp(speech, 'Stream Offline')
