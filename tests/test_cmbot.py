import unittest
from unittest.mock import MagicMock, ANY
from cmbot import CMBot
import cmbot
import pytest
from datetime import datetime as dt, timedelta
import json
import pickle


class CMBotTest(unittest.TestCase):
    def setUp(self):
        self.bot = CMBot()

    def test_has_correct_attributes(self):
        for attr in self.attrs():
            assert hasattr(self.bot, attr)
    
    def attrs(self):
        return ['id', 'db', 'gmail']
    
    def test_build_sentence_with_location_returns_sentence(self):
        location = {'building': 'Walb', 'room': '222-226', 'date': dt(2017, 8, 21)}
        sentence = self.bot.build_sentence(location)
        assert 'The {date.month}/{date.day} meeting was held in {building} {room}'.format_map(location) == sentence

    def test_build_sentence_with_invalid_location_returns_error_sentence(self):
        location = {'date': dt(2017, 8, 21)}
        error = self.bot.build_sentence(location)
        assert 'There was no meeting on {date.month}/{date.day}'.format_map(location) == error

    def test_check_message_sent_today_returns_true_raises_exception(self):
        self.bot.db.message_sent_today = MagicMock(return_value=True)
        with pytest.raises(Exception):
            self.bot.check_message_sent_today('student_leader')

    def test_check_no_student_leader_meeting_today(self):
        self.bot.is_not_day = MagicMock(return_value=True)
        with pytest.raises(Exception):
            self.bot.check_no_student_leader_meeting_today('student_leader')
    
    def test_check_no_conversations_meeting_today(self):
        self.bot.is_not_day = MagicMock(return_value=True)
        with pytest.raises(Exception):
            self.bot.check_no_conversations_meeting_today('conversations')

    def test_student_leader_regex_raises_exception_with_no_student_leader_meeting(self):
        message = self.email_no_student_leader[0]
        with pytest.raises(Exception):
            self.bot.extract_student_leader_room(message)
    
    def test_conversations_regex_matches_with_no_student_leader_meeting(self):
        message = self.email_no_student_leader[0]
        building, room = self.bot.extract_conversations_room(message)
        assert building == 'Walb'
        assert room == 'Classic Ballroom'

    def test_conversations_regex_matches_email_sent_tuesday(self):
        message = self.email_sent_tuesday[0]
        building, room = self.bot.extract_conversations_room(message)
        assert building == 'Walb'
        assert room == 'Classic Ballroom'

    @property
    def student_leader_message(self):
        return 'The Student Leader meeting will be held in Walb 226.'

    @property
    def email_no_student_leader(self):
        message, headers = '', ''
        with open('tests/emails/no-student-leader/message') as f:
            message = f.read()
        with open('tests/emails/no-student-leader/headers', 'rb') as f:
            headers = pickle.load(f)
        return message, headers

    @property
    def email_sent_tuesday(self):
        message, headers = '', ''
        with open('tests/emails/sent-on-tuesday/message') as f:
            message = f.read()
        with open('tests/emails/sent-on-tuesday/headers', 'rb') as f:
            headers = pickle.load(f)
        return message, headers
