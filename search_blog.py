import json
import requests
from helpers import *

def search_blog(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.
    """
    query = intent_request['currentIntent']['slots']['HelpTopic']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    api_endpoint = "https://blog.mmediagroup.fr/wp-json/wp/v2/posts"
    data = {
        '_embed': 1,
        'search': query,
        # 34 is the Help Center category
        'parent_category': 34,
        'orderby': 'relevance'
    }
    
    result = requests.get(url = api_endpoint, params = data).json()

    data_to_return = {
        'contentType': 'PlainText',
        'content': '{} - More info on "{}" can be found on our Help Center: {}'.format(strip_tags(result[0]['excerpt']['rendered']), query, result[0]['link'])
    }

    if intent_request['outputDialogMode'] == "Voice" or ('contact_source' in output_session_attributes and output_session_attributes['contact_source'] == "call"):
        data_to_return = {
            'contentType': 'SSML',
            'content': '<speak>{}. More info on can be found on our online Help Center.</speak>'.format(strip_tags(result[0]['excerpt']['rendered'].replace("https://","")))
        }

    return close(
        output_session_attributes,
        'Fulfilled',
        data_to_return
    )
