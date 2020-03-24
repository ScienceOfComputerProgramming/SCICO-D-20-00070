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
        progress_tracker = ProgressTracker(True, 4)
        progress_tracker.processed_object(1)
        expected_output = \
            '\rProcessing 1/4 objects:  |############--------------------------------------| 25.0%  Duration: 0:00:00\r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_33_percent(self):
        progress_tracker = ProgressTracker(True, 3)
        progress_tracker.processed_object(1)
        expected_output = \
            '\rProcessing 1/3 objects:  |################----------------------------------| 33.3%  Duration: 0:00:00\r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_50_percent(self):
        progress_tracker = ProgressTracker(True, 2)
        progress_tracker.processed_object(1)
        expected_output = \
            '\rProcessing 1/2 objects:  |#########################-------------------------| 50.0%  Duration: 0:00:00\r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_66_percent(self):
        progress_tracker = ProgressTracker(True, 3)
        progress_tracker.processed_object(2)
        expected_output = \
            '\rProcessing 2/3 objects:  |#################################-----------------| 66.7%  Duration: 0:00:00\r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_75_percent(self):
        progress_tracker = ProgressTracker(True, 4)
        progress_tracker.processed_object(3)
        expected_output = \
            '\rProcessing 3/4 objects:  |#####################################-------------| 75.0%  Duration: 0:00:00\r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_100_percent(self):
        progress_tracker = ProgressTracker(True, 1)
        progress_tracker.processed_object(1)
        expected_output = \
            '\rProcessing 1/1 objects:  |##################################################| 100.0%  Duration: 0:00:00\r\n'
        self.assertEqual(sys.stdout.getvalue(), expected_output)
