#!/usr/bin/env python3


import requests
import gmail


base_url = 'https://api.groupme.com/v3'

access_token = '6d9ab8c07df50133342e1546f031de51'

test_group_id = 18344199

room = gmail.find_room()

message = 'Today\'s meeting will be held in Walb %s' % room

bot_id = 'eac5909e675c05af67a1e2c755'
payload = {'bot_id': bot_id, 'text': message}
requests.post('%s/bots/post' % base_url, data=payload)
