from .base import BaseParser

class DefaultParser(BaseParser):
    name = "unknown (default)"

    def tests_passed(self, result):
        return result.retcode == 0
