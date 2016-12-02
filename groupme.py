#!/usr/bin/env python3

import sys
import argparse

import urllib3
import certifi
import gmail


bot_id = '4c2c8f3d6a387d16f818c8fe88'  # CM Bot for Student Leaders

def post(payload):
    """POST the payload to send the message
    This method uses SSL certification verification through certifi
    """
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    http.request('POST', 'https://api.groupme.com/v3/bots/post', fields=payload)


def parse_args():
    """Parse the command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--last', action='store_true', help='View the location of the last meeting')
    parser.add_argument('-s', '--student-leader', action='store_true', help='Get the location of the Student Leader meeting')
    parser.add_argument('-c', '--conversations', action='store_true', help='Get the location of the Conversations meeting')
    parser.add_argument('--clear', action='store_true', help='Clears the status file')

    args = parser.parse_args()

    return args
    
if __name__ == '__main__':
    args = parse_args()

    meeting_type = 'conversations' if args.conversations else 'student_leader'

    if args.last:
        print(gmail.last_location(meeting_type=meeting_type, formatted=True))
        sys.exit() 

    if args.clear:
        gmail.clear_status()
        sys.exit()

    if args.conversations:
        location = gmail.find_location(meeting_type='conversations')
        if location:
            if location['room'] == 'Classic Ballroom':
                message = "Today's Conversations meeting will be held downstairs in the Walb Classic Ballroom"
            elif location['room'] == '222-226':
                message = "Today's Conversations meeting will be held upstairs in rooms 222-226"

    else:
        location = gmail.find_location()
        if location:
            message = "Today's Student Leader meeting will be held in {building} {room}".format_map(location)


    if location:
        payload = dict(bot_id=bot_id, text=message)
        post(payload)
    else:
        print('No meeting today')
        print(gmail.last_location(meeting_type=meeting_type, formatted=True))
 
