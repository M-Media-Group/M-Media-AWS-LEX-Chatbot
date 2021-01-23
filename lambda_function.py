import json
import time
import os
import logging
from intents.search_blog import search_blog
from intents.make_appointment import make_appointment
from intents.handover_to_human import handover

from helpers import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    logger.debug('dispatch userId={}, intentName={}'.format(event['userId'], event['currentIntent']['name']))
    intent_name = event['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == 'MakeAppointment':
        return make_appointment(event)
    elif intent_name == 'GetBlogHelpCenterPost':
        return search_blog(event)
    elif intent_name == 'GetHumanAgent':
        return handover(event)
    raise Exception('Intent with name ' + intent_name + ' not supported')
