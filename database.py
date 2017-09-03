from tinydb import TinyDB, Query

class Database:
    def __init__(self):
        self.db = TinyDB('db.json')
        self.q = Query()
    
    def last_location(self, meeting_type):
        return self.db.get(self.q.type == meeting_type) or {}
    
    def meeting_type_exists(self, meeting_type):
        return self.db.search(self.q.type == meeting_type)

    def update_location(self, location, meeting_type):
        if self.meeting_type_exists(meeting_type):
            self.db.update(location, self.q.type == meeting_type)
        else:
            self.db.insert({'type': meeting_type, **location})

    def message_sent_today(self, meeting_type):
        return self.db.contains((self.q.type == meeting_type) & (self.q.sent == True))

    def mark_as_sent(self, meeting_type):
        self.db.update({'sent': True}, self.q.type == meeting_type)
    
    def clear_sent(self):
        self.db.update({'sent': False}, (self.q.type == 'student_leader') | (self.q.type == 'conversations'))

    def get_bot_id(self, id_type='prod'):
        if not self.exists(id_type):
            bot_id = self.prompt_user('Bot id')
            self.db.insert({id_type: bot_id})
        return self.db.get(self.q[id_type].exists())[id_type]
    
    def prompt_user(self, prompt):
        result = ''
        while not result:
            result = input(f'{prompt}: ')
        return result
    
    def exists(self, key):
        return self.db.contains(self.q[key].exists())

    @property
    def slack_url(self):
        if not self.exists('slack_url'):
            slack_url = self.prompt_user('Slack URL')
            self.db.insert({'slack_url': slack_url})
        return self.db.get(self.q['slack_url'].exists())['slack_url']
