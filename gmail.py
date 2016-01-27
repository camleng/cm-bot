import base64
import datetime as dt
import os
import re

import httplib2
import oauth2client
from apiclient import discovery
from apiclient import errors
from bs4 import BeautifulSoup


def _list_messages_matching_query(service, user_id, query=''):
    response = service.users().messages().list(userId=user_id, q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages


def _get_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_str = str(base64.urlsafe_b64decode(message['raw'].encode('ASCII')))

        return msg_str
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def _get_credentials():
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail_auth.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    return credentials


def _find_room(soup):
    ulists = soup.select('ul')

    for ul in ulists:
        text = ul.text.replace('=', '').replace('\\r', '').replace('\\n', '').lower()
        if 'student leader' in text:
            # find the list item with the Student Leader Meeting
            meeting_pattern = '[Ss]tudent [Ll]eaders? [Mm]eeting:.+[Rr]oom [Gg]?\d{2}\d?'
            matches = re.findall(meeting_pattern, text)
            if matches:
                # list of events -> 'Student Leader Meeting at'
                match = matches[0]
            else:
                return None

            # extract the room number
            room_pattern = '[Rr]oom [Gg]?\d{2}\d?'
            matches = re.findall(room_pattern, match)
            if matches:
                # ['Room 226'] -> '226'
                room = matches[0].split()[1]
                return room
            else:
                return None


def _find_date(soup):
    spans = soup.select('span')

    for span in spans:
        date_pattern = '.+day, .+ \d\d?, \d{4}'
        matches = re.findall(date_pattern, span.text)
        if matches:
            # ['Monday, December 7, 2015'], ... -> ['December', '7']
            date = matches[0].split(', ')[1].split()
            if len(date[1]) == 1:
                date[1] = '0' + str(date[1])
            return date


def _verify_date(ext_date):
    today_day = dt.datetime.today().strftime('%d')
    today_month = dt.datetime.today().strftime('%B')
    today = [today_month, today_day]
    if today == ext_date:
        return True
    return False


def _message_sent_today():
    with open(status_file) as infile:
        if 'sent' in infile:
            return True
    return False


def _mark_as_sent():
    with open(status_file, 'w') as outfile:
        outfile.write('sent')


def find_room():
    if _message_sent_today():
        print('Message already sent')
        return None

    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    user_id = 'me'
    query = 'subject:spiritual cyber-vitamin'

    messages = _list_messages_matching_query(service, user_id, query)
    last_message_id = messages[0]['id']

    message = _get_message(service, user_id, last_message_id)

    soup = BeautifulSoup(message, 'html.parser')

    room = _find_room(soup)

    date = _find_date(soup)

    if _verify_date(date):
        _mark_as_sent()
        return room
    else:
        print('No meeting today')
        return None


current_dir = os.path.dirname(__file__)
credential_dir = os.path.join(current_dir, '.credentials')
status_file = os.path.join(current_dir, '.status')
