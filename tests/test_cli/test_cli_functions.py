import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from sciit.cli.functions import print_progress_bar, read_sciit_version, yes_no_option


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