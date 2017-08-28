import unittest
from unittest import mock
from gmail import CMBot
import pytest

class CMBotTest(unittest.TestCase):
    def setUp(self):
        self.bot = CMBot()

    def test_has_correct_attributes(self):
        for attr in self.attrs():
            assert hasattr(self.bot, attr)
    
    def attrs(self):
        return ['credential_dir', 'status_file', 'db', 'q']
    
    def test_get_last_location(self):
        pass
