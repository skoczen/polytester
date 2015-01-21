import re

from .default import DefaultParser


class DjangoParser(DefaultParser):
    name = "django"

    def command_matches(self, command):
        return "manage.py test" in command

    def num_passes(self, result):
        return self.num_total() - self.num_failed()

    def num_total(self, result):
        # Ran 2 test(s) in nnn seconds.
        m = re.search(result.output, 'Ran \d+ tests?')
        return int(m.group(0))
    
    def num_failed(self, result):
        # If failed, you'll see one of
        # FAILED (failures=1)
        # FAILED (failures=1, errors=1)
        # FAILED (errors=1)
        m = re.search(result.output, 'FAILED \(failures=\d+\)')
        # print(int(m.group(0)))
        return int(m.group(0))

    