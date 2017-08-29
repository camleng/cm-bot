import unittest
from unittest.mock import MagicMock
from cmbot import CMBot
import cmbot
import pytest
from datetime import datetime as dt, timedelta


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
    
    