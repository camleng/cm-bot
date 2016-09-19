import base64
from datetime import datetime as dt
import os
import re
import json
import pickle

import httplib2
import oauth2client
from apiclient import discovery
from apiclient import errors
from bs4 import BeautifulSoup


def _list_messages_matching_query(service, user_id, query=''):
    '''Uses the Gmail API to list messages matching the given query
    '''
    response = service.users().messages().list(userId=user_id, q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    # build list of messages
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages


def _find_date(service, user_id, msg_id):
    '''This method uses the Gmail API to extract the header from the message and parse it for the date the email was sent.
    '''

    # date is formatted [month, day]
    date = []

    # extract date from email headers
    try:
        response = service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
        headers = response['payload']['headers']
        for header in headers:
            if header['name'] == 'Date':
                day, month = header['value'].split()[1:3]
                # pad day with 0's if necessary
                if len(day) == 1:
                    day = '0' + day
                date = [month, day]
        return date
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def _get_message(service, user_id, msg_id):
    """This method uses the Gmail API to extract the encoded text from the message and decodes it to make it readable and searchable
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_str = str(base64.urlsafe_b64decode(message['raw'].encode('ASCII')))

        return msg_str
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def _get_credentials():
    '''Gets stored oauth2 credentials
    '''
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail_auth.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    return credentials


def _find_room(soup):
    '''Finds the building and room number of the meeting
    '''

    # remove unnecessary formatting
    text = soup.text.replace('=', '').replace('\\r', '').replace('\\n', '').lower()
    
    # find the building and room number of the meeting
    pattern = 'student\s*leaders?\s*meeting:\s*monday,\s*\w+\s*\d\d?\w+,\s*(?:\w+|\d+)-1(?::00)?\s*p\.?m\.?,\s*(liberal\s*arts|l\.a\.|walb)\s*\w*,\s*room\s*(g?-?\d{2}\d?)'
    match = re.search(pattern, text)
    # check for success
    if match:
        building, room = match.groups()
        # format results
        if building in ['liberal arts', 'l.a.']:
            bulding = 'LA'
        else:
            building = building.capitalize()
        return building, room.capitalize()
    else:
        return None, None

def _verify_date(ext_date):
    '''Makes sure that the date of the email matches today's date
    '''
    # today_day = dt.datetime.today().strftime('%d')
    # today_month = dt.datetime.today().strftime('%b')
    # today = [today_month, today_day]
    today = dt.today().strftime('%b %d').split()
    if today == ext_date:
        return True
    return False


def _message_sent_today():
    try:
        with open(status_file) as infile:
            if 'sent' in infile:
                return True
        return False
    except Exception:
        open(status_file, 'w').close()
        return False

def _mark_as_sent():
    with open(status_file, 'w') as outfile:
        outfile.write('sent')


def find_room():
    if _message_sent_today():
        print('Message already sent')
        return None, None

    # authorize with oauth2
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    user_id = 'me'
    query = 'subject:spiritual cyber-vitamin'

    # get recent messages matching the query
    messages = _list_messages_matching_query(service, user_id, query)

    # get the latest message id from the list
    last_message_id = messages[0]['id']

    # get the message headers
    message = _get_message(service, user_id, last_message_id)

    # create BeautifulSoup object to help parse the returned html
    soup = BeautifulSoup(message, 'html.parser')

    building, room = _find_room(soup)

    date = _find_date(service, user_id, last_message_id)

    # we don't want to post a message if there is no meeting today
    if _verify_date(date):
        _mark_as_sent()
        return building, room
    else:
        print('No meeting today')
        return None, None

    return building, room

current_dir = os.path.dirname(__file__)
credential_dir = os.path.join(current_dir, '.credentials')
status_file = os.path.join(current_dir, '.status')
