from enum import Enum

class MeetingType(Enum):
    STUDENT_LEADER = 'student_leader'
    CONVERSATIONS = 'conversations'

class Service(Enum):
    GROUPME = 'GroupMe'
    SLACK = 'Slack'
