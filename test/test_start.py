"""Test de comandos"""

import os
import unittest
from .conftest import bot


class TestStart(unittest.TestCase):
    """Test de distintos comandos sin lógica"""

    def test_start(self):
        """Start"""
        bot.send_message(os.environ["CHAT_ID"], '/start')
