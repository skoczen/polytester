from .base import BaseParser


class DefaultParser(BaseParser):
    name = "standard"

    def tests_passed(self, result):
        return result.return_code == 0
