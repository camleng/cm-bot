#!/usr/bin/env python3

import sys
import argparse

import requests
import gmail


def post(base_url, payload):
    """POST the payload to send the message
    """
    requests.post(f'{base_url}/bots/post', data=payload)


def parse_args():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--last', action='store_true', help='View the location of the last meeting')
    args = parser.parse_args()

    if args.last:
        print(gmail.last_location(formatted=True))
        sys.exit() 


if __name__ == '__main__':
    parse_args()

    base_url = 'https://api.groupme.com/v3'
    bot_id = 'fd5961d86f878c3539401edae2'    # Test Bot for Bot Test
    # bot_id = 'eac5909e675c05af67a1e2c755'  # CM Bot for Student Leaders
    location  = gmail.find_location()

    if location:
        message = "Today's meeting will be held in {building} {room}".format_map(location)
        payload = dict(bot_id=bot_id, text=message)
        post(base_url, payload)
    else:
        print('No meeting today')
        print(gmail.last_location(formatted=True))
 
