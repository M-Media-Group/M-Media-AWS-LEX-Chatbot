import json
import requests
import os
from helpers import *

def validate_book_appointment(email, name, surname, message):
    if email:
        if not "@" in email:
            return build_validation_result(False, 'Email', 'I did not understand that, what is your email?')

    if name:
        if len(name) <= 1:
            return build_validation_result(False, 'Name', 'I did not understand that, what is your first name?')

    if surname:
        if len(surname) <= 1:
            return build_validation_result(False, 'Surname', 'I did not understand that, what is your surname name?')

    if message and len(message) <= 10 or message == "" or message == "null":
            # logger.debug("SHOULD FAIL")
            return build_validation_result(False, 'Message', 'I did not understand that, what is your message?')

    return build_validation_result(True, None, None)

def get_facebook_profile(profile_id):
    api_endpoint = "https://graph.facebook.com/v9.0/"+str(profile_id)+"/"
    data = {
        'access_token': os.environ['facebook_page_access_token'],
        'fields': 'first_name,last_name,email'
    }

    return requests.get(url = api_endpoint, params = data).json()

def make_appointment(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    email = output_session_attributes['Email'] if 'Email' in output_session_attributes else intent_request['currentIntent']['slots']['Email']
    name = output_session_attributes['Name'] if 'Name' in output_session_attributes else intent_request['currentIntent']['slots']['Name']
    surname = output_session_attributes['Surname'] if 'Surname' in output_session_attributes else intent_request['currentIntent']['slots']['Surname']
    facebook_user_id = ""
    if 'requestAttributes' in intent_request:
        if intent_request['requestAttributes'] and 'x-amz-lex:user-id' in intent_request['requestAttributes'] and 'fetched_facebook_data' not in output_session_attributes:
            facebook_user_id = intent_request['requestAttributes']['x-amz-lex:user-id']
            facebook_profile = get_facebook_profile(facebook_user_id)
            # logger.debug(facebook_profile)
            output_session_attributes['fetched_facebook_data'] = True
            if not name and facebook_profile['first_name']:
                name = facebook_profile['first_name']
                output_session_attributes['Name'] = name
            if not surname and facebook_profile['last_name']:
                surname = facebook_profile['last_name']
                output_session_attributes['Surname'] = surname

    message = ""
    if 'Message' in intent_request['currentIntent']['slots']:
        message = intent_request['currentIntent']['slots']['Message']
    source = intent_request['invocationSource']
    booking_map = json.loads(try_ex(lambda: output_session_attributes['bookingMap']) or '{}')

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['currentIntent']['slots']
        validation_result = validate_book_appointment(email, name, surname, message)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                build_response_card(
                    'Specify {}'.format(validation_result['violatedSlot']),
                    validation_result['message']['content'],
                    build_options(validation_result['violatedSlot'], appointment_type, booking_map)
                )
            )

        if not email:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Email',
                {'contentType': 'PlainText', 'content': 'What is your email?'},
                None
            )
        else:
            output_session_attributes['Email'] = email

        if not name:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Name',
                {'contentType': 'PlainText', 'content': 'What is your name?'},
                None
            )
        else:
            output_session_attributes['Name'] = name
    
        if not surname:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Surname',
                {'contentType': 'PlainText', 'content': 'What is your surname?'},
                None
            )
        else:
            output_session_attributes['Surname'] = surname

        if not message:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Message',
                {'contentType': 'PlainText', 'content': 'What is your message?'},
                None
            )

        return delegate(output_session_attributes, slots)

    # Book the appointment.  In a real bot, this would likely involve a call to a backend service.
    
    api_endpoint = "https://mmediagroup.fr/api/contact"
    data = {
        'name': name,
        'surname': surname,
        'email': email,
        'phone': None,
        'message': message
    }
    
    requests.post(url = api_endpoint, data = data, allow_redirects=False, verify=False)
    
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Okay, I have booked your appointment.  We will be in touch on your email {}. See you soon, {}'.format(email, name)
        }
    )
