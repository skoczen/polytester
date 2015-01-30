import re
from .default import DefaultParser


class SaladParser(DefaultParser):
    name = "salad"

    def command_matches(self, command):
        return "salad" in command

    def num_passed(self, result):
        # 3 steps (3 passed)
        m = re.findall('(\d+) steps \((\d+) passed\)', result.cleaned_output)
        return int(m[-1][1])

    def num_total(self, result):
        # 3 steps (3 passed)
        m = re.findall('(\d+) steps \((\d+) passed\)', result.cleaned_output)
        return int(m[-1][0])

    def num_failed(self, result):
        return self.num_total(result) - self.num_passed(result)
