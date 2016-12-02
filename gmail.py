"""Helper functions for parsing the email from ministry@ipfw.edu
that contains the meeting location
"""

import pickle
import base64
from datetime import datetime as dt, timedelta
import os
import re
import sys
import json

import httplib2
from apiclient import discovery, errors
from oauth2client import client, tools
from oauth2client.file import Storage
from bs4 import BeautifulSoup


def _get_last_message_id(service, user_id, query=''):
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

    return messages[0]['id']


def _find_date(headers):
    """Uses the Gmail API to extract the header from the message
    and parse it for the date the email was sent.
    """
    # extract date from email headers
    try:
        for header in headers: 
            if header['name'] == 'Date':
                day, month = header['value'].split()[1:3]

                # pad day with a '0' if necessary
                if len(day) == 1:
                    day = '0' + day

                return dict(month=month, day=day)
        return None
    except errors.HttpError as error:
        print(f'An error occurred: {error}')


def _get_message_info(service, user_id, msg_id):
    """Uses the Gmail API to extract the encoded text from the message
    and decodes it to make it readable and searchable
    """
    try:
        enc_message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        message = str(base64.urlsafe_b64decode(enc_message['raw']), 'utf-8')
        message = message.replace('=\r\n', '').replace('=22', '"').replace('=46', 'F').lower()
        message = BeautifulSoup(message, 'html.parser').text
        response = service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
        headers = response['payload']['headers']

        return message, headers
    except errors.HttpError as error:
        print(f'An error occurred: {error}')


def _get_credentials():
    """Gets stored oauth2 credentials
    """
    scopes = 'https://www.googleapis.com/auth/gmail.readonly'
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


def _find_sl_room(message):
    """Finds the building and room number of the meeting
    """
    pattern = re.compile("""
    student
    \s*
    leader
    s?                             # optional plural
    \s*
    meeting:
    \s*
    monday,                        # day of the week
    \s*
    \w+                            # month
    \s*
    \d\d?                          # day, optionally 1 digit
    \w+,                           # day ending ('st', 'th')
    ,?                             # optional comma
    \s*
    (?:\w+|\d+)                    # starting time (noon or 12)
    \s*
    -
    \s*
    1(?::00)?                      # ending time (1 or 1:00)
    \s*
    p\.?m\.?,                      # 'pm' or 'p.m.'
    \s*
    (liberal\s*arts|l\.a\.|walb)   # building
    \s*
    \w*                            # extra info such as 'union' after 'walb'
    \s*
    \w*,
    \s*
    room
    \s*
    (
    [g-]*                          # optional ground floor and hyphen ('G08', 'G-21')
    \d{2}\d?                       # room number, max of 3 digits
    )
    """, re.X)
    match = re.search(pattern, message)

    # check for success
    if match and len(match.groups()) == 2:
        building, room = match.groups()
        # format results
        if building in ['liberal arts', 'l.a.']:
            building = 'LA'
        else:
            building = building.capitalize()

        return building, room.capitalize()
    else:
        return None, None

def _verify_date(date, meeting_type='student_leader'):
    """Makes sure that the date of the email matches today's date
    """
    month, day = dt.today().strftime('%b %d').split()
    today = dict(month=month, day=day)

    if meeting_type == 'student_leader':
        return today == date

    elif meeting_type == 'conversations':
         month, day = (dt.today() + timedelta(days=2)).strftime('%b %d').split()
         wed = dict(month=month, day=day)
         return today == wed


def clear_status():
    with open(status_file, 'w') as f:
        f.write(json.dumps(dict(student_leader='', conversations=''), indent=4))
        
def _message_sent_today(meeting_type='student_leader'):
    try:
        status = {}
        with open(status_file) as f:
            status = json.loads(f.read())
            return status[meeting_type] == 'sent'
    except FileNotFoundError:
        with open(status_file, 'w') as f:
            status = dict(student_leader='', conversations='')
            f.write(json.dumps(status, indent=4))
        return False


def _mark_as_sent(meeting_type):
    status = {}
    with open(status_file) as f:
       status = json.loads(f.read()) 
    with open(status_file, 'w') as f:
        status[meeting_type] = 'sent'
        f.write(json.dumps(status, indent=4))
        

def _save_location(location, meeting_type='student_leader'):
    """Saves the location of the last meeting
    """
    last = last_location(meeting_type='both')
    last[meeting_type] = location

    with open('location.json', 'w') as f:
        f.write(json.dumps(last, indent=4))

    return json.dumps(last, indent=4)


def last_location(meeting_type='student_leader', formatted=False):
    """Returns the last meeting location
    """
    filename = os.path.join(os.path.dirname(__file__), 'location.json')
    try:
        with open(filename) as f:
            location = json.loads(f.read())
            if meeting_type != 'both':
                location = location[meeting_type]
            
            if formatted:
                if not location['building'] and not location['room']:
                    return 'There was no meeting on {date[month]} {date[day]}'.format_map(location)
                return 'The {date[month]} {date[day]} meeting was held in {building} {room}'.format_map(location)
            else:
                return location
    except FileNotFoundError:
        print('No location found')


def _find_conversations_meeting(message, headers):
    """Finds the location of the conversations meeting
    """
    building, room = _find_cv_room(message)

    date = _find_date(headers)
    # only post a message in the GroupMe conversation if there is a meeting today 
    if _verify_date(date, meeting_type='conversations') and building and room:
        # if building and room:
        _mark_as_sent(meeting_type='conversations')
        location = dict(building=building, room=room, date=date)
        _save_location(location)
        return location
    else:
        return None


    return dict(building=building, room=room)

def _find_cv_room(message):
    """Finds the building and room number of the meeting
    """
    # remove unnecessary formatting
    message = message.replace('=\r\n', '').replace('\r\n>', '')\
            .replace('=22', '"').replace('=46', 'F').lower()

    # find the building and room number of the meeting
    pattern = re.compile("""
    cm
    \s*
    "conversations"
    \s*
    meeting:
    \s*
    wednesday         # day of the week
    ,?
    \s*
    \w+               # month
    \s*
    \d\d?             # day, optionally 1 digit
    \w+?              # optional day ending ('st', 'nd', 'th')
    ,?
    \s*
    7(?::00)?         # starting time (7 or 7:30)
    -
    8:30              # ending time
    \s*
    p.?m.?,?          # 'pm' or 'p.m.'
    \s*
    (?:ipfw's\s*)?    # "IPFW's" Walb Class Ballroom
    (walb)            # building (always Walb)
    ,?
    .*
    (222|ballroom)""", re.X)
    match = pattern.search(message)

    # check for success
    if match and len(match.groups()) == 2:
        building, room = match.groups()
        # format results
        if room == 'ballroom':
            room = 'Classic Ballroom'
        elif room == '222':
            room = '222-226'
        return building.capitalize(), room

    else:
        return None, None

     

def _find_student_leader_meeting(message, headers):
    """Finds the location of the student leader meeting
    """
    # find the building and the room from the email
    building, room = _find_sl_room(message)

    # find the date in the email headers
    date = _find_date(headers)

    # only post a message in the GroupMe conversation if there is a meeting today 
    if _verify_date(date) and building and room:
        # if building and room:
        _mark_as_sent(meeting_type='student_leader')
        location = dict(building=building, room=room, date=date)
        _save_location(location)
        return location
    else:
        return None


def find_location(meeting_type='student_leader'):
    if _message_sent_today(meeting_type):
        print('Message already sent')
        print(last_location(meeting_type, formatted=True)) 
        sys.exit()

    # authorize with oauth2
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # 'me' is shorthand for the current user
    user_id = 'me'

    # gmail query to find the relevant emails
    query = 'subject:spiritual cyber-vitamin'

    # get the message id from the last email 
    last_message_id = _get_last_message_id(service, user_id, query)

    # get the formatted message and headers 
    message, headers = _get_message_info(service, user_id, last_message_id)

    if meeting_type == 'student_leader':
        return _find_student_leader_meeting(message, headers)    

    elif meeting_type == 'conversations':
        return _find_conversations_meeting(message, headers)


current_dir = os.path.dirname(__file__)
credential_dir = os.path.join(current_dir, '.credentials')
status_file = os.path.join(current_dir, '.status')
