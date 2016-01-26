#!/usr/bin/env python3

import gmail
import requests


def post(base_url, payload):
    requests.post('%s/bots/post' % base_url, data=payload)


def main():
    base_url = 'https://api.groupme.com/v3'
    bot_id = 'fd5961d86f878c3539401edae2'  # Test Bot for Bot Test group
    # bot_id = 'eac5909e675c05af67a1e2c755'  # CM Bot for Student Leaders
    room = gmail.find_room()
    if room:
        message = 'Today\'s meeting will be held in Walb %s' % room
        payload = {'bot_id': bot_id, 'text': message}
        post(base_url, payload)


if __name__ == '__main__':
    main()
