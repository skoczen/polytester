import re

from .default import DefaultParser


class ProtractorParser(DefaultParser):
    name = "protractor"

    def command_matches(self, command):
        return "protractor" in command

    def num_passed(self, result):
        return self.num_total(result) - self.num_failed(result)

    def num_total(self, result):
        # 2 tests, 3 assertions, 1 failure
        m = re.findall('(\d+) tests?, (\d+) assertions?, (\d+) failures?', result.cleaned_output)

        if len(m) > 0:
            return int(m[-1][1])

    def num_failed(self, result):
        # 2 tests, 3 assertions, 1 failure
        m = re.findall('(\d+) tests?, (\d+) assertions?, (\d+) failures?', result.cleaned_output)

        if len(m) > 0:
            return int(m[-1][-1])
