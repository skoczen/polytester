import re

from .default import DefaultParser


class NoseParser(DefaultParser):
    name = "nose"

    def command_matches(self, command):
        return "manage.py test" in command

    def num_passed(self, result):
        return self.num_total() - self.num_failed()

    def num_total(self, result):
        # Ran 2 test(s) in nnn seconds.
        m = re.search('Ran \d+ tests?', result.output)
        return int(m.group(0))
    
    def num_failed(self, result):
        # If failed, you'll see one of
        # FAILED (failures=1)
        # FAILED (failures=1, errors=1)
        # FAILED (errors=1)
        m = re.search('FAILED \(failures=\d+\)', result.output)
        return int(m.group(0))
