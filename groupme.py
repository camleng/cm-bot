#!/usr/bin/env python3.6

import gmail
import requests


def post(base_url, payload):
    """POST the payload to send the message
    """
    requests.post('%s/bots/post' % base_url, data=payload)


if __name__ == '__main__':
    base_url = 'https://api.groupme.com/v3'
    # bot_id = 'fd5961d86f878c3539401edae2'    # Test Bot for Bot Test
    bot_id = 'eac5909e675c05af67a1e2c755'  # CM Bot for Student Leaders
    building, room = gmail.find_room()

    if building and room:
        message = f'Today\'s meeting will be held in {building} {room}'
        payload = {'bot_id': bot_id, 'text': message}
        post(base_url, payload)
