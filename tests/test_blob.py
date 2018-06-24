"""
This module tests the functionality of the tools module.
"""
from unittest import TestCase
from gitissue import IssueBlob


class TestIssueBlob(TestCase):

    def test_write_blob(self):
        #create blob with some contents
        contents = b'contents'
        issue = IssueBlob(contents)
        issue.write_blob()        
