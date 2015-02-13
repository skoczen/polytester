#!/usr/bin/env python

from polytester.main import parser
from polytester.runner import PolytesterRunner


class TestRunner(object):
    def test_strip_ansi_colors(self):
        """Verify that ansi color codes are stripped from strings."""
        runner = PolytesterRunner(parser.parse_args(['--config', 'tests/tests.yml']))
        colored_string = "\e[31mHello World\e[0m"
        escaped = repr("\\e[31mHello World\\e[0m")
        assert runner.strip_ansi_colors(colored_string) == escaped
