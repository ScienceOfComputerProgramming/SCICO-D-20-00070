"""
This module tests the functionality of the tools module.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from sciit.cli.functions import print_progress_bar


class TestPrintProgressBar(TestCase):
    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_25_percent(self):
        print_progress_bar(1, 4)
        expected_output = '\r |████████████--------------------------------------| 25.0% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_33_percent(self):
        print_progress_bar(1, 3)
        expected_output = '\r |████████████████----------------------------------| 33.3% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_50_percent(self):
        print_progress_bar(1, 2)
        expected_output = '\r |█████████████████████████-------------------------| 50.0% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_66_percent(self):
        print_progress_bar(2, 3)
        expected_output = '\r |█████████████████████████████████-----------------| 66.7% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_75_percent(self):
        print_progress_bar(3, 4)
        expected_output = '\r |█████████████████████████████████████-------------| 75.0% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_100_percent(self):
        print_progress_bar(2, 2)
        expected_output = '\r |██████████████████████████████████████████████████| 100.0% \r\n'
        self.assertEqual(sys.stdout.getvalue(), expected_output)
