from unittest import TestCase
from unittest.mock import Mock
from sciit.regex import get_file_object_pattern
from sciit.regex import (C_STYLE, PYTHON, HTML, MATLAB, HASKELL, PLAIN, MARKDOWN)


class TestFileObjectPattern(TestCase):

    def test_file_is_java(self):
        file_object = Mock()
        file_object.path = 'test.java'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_c(self):
        file_object = Mock()
        file_object.path = 'test.c'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_csharp(self):
        file_object = Mock()
        file_object.path = 'test.cs'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_swift(self):
        file_object = Mock()
        file_object.path = 'test.swift'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_matlab(self):
        file_object = Mock()
        file_object.path = 'test.m'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, MATLAB)

    def test_file_is_xhtml(self):
        file_object = Mock()
        file_object.path = 'test.xhtml'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, HTML)

    def test_file_is_htm(self):
        file_object = Mock()
        file_object.path = 'test.htm'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, HTML)

    def test_file_is_python(self):
        file_object = Mock()
        file_object.path = 'test.py'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, PYTHON)

    def test_file_is_haskell(self):
        file_object = Mock()
        file_object.path = 'test.hs'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, HASKELL)

    def test_file_is_ruby(self):
        file_object = Mock()
        file_object.path = 'test.rb'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_markdown(self):
        file_object = Mock()
        file_object.path = 'test.md'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, MARKDOWN)

    def test_file_is_bdd_feature(self):
        file_object = Mock()
        file_object.path = 'test.feature'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_yaml(self):
        file_object = Mock()
        file_object.path = 'test.yml'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_plain_text(self):
        file_object = Mock()
        file_object.path = 'test'
        file_object.mime_type = 'text/plain'
        pattern = get_file_object_pattern(file_object)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_not_supported(self):
        file_object = Mock()
        file_object.path = 'test.xst'
        pattern = get_file_object_pattern(file_object)
        self.assertFalse(pattern)

    def test_file_mime_type_not_supported(self):
        file_object = Mock()
        file_object.path = 'test'
        file_object.mime_type = 'application/pdf'
        pattern = get_file_object_pattern(file_object)
        self.assertFalse(pattern)
