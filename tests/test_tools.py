"""
This module tests the functionality of the tools module.
"""
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch
from gitissue import tools
from tests import mocks


class TestRunCommand(TestCase):

    @patch('subprocess.run', autospec=True)
    def test_run_command_simple_passes(self, mocked_run):
        mocked_run.return_value = mocks.SubprocessRun.Simple
        self.assertEqual(tools.run_command(
            'hello'), mocks.SubprocessRun.Simple.stdout.decode('utf-8'))

        mocked_run.assert_called()
        mocked_run.assert_called_with(['hello'], stdout=-1)

    @patch('subprocess.run', autospec=True)
    def test_run_git_command_passes(self, mocked_run):
        mocked_run.return_value = mocks.SubprocessRun.GitPass
        self.assertEqual(tools.run_command('git log'),
                         mocks.SubprocessRun.GitPass.stdout.decode('utf-8'))

        mocked_run.assert_called()
        mocked_run.assert_called_with(['git', 'log'], stdout=-1)

    @patch('subprocess.run', autospec=True)
    def test_run_git_command_failed(self, mocked_run):
        mocked_run.return_value = mocks.SubprocessRun.GitFail
        self.assertEqual(tools.run_command('git log'),
                         mocks.SubprocessRun.GitFail.stdout.decode('utf-8'))

        mocked_run.assert_called()
        mocked_run.assert_called_with(['git', 'log'], stdout=-1)


class TestReadManualFiles(TestCase):

    def test_read_file_passed(self):
        self.assertEqual(tools.read_man_file(
            'SUPPORTED_REPOS'), 'gitlab\ngithub\njira')

    def test_read_file_fails(self):
        with self.assertRaises(FileNotFoundError) as context:
            tools.read_man_file('test_read')
        self.assertTrue('No such file or directory:' in str(context.exception))


class TestYesNoOption(TestCase):

    @patch('builtins.input', return_value='Y')
    def test_yes_option_capital(self, mocked_input):
        self.assertTrue(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='y')
    def test_yes_option_common(self, mocked_input):
        self.assertTrue(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='YY')
    def test_yes_option_double_capital(self, mocked_input):
        self.assertFalse(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='YY')
    def test_yes_option_double_common(self, mocked_input):
        self.assertFalse(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='N')
    def test_no_option_capital(self, mocked_input):
        self.assertFalse(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='n')
    def test_no_option_common(self, mocked_input):
        self.assertFalse(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='@')
    def test_symbol_option(self, mocked_input):
        self.assertFalse(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='22')
    def test_double_number_option(self, mocked_input):
        self.assertFalse(tools.yes_no_option('Hear is a value'))

    @patch('builtins.input', return_value='1')
    def test_single_number_option(self, mocked_input):
        self.assertFalse(tools.yes_no_option('Hear is a value'))


class TestPrintProgressBar(TestCase):
    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_25_percent(self):
        tools.print_progress_bar(1, 4)
        expected_output = '\r |████████████--------------------------------------| 25.0% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_33_percent(self):
        tools.print_progress_bar(1, 3)
        expected_output = '\r |████████████████----------------------------------| 33.3% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_50_percent(self):
        tools.print_progress_bar(1, 2)
        expected_output = '\r |█████████████████████████-------------------------| 50.0% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_66_percent(self):
        tools.print_progress_bar(2, 3)
        expected_output = '\r |█████████████████████████████████-----------------| 66.7% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_75_percent(self):
        tools.print_progress_bar(3, 4)
        expected_output = '\r |█████████████████████████████████████-------------| 75.0% \r'
        self.assertEqual(sys.stdout.getvalue(), expected_output)

    def test_100_percent(self):
        tools.print_progress_bar(2, 2)
        expected_output = '\r |██████████████████████████████████████████████████| 100.0% \r\n'
        self.assertEqual(sys.stdout.getvalue(), expected_output)
