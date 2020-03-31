from unittest import TestCase
from unittest.mock import Mock
from sciit.regex import get_file_object_pattern
from sciit.regex import (C_STYLE, PYTHON, HTML, MATLAB, HASKELL, PLAIN, MARKDOWN)


class TestFileObjectPattern(TestCase):

    def test_file_is_java(self):
        path = 'test.java'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_c(self):
        path = 'test.c'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_csharp(self):
        path = 'test.cs'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_swift(self):
        path = 'test.swift'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, C_STYLE)

    def test_file_is_matlab(self):
        path = 'test.m'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, MATLAB)

    def test_file_is_xhtml(self):
        path = 'test.xhtml'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, HTML)

    def test_file_is_htm(self):
        path = 'test.htm'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, HTML)

    def test_file_is_python(self):
        path = 'test.py'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, PYTHON)

    def test_file_is_haskell(self):
        path = 'test.hs'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, HASKELL)

    def test_file_is_ruby(self):
        path = 'test.rb'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_markdown(self):
        path = 'test.md'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, MARKDOWN)

    def test_file_is_bdd_feature(self):
        path = 'test.feature'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_yaml(self):
        path = 'test.yml'
        pattern = get_file_object_pattern(path)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_plain_text(self):
        path = 'test'
        mime_type = 'text/plain'
        pattern = get_file_object_pattern(path, mime_type)
        self.assertEqual(pattern, PLAIN)

    def test_file_is_not_supported(self):
        
        path = 'test.xst'
        pattern = get_file_object_pattern(path)
        self.assertFalse(pattern)

    def test_file_mime_type_not_supported(self):
        
        path = 'test'
        mime_type = 'application/pdf'
        pattern = get_file_object_pattern(path, mime_type)
        self.assertFalse(pattern)
