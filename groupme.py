#!/usr/bin/env python3

import requests
import gmail


def post(payload):
    requests.post('%s/bots/post' % base_url, data=payload)


if __name__ == '__main__':
    base_url = 'https://api.groupme.com/v3'
    bot_id = 'eac5909e675c05af67a1e2c755'

    room = gmail.find_room()
    if room:
        message = 'Today\'s meeting will be held in Walb %s' % room
        payload = {'bot_id': bot_id, 'text': message}
        post(payload)
