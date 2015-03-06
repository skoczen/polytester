# -*- coding: utf-8 -*-

from collections import OrderedDict
from clint.textui import colored
from clint.textui import puts, indent
import fcntl
import importlib
import logging
from multiprocessing import Process
import os
import re
import time
from threading import Thread
import traceback
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from yaml import load
from yaml.scanner import ScannerError

from .parsers.base import BaseParser
from .parsers.default import DefaultParser
from .parsers.django import DjangoParser
from .parsers.karma import KarmaParser
from .parsers.nose import NoseParser
from .parsers.protractor import ProtractorParser
from .parsers.salad import SaladParser
from .parsers.pytest import PyTestParser
from .parsers.unittest import UnittestParser
from .util import Bunch


BUNDLED_PARSERS = [
    BaseParser,
    DefaultParser,
    DjangoParser,
    KarmaParser,
    NoseParser,
    PyTestParser,
    UnittestParser,
    ProtractorParser,
    SaladParser,
]
DEFAULT_PARSER = DefaultParser


class AutoreloadHandler(PatternMatchingEventHandler):
    patterns = []

    def __init__(self, test_name=None, runner=None, patterns=None, *args, **kwargs):
        if not test_name or not runner:
            raise AttributeError("Missing test_name or runner argument")

        self.test_name = test_name
        self.runner = runner
        if patterns:
            self.patterns = patterns
        super(AutoreloadHandler, self).__init__(*args, **kwargs)

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        self.runner.handle_file_change(self.test_name, event)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)


class PolytesterRunner(object):

    def _print_error(self, message):
        puts(colored.red("ERROR: ") + message)

    def _fail(self, message):
        self._print_error(message)
        if not self.autoreload:
            sys.exit(1)

    def _nice_traceback_and_quit(self):
        puts("Traceback: ")
        with indent(2):
            puts(traceback.format_exc(limit=1))
        sys.exit(1)

    def strip_ansi_colors(self, string):
        ansi_escape = re.compile(r's/\x1b\[[0-9;]*m//g')
        return ansi_escape.sub('', repr(string))

    def __init__(self, arg_options):
        # arg_options is expected to be an argparse namespace.

        # Parse out arg_options.
        self.run_thread = None
        self.autoreload = arg_options.autoreload
        self.verbose = arg_options.verbose
        config_file = arg_options.config_file
        wip = arg_options.wip
        run_parallel = arg_options.parallel
        if run_parallel:
            parallel_n = int(arg_options.parallel[0])
            parallel_m = int(arg_options.parallel[1])
            if parallel_m < 1:
                run_parallel = False
            else:
                parallel_modulo = parallel_n % parallel_m
        if arg_options.test_names:
            tests_to_run = arg_options.test_names.split(",")
            all_tests = False
        else:
            all_tests = True

        # Set up variables.
        self.processes = {}
        self.results = {}
        self.threads = {}

        # Detect and configure parsers
        if self.autoreload:
            os.system('clear')

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

            current_num = 0
            for name, options in self.test_config.items():
                run_suite = False
                current_num += 1
                skip_message = ""
                if run_parallel:
                    if parallel_modulo == current_num % parallel_m:
                        run_suite = True
                    else:
                        skip_message = ""
                elif self.autoreload:
                    if "watch_glob" in options:
                        if all_tests or name in tests_to_run:
                            run_suite = True
                    else:
                        skip_message = "no watch_glob"
                elif all_tests or name in tests_to_run:
                    if not wip or "wip_command" in options:
                        run_suite = True
                    else:
                        if wip:
                            skip_message = "no wip_command"

                if run_suite:
                    if wip:
                        if "wip_command" not in options:
                            self._fail("%s is missing a wip_command." % name)
                        else:
                            command = options["wip_command"]
                            del options["wip_command"]
                            try:
                                del options["command"]
                            except KeyError:
                                pass

                    else:
                        if "command" not in options:
                            self._fail("%s is missing a command." % name)
                        else:
                            command = options["command"]
                            del options["command"]
                            try:
                                del options["wip_command"]
                            except KeyError:
                                pass

                    if "short_name" not in options:
                        options["short_name"] = name

                    if "parser" in options:
                        options["autodetected"] = False
                        try:
                            components = options["parser"].split(".")
                            if len(components) < 2:
                                self._fail(
                                    "'%s' in the %s section of tests.yml does not have both a module and a class."
                                    "Please format as module.ParserClass." % (options["parser"], name)
                                )
                            else:
                                module = ".".join(components[:-1])
                                class_name = components[-1]

                            i = importlib.import_module(module)
                            options["parser"] = i.getattr(class_name)()
                        except ImportError:
                            self._fail(
                                "Unable to find a parser called '%s' for %s on your PYTHONPATH." %
                                (options["parser"], name)
                            )
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

        self.config = Bunch(
            autoreload=False,
            failfast=False,
            verbose=False,
            wip=False,
        )

    def add(self, test_command, parser=None, watch_glob=None, watch_dir=None, short_name=None, autodetected=None):
        if not short_name:
            short_name = test_command.split(" ")[0]
        if not parser:
            parser = DefaultParser()
        if not watch_dir:
            watch_dir = "."

        self.tests.append(Bunch(
            command=test_command,
            parser=parser,
            autodetected=autodetected,
            watch_glob=watch_glob,
            watch_dir=watch_dir,
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

    def handle_file_change(self, test_name, event):
        os.system('clear')
        puts("Change detected in '%s' in the %s suite. Reloading..." % (event.src_path.split("/")[-1], test_name))
        self.kick_off_tests()

    def watch_thread(self, test):
        event_handler = AutoreloadHandler(runner=self, test_name=test.short_name, patterns=[test.watch_glob, ])
        observer = Observer()
        observer.schedule(event_handler, test.watch_dir, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            sys.exit(1)
        observer.join()

    def handle_keyboard_exception(self):
        puts()
        puts(colored.yellow("Keyboard interrupt. Stopping tests."))
        sys.exit(1)

    def set_up_watch_threads(self):
        if self.autoreload and self.threads == {}:
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
            # TODO: handle multiple CIs
            for t in self.tests:
                self.threads[t.short_name] = Thread(target=self.watch_thread, args=(t,),)
                self.threads[t.short_name].daemon = True
                self.threads[t.short_name].start()

    def kick_off_tests(self):
        if hasattr(self, 'processes'):
            for name, p in self.processes.items():
                p.terminate()

        if self.run_thread:
            self.run_thread.terminate()

        self.run_thread = Process(target=self.run_tests)
        self.run_thread.start()

    def run(self):
        if self.autoreload:
            self.kick_off_tests()
            while True:
                time.sleep(1)
        else:
            self.run_tests()

    def run_tests(self):
        try:
            puts()
            puts("Running tests...")
            self.results = {}
            self.processes = {}

            if self.verbose:
                with indent(2):
                    for t in self.tests:
                        p = subprocess.Popen(t.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        self.processes[t.short_name] = p
                        self.results[t.short_name] = Bunch(
                            output=u"",
                            return_code=None,
                            parser=t.parser,
                            test_obj=t,
                            passed=None,
                        )
                        while p.poll() is None:
                            line = self.non_blocking_read(p.stdout)
                            if line:
                                self.results[t.short_name].output += "\n%s" % line.decode("utf-8")
                                puts(line.decode("utf-8"))
                            time.sleep(0.5)

                        if p.returncode is not None:
                            try:
                                out, err = p.communicate()
                            except ValueError:
                                out = None
                                err = None

                            if out:
                                self.results[t.short_name].output += "\n%s" % out.decode("utf-8")
                                puts(out.decode("utf-8"))
                            if err:
                                self.results[t.short_name].output += "\n%s" % err.decode("utf-8")
                                puts(err.decode("utf-8"))
                            self.results[t.short_name].return_code = p.returncode
                            if t.short_name in self.processes:
                                del self.processes[t.short_name]
            else:
                for t in self.tests:
                    self.processes[t.short_name] = subprocess.Popen(
                        t.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    self.results[t.short_name] = Bunch(
                        output=u"",
                        return_code=None,
                        parser=t.parser,
                        test_obj=t,
                        passed=None,
                    )
                while len(self.processes.items()) > 0:
                    for name, p in list(self.processes.items()):
                        while p.poll() is None:
                            line = self.non_blocking_read(p.stdout)
                            if line:
                                self.results[name].output += "\n%s" % line.decode("utf-8")
                            time.sleep(0.5)

                        if p.returncode is not None:
                            out, err = p.communicate()
                            if out:
                                self.results[name].output += "\n%s" % out.decode("utf-8")
                            if err:
                                self.results[name].output += "\n%s" % err.decode("utf-8")
                            self.results[name].return_code = p.returncode
                            if name in self.processes:
                                del self.processes[name]

            all_passed = True
            with indent(2):
                for t in self.tests:
                    name = t.short_name
                    r = self.results[name]
                    r.cleaned_output = self.strip_ansi_colors(r.output)

                    r.passed = r.parser.tests_passed(r)
                    pass_string = ""
                    if not r.passed:
                        all_passed = False
                        try:
                            if hasattr(r.parser, "num_failed"):
                                pass_string = " %s" % r.parser.num_failed(r)
                            else:
                                pass_string = " some"

                            if hasattr(r.parser, "num_total"):
                                pass_string += " of %s" % r.parser.num_total(r)
                            else:
                                pass_string += ""
                        except:
                            pass
                        puts(colored.red("✘ %s:%s tests failed." % (name, pass_string)))

                        with indent(2):
                            puts(u"%s" % r.output)
                    else:
                        try:
                            if hasattr(r.parser, "num_passed"):
                                pass_string = " %s" % r.parser.num_passed(r)
                            else:
                                pass_string = ""
                        except:
                            pass
                        puts(colored.green("✔" + " %s:%s tests passed." % (name, pass_string)))
            if all_passed:
                puts()
                puts(colored.green("✔ All tests passed."))
                puts()
                if self.autoreload:
                    while True:
                        time.sleep(1)
            else:
                self._fail("✘ Tests failed.")
                puts()
                if not self.autoreload:
                    sys.exit(1)
                else:
                    while True:
                        time.sleep(1)
        except KeyboardInterrupt:
            self.handle_keyboard_exception()

    def start(self):
        self.set_up_watch_threads()
        self.run()