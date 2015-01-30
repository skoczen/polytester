import re

from .default import DefaultParser


class PyTestParser(DefaultParser):
    name = "py.test"

    def command_matches(self, command):
        return "py.test" in command

    def num_passed(self, result):
        # 99 passed in 99 seconds.
        m = re.findall('(\d+) passed', result.output)
        if len(m) > 0:
            return int(m[-1])
        return 0

    def num_total(self, result):
        return self.num_passed(result) + self.num_failed(result)

    def num_failed(self, result):
        failed = 0
        m = re.findall('(\d+) failed', result.output)
        if len(m) > 0:
            failed += int(m[-1])
        failed += self.num_error(result)
        return failed

    def num_error(self, result):
        m = re.findall('(\d+) error', result.output)
        if len(m) > 0:
            return int(m[-1])
        return 0
