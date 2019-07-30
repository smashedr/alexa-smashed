import os
from alexa import alexa_resp
from helix import Twitch


def lambda_handler(event, context):
    try:
        return LambdaHandler.process_intent(event)
    except Exception as error:
        return alexa_resp('Error. {}'.format(error), 'Error')


class LambdaHandler(object):
    user_id = os.environ.get('user_id')
    client_id = os.environ.get('client_id')
    phonetic_name = os.environ.get('phonetic_name')
    twitch = Twitch(user_id, client_id)

    @classmethod
    def process_intent(cls, event):
        return getattr(cls, event['request']['intent']['name'])()

    @classmethod
    def check_live(cls):
        if cls.twitch.is_live():
            speech = 'Yes {} has been streaming for {}.'.format(cls.phonetic_name, cls.twitch.get_uptime())
            return alexa_resp(speech, 'Stream Live')
        else:
            speech = 'Sorry {} is not currently streaming.'.format(cls.phonetic_name)
            return alexa_resp(speech, 'Stream Offline')

    @classmethod
    def check_followers(cls):
        speech = '{} currently has {} followers.'.format(cls.phonetic_name, cls.twitch.get_followers())
        return alexa_resp(speech, 'Total Followers')
