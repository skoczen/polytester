# -*- coding: utf-8 -*-

from collections import OrderedDict
from clint.textui import colored
from clint.textui import puts, indent, columns
import fcntl
import importlib
import os
import time
import traceback
import subprocess
import sys
from yaml import load
from yaml.scanner import ScannerError

from .parsers import BaseParser, DefaultParser, DjangoParser
from .util import Bunch

BUNDLED_PARSERS = [BaseParser, DefaultParser, DjangoParser]
DEFAULT_PARSER = DefaultParser


class PolytesterRunner(object):

    def _print_error(self, message):
        puts(colored.red("ERROR: ") + message)

    def _fail(self, message):
        self._print_error(message)
        sys.exit(1)

    def _nice_traceback_and_quit(self):
        puts("Traceback: ")
        with indent(2):
            puts(traceback.format_exc(limit=1))
        sys.exit(1)

    def __init__(self, arg_options):
        # arg_options is expected to be an argparse namespace.

        # Parse out arg_options.
        self.verbose = arg_options.verbose
        config_file = arg_options.config_file
        wip = arg_options.wip
        run_parallel = arg_options.parallel
        if run_parallel:
            parallel_n = int(arg_options.parallel[0])
            parallel_m = int(arg_options.parallel[1])
            parallel_modulo = parallel_n % parallel_m
        if arg_options.test_names:
            tests_to_run = arg_options.test_names.split(",")
            all_tests = False
        else:
            all_tests = True

        # Detect and configure parsers
        puts("Detecting...")
        with indent(2):
            self.tests = []
            self.parsers = []
            for p in BUNDLED_PARSERS:
                self.register_parser(p)
            try:
                with open(os.path.join(os.getcwd(), config_file)) as f:
                    self.test_config = load(f)
                    self.test_config = OrderedDict(sorted(self.test_config.items(), key=lambda x: x[0]))
            except IOError:
                self._fail("Config file %s not found." % config_file)
            except ScannerError:
                self._print_error("Trouble parsing %s." % config_file)
                self._nice_traceback_and_quit()
            except:
                self._fail(puts(traceback.format_exc()))


            num_total = len(self.test_config.items())
            current_num = 0
            for name, options in self.test_config.items():
                run_suite = False
                current_num += 1
                skip_message = ""
                if run_parallel:
                    if parallel_modulo == current_num % num_total:
                        run_suite = True
                    else:
                        skip_message = ""
                elif all_tests or name in tests_to_run:
                    if not wip or "wip_command" in options:
                        run_suite = True
                    else:
                        if wip:
                            skip_message = "no wip_command"

                if run_suite:
                    if wip:
                        if not "wip_command" in options:
                            self._fail("%s is missing a wip_command." % name)
                        else:
                            command = options["wip_command"]
                            del options["wip_command"]
                            try:
                                del options["command"]
                            except KeyError:
                                pass

                    else:
                        if not "command" in options:
                            self._fail("%s is missing a command." % name)
                        else:
                            command = options["command"]
                            del options["command"]
                            try:
                                del options["wip_command"]
                            except KeyError:
                                pass
            

                    if not "short_name" in options:
                        options["short_name"] = name

                    if "parser" in options:
                        options["autodetected"] = False
                        try:
                            components = options["parser"].split(".")
                            if len(components) < 2:
                                self._fail("'%s' in the %s section of tests.yml does not have both a module and a class. Please format as module.ParserClass." % (
                                    options["parser"], name))
                            else:
                                module = ".".join(components[:-1])
                                class_name = components[-1]

                            i = importlib.import_module(module)
                            options["parser"] = i.getattr(class_name)()
                        except ImportError:
                            self._fail("Unable to find a parser called '%s' for %s on your PYTHONPATH." % (options["parser"], name))
                    else:
                        for p in self.parsers:
                            if hasattr(p, "command_matches"):
                                if p.command_matches(command) is True:
                                    options["parser"] = p
                                    break
                        if "parser" not in options:
                            options["parser"] = DEFAULT_PARSER()
                    try:
                        self.add(command, **options) 
                    except TypeError:
                        self._print_error("Unsupported attribute in tests.yml file.")
                        self._nice_traceback_and_quit()

                    puts(colored.green("✔") + " %s detected as %s tests." % (name, options["parser"].name))
                else:
                    if skip_message != "":
                        puts(colored.yellow("- %s skipped (%s)." % (name, skip_message)))
                    else:
                        puts(colored.yellow("- %s skipped." % (name,)))
        # runner.add("jasmine")
        # runner.add("karma e2e")

        self.config = Bunch(
            autoreload=False,
            failfast=False,
            verbose=False,
            wip=False,
        )

    def add(self, test_command, parser=None, watch_glob=None, short_name=None, autodetected=None):
        if not short_name:
            short_name = test_command.split(" ")[0]
        if not parser:
            parser = DefaultParser()

        self.tests.append(Bunch(
            command=test_command,
            parser=parser,
            autodetected=autodetected,
            watch_glob=watch_glob,
            short_name=short_name,
        ))

    def non_blocking_read(self, output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            return output.read()
        except:
            return None

    def register_parser(self, parser_class):
        self.parsers.append(parser_class())

    def run(self):
        puts()
        puts("Running tests...")
        results = {}
        processes = {}

        if self.verbose:
            for t in self.tests:
                processes[t.short_name] = subprocess.Popen(t.command, shell=True)
                processes[t.short_name].communicate()
                results[t.short_name] = Bunch(
                    output=u"",
                    retcode=None,
                    parser=t.parser,
                    test_obj=t,
                    passed=None,
                )
                results[t.short_name].retcode = processes[t.short_name].returncode
        else:
            for t in self.tests:
                processes[t.short_name] = subprocess.Popen(t.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                results[t.short_name] = Bunch(
                    output=u"",
                    retcode=None,
                    parser=t.parser,
                    test_obj=t,
                    passed=None,
                )
            while len(processes.items()) > 0:
                for name, p in list(processes.items()):
                    while p.poll() is None:
                        line = self.non_blocking_read(p.stdout)
                        if line:
                            results[name].output += "\n%s" % line.decode("utf-8")
                        time.sleep(0.5)

                    if p.returncode is not None:
                        out, err = p.communicate()
                        if out:
                            results[name].output += "\n%s" % out.decode("utf-8")
                        if err:
                            results[name].output += "\n%s" % err.decode("utf-8")
                        results[name].retcode = p.returncode
                        del processes[name]

        all_passed = True
        with indent(2):
            for t in self.tests:
                name = t.short_name
                r = results[name]

                r.passed = r.parser.tests_passed(r)
                pass_string = ""
                if not r.passed:
                    all_passed = False
                    try:
                        if r.parser.hasattr("num_fails"):
                            pass_string = " %s" % r.parser.num_fails(r)
                        else:
                            pass_string = " some"

                        if r.parser.hasattr("num_total"):
                            pass_string += " of %s" % r.parser.num_total(r)
                        else:
                            pass_string += ""
                    except:
                        pass
                    puts(colored.red("✘ %s -%s tests failed." % (name, pass_string)))
                    
                    with indent(2):
                        puts(u"%s" % r.output)

                            
                else:
                    try:
                        if r.parser.hasattr("num_passes"):
                            pass_string = " %s" % r.parser.num_passes(r)
                        else:
                            pass_string = ""
                    except:
                        pass
                    puts(colored.green("✔" + " %s -%s tests passed." % (name, pass_string)))

        if all_passed:
            puts()
            puts(colored.green("✔ All tests passed."))
            puts()
        else:
            self._fail("✘ Tests failed.")
            puts()
            sys.exit(1)
