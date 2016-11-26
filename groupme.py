#!/usr/bin/env python3

import gmail
import requests
import sys

if '--last' in sys.argv:
    location = gmail.last_location(formatted=True)
    print(location)
    sys.exit() 

def post(base_url, payload):
    """POST the payload to send the message
    """
    requests.post(f'{base_url}/bots/post', data=payload)


if __name__ == '__main__':
    base_url = 'https://api.groupme.com/v3'
    # bot_id = 'fd5961d86f878c3539401edae2'    # Test Bot for Bot Test
    bot_id = 'eac5909e675c05af67a1e2c755'  # CM Bot for Student Leaders
    location  = gmail.find_location()

    if location:
        message = "Today's meeting will be held in {building} {room}".format_map(location)
        payload = dict(bot_id=bot_id, text=message)
        post(base_url, payload)
    else:
        print('No meeting today')
        print(gmail.last_location(formatted=True))
 
