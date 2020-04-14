import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from sciit.cli.functions import read_sciit_version, yes_no_option
from sciit.cli import ProgressTracker


class TestReadManualFiles(TestCase):

    def test_read_file_passed(self):
        result = read_sciit_version()
        self.assertTrue(isinstance(result, str))


class TestYesNoOption(TestCase):

    @patch('builtins.input', return_value='Y')
    def test_yes_option_capital(self, mocked_input):
        self.assertTrue(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='y')
    def test_yes_option_common(self, mocked_input):
        self.assertTrue(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='YY')
    def test_yes_option_double_capital(self, mocked_input):
        self.assertFalse(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='YY')
    def test_yes_option_double_common(self, mocked_input):
        self.assertFalse(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='N')
    def test_no_option_capital(self, mocked_input):
        self.assertFalse(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='n')
    def test_no_option_common(self, mocked_input):
        self.assertFalse(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='@')
    def test_symbol_option(self, mocked_input):
        self.assertFalse(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='22')
    def test_double_number_option(self, mocked_input):
        self.assertFalse(yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='1')
    def test_single_number_option(self, mocked_input):
        self.assertFalse(yes_no_option('Hear is a value'))


class TestPrintProgressBar(TestCase):
    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_25_percent(self):
        progress_tracker = ProgressTracker(4)
        progress_tracker.processed_object(1)
        self.assertIn("25.0%", sys.stdout.getvalue())


    def test_33_percent(self):
        progress_tracker = ProgressTracker(3)
        progress_tracker.processed_object(1)
        self.assertIn("33.3%", sys.stdout.getvalue())


    def test_50_percent(self):
        progress_tracker = ProgressTracker(2)
        progress_tracker.processed_object(1)
        self.assertIn("50.0%", sys.stdout.getvalue())


    def test_66_percent(self):
        progress_tracker = ProgressTracker(3)
        progress_tracker.processed_object(2)
        self.assertIn("66.7%", sys.stdout.getvalue())

    def test_75_percent(self):
        progress_tracker = ProgressTracker(4)
        progress_tracker.processed_object(3)
        self.assertIn("75.0%", sys.stdout.getvalue())

    def test_100_percent(self):
        progress_tracker = ProgressTracker(1)
        progress_tracker.processed_object(1)
        self.assertIn("100.0%", sys.stdout.getvalue())
