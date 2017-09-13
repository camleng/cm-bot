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

    return 'OK', 200


def log(data: str) -> None:
    message = '{name} - {text}'.format_map(data)
    bot.post_to_slack(message)
    

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001)
