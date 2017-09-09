from datetime import datetime as dt
import json

from flask import Flask, request
from cmbot import CMBot

app = Flask(__name__)
bot = CMBot()

@app.route('/', methods=['POST'])
def parse():
    data = request.get_json()

    log(data)
    
    if data['sender_id'] == '365443':
        return 'Bot sent message\n'

    today = dt.today()

    text = data['text'].lower()
    if 'where is the student leader meeting' in text:
        if today.strftime('%A') == 'Monday' and today.hour < 13:
            location = gmail.find_location()
            if location:
                message = "Today's Student Leader meeting will be held in {building} {room}".format_map(location)
                groupme.post({'bot_id': groupme.bot_id, 'text': message})

        else:
            location = gmail.last_location(formatted=True)
            groupme.post({'bot_id': groupme.bot_id, 'text': location})

        return location + '\n'

    elif 'where is the conversations meeting' in text:
        if int(today.strftime('%w')) <= 3 and today.hour < 21:
            location = gmail.find_location(meeting_type='conversations')
            if location:
                if location['room'] == 'Classic Ballroom':
                    message = "The Conversations meeting will be held downstairs in the Walb Classic Ballroom"
                elif location['room'] == '222-226':
                    message = "The Conversations meeting will be held upstairs in rooms 222-226"
                groupme.post({'bot_id': groupme.bot_id, 'text': message})

        else:
            location = gmail.last_location(meeting_type='conversations', formatted=True)
            groupme.post({'bot_id': groupme.bot_id, 'text': location})

        return location + '\n'


    else:
        return 'No meeting location found\n'

def log(data):
    timestamp = dt.today().strftime('%b %d %H:%M:%S')
    entry = f"[{timestamp}] {data['name']}: {data['text']}\n"
    try:
        with open('chat.log', 'a') as f:
            f.write(entry)
 

if __name__ == '__main__':
    app.run(host='10.0.0.25')
