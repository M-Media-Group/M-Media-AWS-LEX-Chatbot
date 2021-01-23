import json
import requests
import os
from helpers import *

def handover_to_facebook(profile_id):
    api_endpoint = "https://graph.facebook.com/v9.0/me/pass_thread_control?access_token="+os.environ['facebook_page_access_token']

    data = {
        "recipient": {
            "id": profile_id
        },
        "target_app_id": 263902037430900
    }

    r = requests.post(url = api_endpoint, json = data).json()
    logger.debug(r)
    return r
    
def handover(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.
    """
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['currentIntent']['slots']
        return delegate(output_session_attributes, slots)

    # Book the appointment.  In a real bot, this would likely involve a call to a backend service.
    if 'x-amz-lex:channel-type' in intent_request['requestAttributes'] and intent_request['requestAttributes']['x-amz-lex:channel-type'] == 'Facebook':
        facebook_user_id = intent_request['requestAttributes']['x-amz-lex:user-id']
        handover_to_facebook(facebook_user_id)
        return close(
            output_session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Okay, I am getting a human online. Messages you send from now on will go to our support team.'
            }
        )
    elif ('contact_source' in output_session_attributes and output_session_attributes['contact_source'] == "call"):
        return close(
            output_session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Okay, please hold while I try to get a human on the line.'
            }
        )
    return close(
            output_session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'I can not get ahold of anyone right now. Please try again later.'
            }
        )
