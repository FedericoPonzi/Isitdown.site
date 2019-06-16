import unittest
from isitdown.routes import is_spam

class TestUtils(unittest.TestCase):
    def test_isSpam(self):
        self.assertTrue(is_spam("google.it",["google.it"]))
        self.assertFalse(is_spam("google.it", ["google.com"]))
        self.assertTrue(is_spam("google.it",["google"]))
