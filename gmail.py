"""Helper functions for parsing the email from ministry@ipfw.edu
that contains the meeting location
"""

import base64
from datetime import datetime as dt
import os
import re
import httplib2

from apiclient import discovery, errors
from oauth2client import client, tools
from oauth2client.file import Storage
from bs4 import BeautifulSoup


def _list_messages_matching_query(service, user_id, query=''):
    """Uses the Gmail API to list messages matching the given query
    """
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
    """Uses the Gmail API to extract the header from the message
    and parse it for the date the email was sent.
    """

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
        print(f'An error occurred: {error}')


def _get_message(service, user_id, msg_id):
    """Uses the Gmail API to extract the encoded text from the message
    and decodes it to make it readable and searchable
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_str = str(base64.urlsafe_b64decode(message['raw'].encode('ASCII')))

        return msg_str
    except errors.HttpError as error:
        print(f'An error occurred: {error}')


def _get_credentials():
    """Gets stored oauth2 credentials
    """

    scopes = 'https://www.googleapis.com/auth.gmail.readonly'
    client_secret_file = 'client_secret.json'
    application_name = 'GroupMe Bot'

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'groupme-bot.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(credential_dir, client_secret_file), scopes)
        flow.user_agent = application_name 
        credentials = tools.run_flow(flow, store)
        print(f'Storing credentials to {credential_path}')
    return credentials


def _find_room(soup):
    """Finds the building and room number of the meeting
    """
    # remove unnecessary formatting
    text = soup.text.replace('=', '').replace('\\r', '').replace('\\n', '').lower()

    # find the building and room number of the meeting
    pattern = re.compile(r"""
    student
    \s*
    leader
    s? # optional plural
    \s*
    meeting:
    \s*
    monday, # day of the week
    \s*
    \w+ # month
    \s*
    \d\d? # day, optionally 1 digit
    \w+, # day ending ('st', 'th')
    \s*
    (?:\w+|\d+) # starting time (noon or 12)
    -
    1(?::00)? # ending time (1 or 1:00)
    \s*
    p\.?m\.?, # 'pm' or 'p.m.'
    \s*
    (liberal\s*arts|l\.a\.|walb) # building
    \s*
    \w*, # extra info such as 'union' after 'walb'
    \s*
    room
    \s*
    (
    [g-]* # optional ground floor and hyphen ('G08', 'G-21')
    \d{2}\d? # room number, max of 3 digits
    )
    """, re.X)
    match = re.search(pattern, text)

    # check for success
    if match:
        building, room = match.groups()
        # format results
        if building in ['liberal arts', 'l.a.']:
            building = 'LA'
        else:
            building = building.capitalize()

        return building, room.capitalize()
    else:
        return None, None

def _verify_date(ext_date):
    """Makes sure that the date of the email matches today's date
    """
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
    """Finds the room number and building of the meeting location
    """
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
    if _verify_date(date) and building and room:
        _mark_as_sent()
        return building, room
    else:
        print('No meeting today')
        return None, None

current_dir = os.path.dirname(__file__)
credential_dir = os.path.join(current_dir, '.credentials')
status_file = os.path.join(current_dir, '.status')
