import argparse
from .runner import PolytesterRunner


parser = argparse.ArgumentParser(
    description="Polytester easily runs tests in multiple languages."
)
parser.add_argument(
    '--verbose', '-v', dest='verbose', action='store_const',
    const=True, default=False,
    help="Dumps all output to the shell. This will run test suites serially."
)
parser.add_argument(
    '--wip', dest='wip', action='store_const',
    const=True, default=False,
    help="Work in progress mode. Runs wip_commnand for all suites that specify it."
)
parser.add_argument(
    '--autoreload', '--ci', dest='autoreload', action='store_const',
    const=True, default=False,
    help="Watches all files specified in watch_globs, and runs the relevant suite on file changes."
)
parser.add_argument(
    '--parallel', metavar=('n', 'm'), type=str, nargs=2,
    help="In parallel build test environments, only runs test chunk n of m."
)
parser.add_argument(
    '--config', dest='config_file', type=str, default="tests.yml",
    help="Specifies a different location for the config file.  Default is tests.yml."
)
parser.add_argument(
    'test_names', metavar='tests', type=str, nargs='?',
    help='Optional. Just runs the test(s) specified. Comma-separating is fine. If not specified, all tests are run.')


def main():
    args = parser.parse_args()
    runner = PolytesterRunner(args)
    runner.run()


if __name__ == '__main__':
    main()
