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
    parser.add_argument('-l', '--last', action='store_true', help='View the location of the last meeting')
    parser.add_argument('-s', '--student-leader', action='store_true', help='Get the location of the Student Leader meeting. Use with -l to show the last location.')
    parser.add_argument('-c', '--conversations', action='store_true', help='Get the location of the Conversations meeting. Use with -l to show the last location.')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Do not send message to GroupMe--just show what would be sent')
    parser.add_argument('--clear', action='store_true', help='Clears the status file')
    args = parser.parse_args()

    return args
    
if __name__ == '__main__':
    # parse the command line arguments
    args = parse_args()

    # set meeting type
    meeting_type = 'conversations' if args.conversations else 'student_leader'

    if args.last:
        # get last location 
        print(gmail.last_location(meeting_type, formatted=True))
        sys.exit() 

    if args.clear:
        # clear the status file
        gmail.clear_status()
        sys.exit()

    if args.conversations:
        # get Conversations meeting location
        location = gmail.find_location('conversations')
        if location:
            # build message and format the room
            if location['room'] == 'Classic Ballroom':
                message = "Today's Conversations meeting will be held downstairs in the Walb Classic Ballroom."
            elif location['room'] == '222-226':
                message = "Today's Conversations meeting will be held upstairs in rooms 222-226."
            
            # check if it's a pizza night
            if gmail.pizza_night(location['date']):
                message += " Pizza tonight!"
    else:
        # get Student Leader meeting location
        location = gmail.find_location('student_leader')
        if location:
            message = "Today's Student Leader meeting will be held in {building} {room}.".format_map(location)

    if location:
        # if location exists
        payload = {'bot_id': bot_id, 'text': message}
        if args.dry_run:
            print(message)
        else:
            post(payload)
    else:
        print('No meeting today')
        print(gmail.last_location(meeting_type, formatted=True))
 
