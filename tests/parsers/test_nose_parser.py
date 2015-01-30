#!/usr/bin/env python

import pytest
from mock import Mock

from polytester.parsers.nose import NoseParser

parser = NoseParser()


def _get_statusline(params):
    """Generate a mock statusline like nose would output."""
    total = sum(params.values())
    statusline = 'Ran {total} tests in 0.001s\n\n'.format(total=total)

    info_elements = []
    if 'error' in params:
        info_elements.append('errors={error}')
    if 'failed' in params:
        info_elements.append('failures={failed}')

    if info_elements:
        statusline += 'FAILED ({0})'.format(', '.join(info_elements))
    else:
        statusline += 'OK'

    return statusline


class TestNoseParser(object):
    @pytest.mark.parametrize('cmd,should_match', [
        ('nosetests', True,),
        ('python -m nose', True,),
        ('coverage run --source foo -m nose', True,),
        ('py.test', False,),
        ('unittest', False,),
    ])
    def test_command_matches(self, cmd, should_match):
        """Verify detection of invocation of py.test"""
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

        # Only errored tests
        {'error': 1},
        {'error': 10},
        {'error': 100},
        {'error': 1000},
        {'error': 123456789},

        # Some error, some failed
        {'error': 10, 'failed': 1},
        {'error': 1, 'failed': 10},

        # Some error, some passed
        {'error': 10, 'passed': 1},
        {'error': 1, 'passed': 10},

        # Some passed, some failed
        {'passed': 10, 'failed': 1},
        {'passed': 1, 'failed': 10},

        # Some error, some failed, some passed
        {'error': 10, 'failed': 1, 'passed': 100},
        {'error': 1, 'failed': 10, 'passed': 100},
    ])
    def test_status_parsers(self, params):
        statusline = _get_statusline(params)
        r = Mock()
        r.output = statusline.format(**params)

        expected_passed = params.get('passed', 0)
        expected_error = params.get('error', 0)
        # Result collector currently counts errored tests as failed
        expected_failed = params.get('failed', 0) + expected_error
        expected_total = expected_passed + expected_failed

        assert parser.num_passed(r) == expected_passed
        assert parser.num_failed(r) == expected_failed
        assert parser.num_error(r) == expected_error
        assert parser.num_total(r) == expected_total
