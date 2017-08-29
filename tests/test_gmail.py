import unittest
from unittest.mock import MagicMock
from cmbot import CMBot
import cmbot
import pytest
from datetime import datetime as dt, timedelta
from gmail import Gmail

class GmailTest(unittest.TestCase):
    def setUp(self):
        self.gmail = Gmail()
    
    