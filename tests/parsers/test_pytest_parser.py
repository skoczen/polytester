#!/usr/bin/env python

import pytest
from mock import Mock

from polytester.parsers import PyTestParser

parser = PyTestParser()


class TestPyTestParser(object):
    @pytest.mark.parametrize('cmd,should_match', [
        ('py.test', True,),
        ('python -m py.test', True,),
        ('coverate run --source foo -m py.test', True,),
        ('nosetests', False,),
        ('unittest', False,),
    ])
    def test_command_matches(self, cmd, should_match):
        """Verify detection of invocation of py.test"""
        assert parser.command_matches(cmd) == should_match

    def test_no_tests(self):
        """Verify parsing of no collected tests"""
        statusline = '=== in 0.00 seconds ==='
        r = Mock()
        r.output = statusline
        assert parser.num_passed(r) == 0
        assert parser.num_failed(r) == 0
        assert parser.num_error(r) == 0
        assert parser.num_total(r) == 0

    @pytest.mark.parametrize('total', [
        1,
        10,
        100,
        1000,
        123456789,
    ])
    def test_all_success(self, total):
        """Verify parsing of successfull test cases when all pass"""
        statusline = '=== {0} passed in 1.00 seconds ==='
        r = Mock()
        r.output = statusline.format(total)
        assert parser.num_passed(r) == total
        assert parser.num_failed(r) == 0
        assert parser.num_error(r) == 0
        assert parser.num_total(r) == total

    @pytest.mark.parametrize('passed,failed', [
        (1, 1,),
        (10, 1,),
        (1, 10,),
        (10, 10,),
        (100, 100,),
    ])
    def test_some_fail_some_pass(self, passed, failed):
        """Verify parsing of successfull and failed test cases when some pass
        and some fail.
        """
        statusline = '=== {failed} failed, {passed} passed in 1.00 seconds ==='
        r = Mock()
        r.output = statusline.format(failed=failed, passed=passed)
        assert parser.num_passed(r) == passed
        assert parser.num_failed(r) == failed
        assert parser.num_error(r) == 0
        assert parser.num_total(r) == passed + failed

    @pytest.mark.parametrize('passed,failed,error', [
        (1, 1, 1,),
        (10, 1, 1,),
        (1, 1, 10,),
        (10, 1, 1,),
        (1, 10, 1,),
        (10, 10, 1,),
        (100, 100, 1,),
    ])
    def test_some_fail_some_pass_some_error(self, passed, failed, error):
        """Verify parsing of combination of paseed/failed/errored tests."""
        statusline = ('=== {failed} failed, {passed} passed, {error} error in '
                      '1.00 seconds ===')
        r = Mock()
        r.output = statusline.format(failed=failed, passed=passed, error=error)
        assert parser.num_passed(r) == passed
        # Result collector currently counts errors as failures
        assert parser.num_failed(r) == failed + error
        assert parser.num_error(r) == error
        assert parser.num_total(r) == passed + failed + error
