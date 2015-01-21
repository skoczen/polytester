class BaseParser(object):
    def tests_passed(self, result):
        raise NotImplementedError

    # def num_passes(self):
    #     # Optional, returns the number of passing tests.
    #     # Can depend on num_fails or num_total.
    #     pass

    # def num_fails(self):
    #     # Optional, returns the number of failing tests.
    #     # Can depend on num_passes or num_total.
    #     pass

    # def num_total(self):
    #     # Optional, returns the total number of tests.
    #     # Can depend on num_passes or num_fails.
    #     pass

    # def command_matches(self, command):
    #     # Optional, used for trying to auto detect the test framework.
    #     return False
