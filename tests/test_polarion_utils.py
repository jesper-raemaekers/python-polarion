import unittest
from polarion.utils import *


class TestPolarionUtils(unittest.TestCase):

    def test_clean_html(self):
        core_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu libero ipsum. Nullam eget augue'
        html_text = f'<p><img src="bla"/>{core_text}</p></br>'

        clean_text = clean_html(html_text)

        self.assertEqual(core_text, clean_text, msg="Cleaned text was not equal to expected core text")
