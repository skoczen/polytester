#!/usr/bin/env python

from polytester.main import parser
from polytester.runner import PolytesterRunner


class TestRunner(object):
    def test_strip_ansi_escape_codes(self):
        """Verify that ansi escape codes are stripped from strings."""
        runner = PolytesterRunner(parser.parse_args(['--config', 'tests/tests.yml']))
        ansi_escaped_string = "\x1b[31mHello World\x1b[0m"
        escaped = "Hello World"
        assert runner.strip_ansi_escape_codes(ansi_escaped_string) == escaped
