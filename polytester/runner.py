# -*- coding: utf-8 -*-

from clint.textui import colored
from clint.textui import puts, indent, columns
import fcntl
import importlib
import os
import time
import traceback
import subprocess
import sys
from yaml import load, dump
from yaml.scanner import ScannerError

from parsers import BaseParser, DefaultParser, DjangoParser
from util import Bunch

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

    def __init__(self, config_file=None, *args, **kwargs):
        super(PolytesterRunner, self).__init__(*args, **kwargs)
        puts("Detecting...")
        with indent(2):
            self.tests = []
            self.parsers = []
            for p in BUNDLED_PARSERS:
                self.register_parser(p)

            if not config_file:
                config_file = "tests.yml"
            try:
                with open(os.path.join(os.getcwd(), config_file)) as f:
                    self.test_config = load(f)
            except IOError:
                self._fail("Config file %s not found." % config_file)
            except ScannerError:
                self._print_error("Trouble parsing %s." % config_file)
                self._nice_traceback_and_quit()
            except Exception, e:
                self._fail(puts(traceback.format_exc()))

            for name, options in self.test_config.items():
                if not "command" in options:
                    self._fail("%s is missing a command." % name)
                else:
                    command = options["command"]
                    del options["command"]
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
            for name, p in processes.items():
                while p.poll() is None:
                    line = self.non_blocking_read(p.stdout)
                    if line:
                        results[name].output += "\n%s" % line
                    time.sleep(0.5)

                if p.returncode is not None:
                    out, err = p.communicate()
                    if out:
                        results[name].output += "\n%s" % out
                    if err:
                        results[name].output += "\n%s" % err
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
                        puts("%s" % r.output)
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
            puts(colored.green("All tests passed."))
            puts()
        else:
            self._fail("Tests failed.")
            puts()
            sys.exit(1)
