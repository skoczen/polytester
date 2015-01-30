import re
from .default import DefaultParser


class KarmaParser(DefaultParser):
    name = "karma"

    def command_matches(self, command):
        return "karma" in command

    def num_passed(self, result):
        return self.num_total(result) - self.num_failed(result)

    def num_total(self, result):
        # Executed 2 of 2 (1 FAILED)
        m = re.findall('Executed (\d+) of (\d+)', result.cleaned_output)
        return int(m[-1][1])

    def num_failed(self, result):
        # You'll see either
        # Executed 2 of 2 (1 FAILED)
        # Executed 1 of 1 SUCCESS
        # Note that karma rewrites the screen as it goes,
        # so you have to grab the last one.
        fails = re.findall(
            'Executed (\d+) of (\d+) \((\d+) FAILED\)',
            result.cleaned_output
        )

        if len(fails) > 0:
            return int(fails[-1][-1])
        else:
            m = re.findall(
                'Executed (\d+) of (\d+) SUCCESS',
                result.cleaned_output
            )
            if len(m) > 0:
                return 0
