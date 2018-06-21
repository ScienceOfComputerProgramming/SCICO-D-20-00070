"""
This module tests the functionality of the tools module.
"""
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
