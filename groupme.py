#!/usr/bin/env python3

import sys
import argparse

import urllib3
import certifi
import gmail


def post(payload):
    """POST the payload to send the message
    This method uses SSL certification verification through certifi
    """
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    http.request('POST', '{https://api.groupme.com/v3/bots/post', fields=payload)


def parse_args():
    """Parse the command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--last', action='store_true', help='View the location of the last meeting')
    args = parser.parse_args()

    if args.last:
        print(gmail.last_location(formatted=True))
        sys.exit() 


if __name__ == '__main__':
    parse_args()

    base_url = ''
    bot_id = ''  # CM Bot for Student Leaders
    location = gmail.find_location()

    if location:
        message = "Today's meeting will be held in {building} {room}".format_map(location)
        payload = dict(bot_id=bot_id, text=message)
        post(base_url, payload)
    else:
        print('No meeting today')
        print(gmail.last_location(formatted=True))
 
