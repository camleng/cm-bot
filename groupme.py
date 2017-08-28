#!/usr/bin/env python

import sys
import argparse

import urllib3
import certifi
import gmail


bot_id = ''  # CM Bot for Student Leaders

def post(payload):
    """POST the payload to send the message
    Uses SSL certification verification through certifi
    """
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    http.request('POST', 'https://api.groupme.com/v3/bots/post', fields=payload)


def parse_args():
    """Parse the command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--last', action='store_true', help='View the location of the last meeting. Used in conjunction with -s or -c')
    parser.add_argument('-s', '--student-leader', action='store_true', help='Get the location of the Student Leader meeting. Use with -l to show the last location.')
    parser.add_argument('-c', '--conversations', action='store_true', help='Get the location of the Conversations meeting. Use with -l to show the last location.')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Do not send message to GroupMe--just show what would be sent')
    parser.add_argument('--clear', action='store_true', help='Clears the status file')
    args = parser.parse_args()

    return args


def get_meeting_type(args):
    return 'conversations' if args.conversations else 'student_leader'


def print_last_location():
    location = gmail.last_location(meeting_type, sentence=True)
    if location:
        print(location)
    sys.exit()


def build_message(location):
    if location['room'] == 'Classic Ballroom':
        message = "Today's Conversations meeting will be held downstairs in the Walb Classic Ballroom."
    elif location['room'] == '222-226':
        message = "Today's Conversations meeting will be held upstairs in rooms 222-226."
    return message


def pizza_night_message(location):
    return ' Pizza tonight!' if gmail.pizza_night(location['date']) else ''


def get_student_leader_meeting_location():
    location = gmail.find_location('student_leader')
    message = ''
    if location:
        message = "Today's Student Leader meeting will be held in {building} {room}.".format_map(location)
    return location, message


def get_conversations_meeting_location():
    location = gmail.find_location('conversations')
    message = ''
    if location:
        message = build_message(location)
        message += pizza_night_message(location)
    return location, message


if __name__ == '__main__':
    args = parse_args()
    meeting_type = get_meeting_type(args)

    if args.last:
        print_last_location()

    if args.clear:
        # clear the status file
        gmail.clear_status()
        sys.exit()

    if args.conversations:
        location, message = get_conversations_meeting_location()
    else:
        location, message = get_student_leader_meeting_location()

    if location:
        # if location exists
        if args.dry_run:
            print(message)
        else:
            payload = {'bot_id': bot_id, 'text': message}
            post(payload)
            gmail.mark_as_sent(meeting_type)
    else:
        print('No meeting today')
        print_last_location()
