#!/usr/bin/env python
import pytest

from polytester.main import parser
from polytester.runner import PolytesterRunner


class TestRunner(object):
    def test_strip_ansi_escape_codes(self):
        """Verify that ansi escape codes are stripped from strings."""
        runner = PolytesterRunner(parser.parse_args(['--config', 'tests/tests.yml']))
        ansi_escaped_string = "\x1b[31mHello World\x1b[0m"
        escaped = "Hello World"
        assert runner.strip_ansi_escape_codes(ansi_escaped_string) == escaped

    def test_config_not_found(self):
        with pytest.raises(SystemExit):
            PolytesterRunner(parser.parse_args(['--config', 'tests/foo.yml']))

    def test_config_not_found_autoreload(self):
        with pytest.raises(SystemExit):
            PolytesterRunner(parser.parse_args(['--config', 'tests/foo.yml', '--autoreload']))

    def test_config_not_found_autoreload_wip_no_wip_command(self):
        with pytest.raises(SystemExit):
            PolytesterRunner(parser.parse_args(['--config', 'tests/foo.yml', '--autoreload', '--wip']))

    def test_config_not_found_autoreload_no_command(self):
        with pytest.raises(SystemExit):
            PolytesterRunner(parser.parse_args(['--config', 'tests/foo.yml', '--autoreload']))
