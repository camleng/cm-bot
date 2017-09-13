from datetime import datetime as dt, timedelta
import argparse
import sys

from database import Database
from cmbot import CMBot
from models import MeetingType as Type


class Main:
    def __init__(self, args: dict):
        self.args = args
        self.bot = CMBot(self.specified_setup())
        self.meeting_type = self.get_meeting_type(args)

    def get_meeting_type(self, args: dict) -> Type:
        return Type.CONVERSATIONS if self.args[Type.CONVERSATIONS.value] else Type.STUDENT_LEADER

    def last_location(self) -> dict:
        location = self.bot.last_location(self, meeting_type, sentence=True)
        return location if location else "Sorry, I couldn't find a previous location"

    def build_conversations_message(self, location: str) -> str:
        message = ''
        if location['room'] == 'Classic Ballroom':
            message = "Today's Conversations meeting will be held downstairs in the Walb Classic Ballroom."
        elif location['room'] == '222-226':
            message = "Today's Conversations meeting will be held upstairs in rooms 222-226."
        message += self.pizza_night_message(location)
        return message

    def pizza_night_message(self, location: dict) -> str:
        return ' Pizza tonight!' if self.bot.is_pizza_night(location['date']) else ''

    def get_student_leader_meeting_location_message(self) -> str:
        location = self.bot.find_location(Type.STUDENT_LEADER)
        message = "Today's Student Leader meeting will be held in {building} {room}.".format_map(location)
        return message

    def get_conversations_meeting_location_message(self) -> str:
        location = self.bot.find_location(Type.CONVERSATIONS)
        message = self.build_conversations_message(location)
        return message

    def specified_last_location(self) -> bool:
        return self.args['last_location']
    
    def specified_clear_sent(self) -> bool:
        return self.args['clear_sent']

    def specified_conversations(self) -> bool:
        return self.args[Type.CONVERSATIONS.value]

    def specified_student_leader(self) -> bool:
        return self.args[Type.STUDENT_LEADER.value]

    def specified_dry_run(self) -> bool:
        return self.args['dry_run']
    
    def specified_setup(self) -> bool:
        return self.args['setup']

    def main(self) -> int:
        if self.specified_setup():
            self.bot.gmail.get_new_credentials()
            print("\nYou're all set up! Run `python main.py -h` for more help.")
            sys.exit()

        if self.specified_last_location():
            print(self.last_location())
            return

        if self.specified_clear_sent():
            self.bot.db.clear_sent()
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
                self.bot.db.mark_as_sent(self.meeting_type)
        except Exception as e:
            print(e)
            return 1


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--student-leader', action='store_true', help='Get the location of the Student Leader meeting. Use with -l to show the last location.')
    parser.add_argument('-c', '--conversations', action='store_true', help='Get the location of the Conversations meeting. Use with -l to show the last location.')
    parser.add_argument('-l', '--last-location', action='store_true', help='View the location of the last meeting. Used in conjunction with -s or -c.')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Do not send message to GroupMe--just show what would be sent.')
    parser.add_argument('--setup', action='store_true', help='Guided setup for CM-Bot.')        
    parser.add_argument('--clear-sent', action='store_true', help='Clears the sent attribute in the database.')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = vars(parse_args())
    code = Main(args).main()
    sys.exit(code or 0)
