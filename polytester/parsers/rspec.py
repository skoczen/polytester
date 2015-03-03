import re

from .default import DefaultParser


class RspecParser(DefaultParser):
    name = "rspec"

    def command_matches(self, command):
        return "rspec" in command

    def num_passed(self, result):
        return self.num_total(result) - self.num_failed(result)

    def num_total(self, result):
        # 10 examples, 0 failures
        m = re.findall('(\d+) examples', result.output)
        return int(m[-1])

    def num_failed(self, result):
        # 10 examples, 1 failure
        # 10 examples, 9 failures
        m = re.findall('(\d+) failure', result.output)
        return int(m[-1])

    def num_error(self, result):
        return self.num_failed(result)
