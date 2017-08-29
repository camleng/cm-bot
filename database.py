from tinydb import TinyDB, Query

class Database:
    def __init__(self):
        self.db = TinyDB('db.json')
        self.q = Query()
    
    def last_location(self, meeting_type):
        return self.db.get(self.q.type == meeting_type) or {}
    
    def update_location(self, location, meeting_type):
        self.db.update(location, self.q.type == meeting_type)

    def message_sent_today(self, meeting_type):
        return self.db.contains((self.q.type == meeting_type) & (self.q.status == 'sent'))

    def mark_as_sent(self, meeting_type):
        self.db.update({'status': 'sent'}, self.q.type == meeting_type)
    
    def clear_status(self):
        self.db.update({'status': ''}, (self.q.type == 'student_leader') | (self.q.type == 'conversations'))
