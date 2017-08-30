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
