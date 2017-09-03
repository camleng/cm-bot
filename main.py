from datetime import datetime as dt, timedelta
import argparse
import sys

from database import Database
from cmbot import CMBot


class Main:
    def __init__(self, args: dict):
        self.args = args
        self.bot = CMBot()
        self.db = Database()
        self.meeting_type = self.get_meeting_type(args)

    def get_meeting_type(self, args):
        return 'conversations' if self.args['conversations'] else 'student_leader'

    def last_location(self):
        location = self.bot.last_location(self, meeting_type, sentence=True)
        return location if location else 'Sorry, I couldn\'t find a previous location'

    def build_conversations_message(self, location):
        message = ''
        if location['room'] == 'Classic Ballroom':
            message = "Today's Conversations meeting will be held downstairs in the Walb Classic Ballroom."
        elif location['room'] == '222-226':
            message = "Today's Conversations meeting will be held upstairs in rooms 222-226."
        message += self.pizza_night_message(location)
        return message

    def pizza_night_message(self, location: dict):
        return ' Pizza tonight!' if self.bot.pizza_night(location['date']) else ''

    def get_student_leader_meeting_location_message(self):
        location = self.bot.find_location('student_leader')
        message = "Today's Student Leader meeting will be held in {building} {room}.".format_map(location)
        return message

    def get_conversations_meeting_location_message(self):
        location = self.bot.find_location('conversations')
        message = self.build_conversations_message(location)
        return message

    def specified_last_location(self):
        return self.args['last_location']
    
    def specified_clear_sent(self):
        return self.args['clear_sent']

    def specified_conversations(self):
        return self.args['conversations']

    def specified_student_leader(self):
        return self.args['student_leader']

    def specified_dry_run(self):
        return self.args['dry_run']

    def main(self):
        if self.specified_last_location():
            print(self.last_location())
            return

        if self.specified_clear_sent():
            self.db.clear_sent()
            return

        try:
            if self.specified_conversations():
                message = self.get_conversations_meeting_location_message()
            elif self.specified_student_leader():
                message = self.get_student_leader_meeting_location_message()
            else:
                raise Exception('Please specify either --student_leader or --conversations')

            if self.specified_dry_run():
                print(message)
            else:
                self.bot.post(message)
                self.db.mark_as_sent(self.meeting_type)
        except Exception as e:
            print(e)
            return 1


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--student-leader', action='store_true', help='Get the location of the Student Leader meeting. Use with -l to show the last location.')
    parser.add_argument('-c', '--conversations', action='store_true', help='Get the location of the Conversations meeting. Use with -l to show the last location.')
    parser.add_argument('-l', '--last-location', action='store_true', help='View the location of the last meeting. Used in conjunction with -s or -c')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Do not send message to GroupMe--just show what would be sent')
    parser.add_argument('--clear-sent', action='store_true', help='Clears the sent attribute in the database')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = vars(parse_args())
    code = Main(args).main()
    sys.exit(code or 0)
