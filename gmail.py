"""Helper functions for parsing the email from ministry@ipfw.edu
that contains the meeting location
"""

import base64
from datetime import datetime as dt, timedelta
import os
import re
import sys

import httplib2
from apiclient import discovery, errors
from oauth2client import client, tools
from oauth2client.file import Storage
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query


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
    for header in headers: 
        if header['name'] == 'Date':
            day, month, year = header['value'].split()[1:4]

            # pad day with a '0' if necessary
            if len(day) == 1:
                day = '0' + day

            date = {'year': year, 'month': month, 'day': day}

            return date
    return None


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
    \w+                            # day ending ('st', 'th')
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

def _verify_date(date, meeting_type):
    """Makes sure that the date of the email matches today's date
    """
    today = dt.today()

    if meeting_type == 'student_leader':
        month, day = today.strftime('%b %d').split()
        today_date = {'month': month, 'day': day}
        return today_date == date

    elif meeting_type == 'conversations':
        wed = date + timedelta(days=2)
        return today.date() == wed.date()
        

def pizza_night(date):
    weekday, day = [int(x) for x in dt.today().strftime('%w %d').split()]
    return weekday == 3 and day - 7 <= 0


def clear_status():
    db.update({'status': ''}, (q.type == 'student_leader') | (q.type == 'conversations'))


def _message_sent_today(meeting_type):
    return db.contains((q.type == meeting_type) & (q.status == 'sent'))


def _mark_as_sent(meeting_type):
    db.update({'status': 'sent'}, q.type == meeting_type)


def _save_location(location, meeting_type):
    """Saves the location of the last meeting
    """
    # separate the datetime object in location to be a year, month, and day
    location['date'] = dict(zip(['year', 'month', 'day'], location['date'].strftime('%Y %b %d').split()))
    db.update(location, q.type == meeting_type)


def last_location(meeting_type, formatted=False):
    """Returns the last meeting location
    """
    location = db.get(q.type == meeting_type)
     
    if location:
        if formatted:
            if not location['building'] and not location['room']:
                return 'There was no meeting on {date[month]} {date[day]}'.format_map(location)
            return 'The {date[month]} {date[day]} meeting was held in {building} {room}'.format_map(location)
        else:
            return location


def _find_conversations_meeting(message, headers):
    """Finds the location of the conversations meeting
    """
    building, room = _find_cv_room(message)

    date = _find_date(headers)
    # only post a message in the GroupMe conversation if there is a meeting today 
    if _verify_date(date, 'conversations') and building and room:
        _mark_as_sent('conversations')
        location = {'building': building, 'room': room, 'date': date, 'status': ''}
        _save_location(location, 'student_leader')
        return location
    else:
        return None


    return {'building': building, 'room': room}


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
    if _verify_date(date, 'student_leader') and building and room:
        _mark_as_sent()
        location = {'building': building, 'room': room, 'date': date, 'status': ''}
        _save_location(location, 'student_leader')
        return location
    else:
        return None


def find_location(meeting_type):
    exit_early = False
    if _message_sent_today(meeting_type):
        print('Message already sent')
        exit_early = True

    day = dt.today().strftime('%A')
    if meeting_type == 'student_leader' and day != 'Monday':
        print('No Student Leader meeting today')
        exit_early = True

    if meeting_type == 'conversations' and day != 'Wednesday':
        print('No Conversations meeting today')
        exit_early = True
     
    if exit_early:
        location = last_location(meeting_type, formatted=True)
        if location:
            print(location)
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
db = TinyDB('db.json')
q = Query()
