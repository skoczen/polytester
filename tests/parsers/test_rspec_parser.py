#!/usr/bin/env python

import pytest
from mock import Mock

from polytester.parsers.rspec import RspecParser

parser = RspecParser()


def _get_statusline(params):
    """Generate a mock statusline like rspec would output."""
    total = sum(params.values())
    statusline = 'Finished in 0.001s seconds\n'

    passed = params.get('passed', 0)
    failed = params.get('failed', 0)
    error = params.get('error', 0)

    total = passed + failed + error
    total_failed = failed + error
    statusline += '{0} examples, {1} failures'.format(total, total_failed)
    return statusline


class TestRspecParser(object):
    @pytest.mark.parametrize('cmd,should_match', [
        ('rspec', True,),
        ('bundle exec rspec', True,),
        ('bundle exec rspec spec', True,),
        ('rspec spec/', True,),
        ('rspec .', True,),
        ('rake test', False,),
        ('rake teaspoon', False,),
    ])
    def test_command_matches(self, cmd, should_match):
        """Verify detection of invocation of rspec"""
        assert parser.command_matches(cmd) == should_match

    @pytest.mark.parametrize('params', [
        # No tests collected at all
        {},

        # Only passed tests
        {'passed': 1},
        {'passed': 10},
        {'passed': 100},
        {'passed': 1000},
        {'passed': 123456789},

        # Only failed tests
        {'failed': 1},
        {'failed': 10},
        {'failed': 100},
        {'failed': 1000},
        {'failed': 123456789},

        # Some passed, some failed
        {'passed': 10, 'failed': 1},
        {'passed': 1, 'failed': 10},
    ])
    def test_status_parsers(self, params):
        statusline = _get_statusline(params)
        r = Mock()
        r.output = statusline.format(**params)

        expected_passed = params.get('passed', 0)
        expected_failed = params.get('failed', 0)
        expected_total = expected_passed + expected_failed

        assert parser.num_passed(r) == expected_passed
        assert parser.num_failed(r) == expected_failed
        assert parser.num_total(r) == expected_total
