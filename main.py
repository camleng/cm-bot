from datetime import datetime as dt, timedelta
import argparse
import sys

from database import Database
from cmbot import CMBot

def parse_args():
    """Parse the command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--last', action='store_true', help='View the location of the last meeting. Used in conjunction with -s or -c')
    parser.add_argument('-s', '--student-leader', action='store_true', help='Get the location of the Student Leader meeting. Use with -l to show the last location.')
    parser.add_argument('-c', '--conversations', action='store_true', help='Get the location of the Conversations meeting. Use with -l to show the last location.')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Do not send message to GroupMe--just show what would be sent')
    parser.add_argument('--clear-sent', action='store_true', help='Clears the sent attribute in the database')
    args = parser.parse_args()

    return args


def get_meeting_type(args):
    return 'conversations' if args.conversations else 'student_leader'


def last_location():
    location = bot.last_location(meeting_type, sentence=True)
    return location if location else 'Sorry, I couldn\'t find a previous location'


def build_message(location):
    if location['room'] == 'Classic Ballroom':
        message = "Today's Conversations meeting will be held downstairs in the Walb Classic Ballroom."
    elif location['room'] == '222-226':
        message = "Today's Conversations meeting will be held upstairs in rooms 222-226."
    message += pizza_night_message(location)
    return message


def pizza_night_message(location):
    return ' Pizza tonight!' if bot.pizza_night(location['date']) else ''


def get_student_leader_meeting_location():
    location = bot.find_location('student_leader')
    message = "Today's Student Leader meeting will be held in {building} {room}.".format_map(location)
    return message


def get_conversations_meeting_location():
    location = bot.find_location('conversations')
    message = build_message(location)
    return message


if __name__ == '__main__':
    bot = CMBot()
    db = Database()
    args = parse_args()
    meeting_type = get_meeting_type(args)    

    if args.last:
        print(last_location())
        sys.exit()

    if args.clear_sent:
        db.clear_sent()
        sys.exit()

    try:
        if args.conversations:
            message = get_conversations_meeting_location()
        else:
            message = get_student_leader_meeting_location()

        if args.dry_run:
            print(message)
        else:
            bot.post(message)
            db.mark_as_sent(meeting_type)
    except Exception as e:
        print(e)
        sys.exit(1)
