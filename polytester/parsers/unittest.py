from .nose import NoseParser


class UnittestParser(NoseParser):
    """Output when using `python -m unittest` is the same as nose output."""
    name = "unittest"

    def command_matches(self, command):
        return "unittest" in command
