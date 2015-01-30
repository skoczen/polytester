import re

from .default import DefaultParser


class DjangoParser(DefaultParser):
    name = "django"

    def command_matches(self, command):
        return "manage.py test" in command

    def num_passed(self, result):
        return self.num_total(result) - self.num_failed(result)

    def num_total(self, result):
        # Ran 2 test(s) in nnn seconds.
        m = re.findall('Ran (\d+) tests?', result.output)
        return int(m[-1])

    def num_failed(self, result):
        # If failed, you'll see one of
        # FAILED (failures=1)
        # FAILED (failures=1, errors=1)
        # FAILED (errors=1)
        m = re.findall('FAILED \(failures=(\d+)', result.output)
        if len(m) > 0:
            return int(m[-1])
        else:
            return 0
