import unittest
from unittest import mock
from database import Database
import pytest
from datetime import datetime as dt, timedelta


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = Database()

    def test_has_correct_attributes(self):
        for attr in self.attrs():
            assert hasattr(self.db, attr)
    
    def attrs(self):
        return ['db', 'q']
    
    def test_last_location_returns_location(self):
        location = self.db.last_location('student_leader')
        assert isinstance(location, dict)
