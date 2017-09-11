from tinydb import TinyDB, Query

class Database:
    def __init__(self, setup=False):
        self.db = TinyDB('db.json')
        self.q = Query()
        self.setup = setup
    
    def last_location(self, meeting_type: str):
        return self.db.get(self.q.type == meeting_type) or {}
    
    def meeting_type_exists(self, meeting_type: str):
        return self.db.search(self.q.type == meeting_type)

    def update_location(self, location: dict, meeting_type: str):
        if self.meeting_type_exists(meeting_type):
            self.db.update(location, self.q.type == meeting_type)
        else:
            self.db.insert({'type': meeting_type, **location})

    def message_sent_today(self, meeting_type: str):
        return self.db.contains((self.q.type == meeting_type) & (self.q.sent == True))

    def mark_as_sent(self, meeting_type: str):
        self.db.update({'sent': True}, self.q.type == meeting_type)
    
    def clear_sent(self):
        self.db.update({'sent': False}, (self.q.type == 'student_leader') | (self.q.type == 'conversations'))

    def get_bot_id(self, id_type='prod'):
        if self.setup and not self.exists(id_type):
            bot_id = self.prompt_user('Bot ID')
            self.insert_bot_id(id_type, bot_id)
        elif self.setup and self.exists(id_type):
            bot_id = self.prompt_user('Bot ID')            
            self.db.update({id_type: bot_id}, self.q[id_type].exists())
        elif not self.exists(id_type):
            bot_id = self.prompt_user('Bot ID')
            self.insert_bot_id(id_type, bot_id)
        return self.db.get(self.q[id_type].exists())[id_type]
    
    def insert_bot_id(self, id_type: str, bot_id: str):
        self.db.insert({id_type: bot_id})
                                                    
    def prompt_user(self, prompt: str, required=True):
        optional_tag = ' [optional]' if not required else ''
        result = input(f'{prompt}{optional_tag}: ').strip()    
        while required and not result:
            result = input(f'{prompt}{optional_tag}: ').strip() 
        return result or None
    
    def exists(self, key: str):
        return self.db.contains(self.q[key].exists())

    @property
    def slack_url(self):
        key = 'slack_url'
        if self.setup and not self.exists(key):
            slack_url = self.prompt_user('Slack URL', required=False)
            self.db.insert({key: slack_url})
        elif self.setup and self.exists(key):
            slack_url = self.prompt_user('Slack URL', required=False)            
            self.db.update({key: slack_url}, self.q[key].exists())
        return (self.db.get(self.q[key].exists()) or {}).get(key, None)
