![Polytester Logo](https://cloud.githubusercontent.com/assets/200635/5837495/4b37ce74-a1b2-11e4-8eb7-0b7e8b05e52b.png)


Polytester is a simple, groovy multi-language test runner.

It makes it easy to run tests in your polygot projects.  Run python, javascript, ruby, java, and more side by side.  It abstracts away the pain and config and lets you just get get developing. Easily.

Polytester Just Works with any testing framework that runs in the shell (yo, that's pretty much everything on the planet), and ships with extra-smooth integration for lots of common frameworks including django, karma, protractor, and more.
Polytester was built by [Steven Skoczen](http://stevenskoczen.com) at [BuddyUp](http://buddyup.org).  If you're in school, and could use a study buddy, check us out!

[![Build Status](https://travis-ci.org/skoczen/polytester.svg)](https://travis-ci.org/skoczen/polytester) ![Pypi Badge](https://badge.fury.io/py/polytester.png)   ![Downloads Badge](https://pypip.in/d/polytester/badge.png)

# Installation

```
pip install polytester
```

# Getting started


1. Create a tests.yml file. The following example shows django, protractor, and karma (jasmine) tests.
    ```yml
    api:
        command: python manage.py test
    js:
        command: karma start karma.conf.js
    e2e:
        command: protractor
    ```


2. Run `polytester`

    ```
    $ polytester
    Detecting...
      ✔ api detected as django tests.
      ✔ e2e detected as protractor tests.
      ✔ js detected as karma tests.
    Running tests...
      ✔ api - 35 tests passed.
      ✔ e2e - 17 tests passed.
      ✔ js - 23 tests passed.

    ✔ All tests passed.
    ```

    Note that the status code returned is correct, so you can just dump this on your CI service, and be done.

That's it. There is no step 3.

# Because everyone loves animated gifs

Here's the above - polytester installed, configured, and running in less than 30 seconds:

![install](https://cloud.githubusercontent.com/assets/200635/5915016/3d92455e-a632-11e4-9ff4-d3553b6774c0.gif)

# Supported Frameworks

Any test framework that returns standard error codes will work out of the box.  That's pretty much everything.

In addition, polytester progressively upgrades to extra-nice output for the frameworks it has parsers for. As of v1.0, the following parsers are built-in, and it's simple to write your own.  More are very much welcome via PR, and as you [can see below](#writing-a-custom-parser), writing them is easy!

- [Django](https://www.djangoproject.com/)
- [Karma](http://karma-runner.github.io/)
- [Protractor](http://angular.github.io/protractor/)
- [Python Nose](https://nose.readthedocs.org/en/latest/)
- [Python py.test](http://pytest.org/latest/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Rspec](http://rspec.info/)
- [Salad](https://github.com/salad/salad)

But again, for extra clarity - if your test runner returns normal output codes, you can just drop it in and it'll work great.

# Command-line options

## Running polytester.

Polytester will respond to `pt` or `polytester`.  Both do the exact same thing.

## Options

There are a variety of options to make development simple.

- `polytester foo` or `polytester foo,bar` just runs the test suite(s) specified.
- `--autoreload` or `--ci` watches all files specified in a `watch_glob`, and immediately runs the relevant suite on file changes. Any running tests are killed.
- `--wip` runs tests flagged as "work in progress" by running the `wip_command` for all suites that specify it.
- `--verbose` or `-v` dumps all output to the shell.  To prevent collisions, when run in this mode, test suites are run in serial, instead of the normal parallel execution.
- `--parallel n m` only runs test chunk `n` of `m`, for parallel build test environments. 
- `--config foo.yml` specifies a different location for the config file.  Default is `tests.yml`


# Advanced usage

If you want to get more out of polytester, there's more under the surface, including wip, autoreload, pass/fail counts, custom frameworks, and more.

Here's all the goodness.


## Autoreload

Having your tests auto-run when files change is super-handy.  With polytester, it's simple.

1. Specify a `watch_glob` (and optionally a `watch_dir`) in your `tests.yml`

    ```yml
    python: 
        command: nosetests
        watch_glob: "*.py"
        watch_dir: api
    ```

2. Run with `--autoreload`

    ```bash
    polytester --autoreload
    ```

Any time you change a file that matches the glob, polytester will immediately run the matching test suite.  Any running tests for that suite will be immediately killed.

Notes:

- If `watch_dir` is not specified, it defaults to the current directory.
- To specify multiple file types, you can use standard unix globs, i.e. `*.html;*.js;*.css`.
- Running with `--autoreload` will only run the tests that have a `watch_glob` in their config.  Which makes sense once you think about it, but might suprise you at first glance.

Autoreload in action:

![ci-small-2](https://cloud.githubusercontent.com/assets/200635/5915017/3dce3852-a632-11e4-8c4e-ade981d98a71.gif)

## WIP (Work in Progress) tests

Being able to tag and run certain groups of tests becomes a huge develoment time-saver for larger codebases. Polytester makes it simple.   Just specify a `wip_command`, and run with `--wip`.

1. Specify a `wip_command` in your `tests.yml`

    ```yml
    python: 
        command: nosetests
        wip_command: nosetests -a wip
    ```

2. Run with `--wip`

    ```bash
    polytester --wip
    ```

That's it!

## Parallel Execution

If you're running on a ci platform with parallel builds, like [CircleCI](http://circleci.com), the `--parallel` option can save you some time.

Just set up your build config to use it, and pass in the appropriate shell variables.

For CircleCI, just set your `circle.yml` to:
```yml
test:
  override:
    - polytester --parallel $CIRCLE_NODE_INDEX $CIRCLE_NODE_TOTAL:
        parallel: true
```

And you're all set.  Your test suites will split out automatically, according to the number of build containers you have.


## Specifying test frameworks

If you're using the default test command for any supported frameworks, polytester just detects the right one, and you're on your way.  However, if you're using a custom runner, or something a bit special, you can easily just specify which parser polytester should use.

Let's say for reasons too complex to explain, I have a custom wrapper around my nose script. No problem.  In my `tests.yml`, I just tell polytester to expect nose output.


```yml
python: 
    command: my_custom_nose_script.sh
    parser: polytester.NoseParser
```

Now, when you run, you get this output:

```bash
$ polytester
Detecting...
  ✔ python specified as nose tests.

Running tests...
  ✔ python: 47 tests passed.

✔ All tests passed.
```

Here's the full list of built-in parsers:

- `DefaultParser` (Just listens to exit codes, no support for number of tests.)
- `NoseParser`
- `DjangoParser`
- `KarmaParser`
- `ProtractorParser`
- `SaladParser`

If you need a parser not in this list, you can make it by writing a few simple functions. See [Custom parsers](#writing-a-custom-parser) below.



## All options
Here's a yml file, with everything, just for easy reference.:

```yml
python: 
    command: nosetests
    wip_command: nosetests -a wip
    watch_glob: "*.py;*.html"  # Note you do need quotes because of the *.
    watch_dir: my_app/foo
    parser: my_parsers.MyNiftyCustomNoseParser
```


## Writing a Custom Parser

Any test framework that returns standard error codes (0 for pass, non-zero for fail) will Just Work out of the box. However, if you want fancy test counts (and someday more), writing a custom parser is easy.

Just write a class that inherits `DefaultParser`, stick it somewhere on your python path, put in in your `tests.yml` file, and you're good to go.  Here's an example for pep8.

**Please note:** if you're writing for a common framework/use case, please submit a pull request!


1. Write your own parser.

    my_parsers.py
    ```python
    from polytester.parsers import DefaultParser

    class MyCustomParser(DefaultParser):
        name = "my custom"

        def tests_passed(self, result):
            # Required, the code below is the default in DefaultParser
            return result.return_code == 0

        def num_failed(self, result):
            # Optional.
            m = re.match("(\d+) failed", result.output)
            return int(m.group(0))

        def num_passed(self, result):
            # Optional.
            return self.num_total(result) - self.num_failed(result)

        def num_total(self, result):
            # Optional.
            m = re.match("(\d+) total", result.output)
            return int(m.group(0))

        def command_matches(self, command_string):
            # Optional, used for trying to auto-detect the test framework.
            # Since this is totally custom, we just return false
            return False
    ```

    For reference, `results` is an object with the following attributes:

    - `output` - The stdout and stderr, in the order produced while running.
    - `cleaned_output` - `output`, but stripped of all ANSI colors and escape codes.
    - `return_code` - The return code.
    - `passed` - A boolean indicating if the tests have passed. `None` until a definitive answer is known.
    - `parser` - An instance of the parser class. (i.e. you can call `result.parser.num_failed(result)`).


2. Specify it in your test.yml file.

    ```yml
    custom: 
        command: run_tests.sh
        parser: my_parsers.MyCustomParser
    ```

3. Run your tests like normal!

    ```bash
    $ polytester
    Detecting...
      ✔ custom specified as my custom tests.

    Running tests...
      ✔ custom: 18 tests passed.

    ✔ All tests passed.
    ```

# When things go wrong.

When tests fail, polytester just falls back to the helpful output your test frameworks already give you:

```
$ polytester
Detecting...
  ✔ api detected as django tests.
  ✔ e2e detected as karma tests.
  ✔ js detected as protractor tests.
Running tests...
  ✘ api - 1 of 35 tests failed.

    ======================================================================
    FAIL: test_addition (events.tests.SampleTest)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/me/project/events/tests.py", line 6, in test_addition
        self.assertEquals(1+1, 3)
    AssertionError: 2 != 3

    ----------------------------------------------------------------------
    Ran 35 tests in 1.642s

    FAILED (failures=1)

  ✔ e2e - 17 tests passed.
  ✔ js - 23 tests passed.

✘ Tests failed
```


# Built on the shoulders of giants

Polytester leverages some fantastic libraries.  It wouldn't exist without them.

- [Clint](https://github.com/kennethreitz/clint) for all the nice shell output,
- [Watchdog](https://github.com/gorakhargosh/watchdog) for the magical file watching, and
- [PyYAML](http://pyyaml.org/) because nobody should have to think about parsing yaml files again.

Polytester has also has had help from lots of coders. Alphabetically:

- [brandoncazander](https://github.com/brandoncazander) gave you more robust ansi parsing across older versions of python.
- [calebmeyer](https://github.com/calebmeyer) gave you rspec support.
- [joshfriend](https://github.com/joshfriend) added py.test support, and spotted a bug on python 2.7.x with `--ci`.


# Releases

#### 1.2.0 - March 6, 2015

- Pretty hefty rewrite of how the test runner and watch threads are handled, to fix the incompatabilities reported by [alecklandgraf](https://github.com/alecklandgraf).


#### 1.1.3 - March 3, 2015

- Rspec parser, thanks to [calebmeyer](https://github.com/calebmeyer).
- Improvements to ansi parsing across older versions of python, thanks to (brandoncazander)[https://github.com/brandoncazander].

#### 1.1.2 - Feb 5, 2015

- Bugfix to `--ci` on python 3.4.

#### 1.1.1 - Jan 30, 2015

- Copypasta bugfix to django parser.

#### 1.1 - Jan 30, 2015

- The start of a test suite for polytester, thanks entirely to [joshfriend](https://github.com/joshfriend).
- Parser for the python unittest runner added by [joshfriend](https://github.com/joshfriend).
- Bugfix to nose parser, by [joshfriend](https://github.com/joshfriend).
- Fixed a bug in test output introduced by 1.0.2.  Thanks to [joshfriend](https://github.com/joshfriend) for the report.
- Noticing a pattern?  That pattern is that people like [joshfriend](https://github.com/joshfriend) are what makes open-source awesome.
- All code now passes pep8.

#### 1.0.2 - Jan 30, 2015

- Adds support for py.test, thanks to [joshfriend](https://github.com/joshfriend).
- Fixes support for KeyboardInterrupts on python 2.7.x, thanks to the report by [joshfriend](https://github.com/joshfriend).

#### 1.0.1 - Jan 27, 2015 

- Bugfix on --parallel.

#### 1.0 - Jan 27, 2015 - "Rick James"

- All RDD features in, we're using polytester in production.

#### 0.1.3 - Jan 22, 2015

- Everything but `--ci`, `--failfast`, and a couple parsers is in.

#### 0.1.2 - Jan 21, 2015

- Works on python 3. First stable release!

#### 0.1.1 - Jan 21, 2015

- Fixes inclusion of wsgiref, which breaks python 3 due to a print.

#### 0.1 - Jan 21, 2015

- Initial release.  Basic functionality works, only Django parser is in. Very much RDD.


# Into the Future

As with all the open-source projects I run, I leave the future pretty open to what the people who use the project request, and the PRs that are sent.

But here's a short list of things that are rolling around in my head as future features:

- Full test coverage.  We've got a good start, but 100% (or near) coverage with some integration tests is the long-term goal.
- Better parsing of test outputs, to just list failed test file names and line numbers or other fancy niceties.
- xUnit output
- `--failfast`, for super-quick iteration.
- The ability for parsers to do better parallelization introspection (based on globs, etc)
- Whatever great stuff you bring to the table!

# Contributing

### PRs Welcome!
If you want to add support for a language or framework, those PRs are *always* welcome.  

If you have a bigger idea, just pop open an issue, and we'll talk it through, so we don't cross wires when the PR comes!

### Culture

Anyone is welcome to contribute to polytester, regardless of skill level or experience. To make polytester the best it can be, we have one big, overriding cultural principle:

**Be kind.**

Simple. Easy, right?

We've all been newbie coders, we've all had bad days, we've all been frustrated with libraries, we've all spoken a language we learned later in life. In discussions with other coders, PRs, and CRs, we just give each the benefit of the doubt, listen well, and assume best intentions. It's worked out fantastically.

This doesn't mean we don't have honest, spirited discussions about the direction to move polytester forward, or how to implement a feature. We do. We just respect one other while we do it. Not so bad, right? :)

### Testing
A `Makefile` is included for your testing convenience. Here's a few sample commands:

    $ make test       # run the tests on the default python version (3.4)
    $ make test-all   # run tests on all supported pythons (2.7, 3.3, 3.4)
    $ make flake8     # run a pep8/pyflakes style/syntax check
    $ make clean      # remove cached/compiled python test data
    $ make clean-all  # rebuild the virtualenv from scratch

The `Makefile` will take care of creating a [virtualenv](https://pypi.python.org/pypi/virtualenv) and installing the required dependencies (and keep them up to date).

If you don't have all the supported versions of Python installed, don't worry! Push your changes to a branch, open a pull-request, and [Travis](https://travis-ci.org/) will run the tests on your behalf.
