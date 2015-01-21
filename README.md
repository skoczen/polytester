![Polytester Logo](https://cloud.githubusercontent.com/assets/200635/5837495/4b37ce74-a1b2-11e4-8eb7-0b7e8b05e52b.png)


Polytester is a simple multi-language test runner.

It makes it easy to run tests in your polygot projects.  Run python, javascript, ruby, java, and more side by side. Easily.

Polytester ships with lots of batteries included, including support for django, jasmine, and karma.

It's also easily extensible to any testing framework that runs in the shell (that'd be pretty much everything), and pull requests to add new languages and frameworks are welcome!

Polytester was built by [Steven Skoczen](http://stevenskoczen.com) at [BuddyUp](http://buddyup.org).  If you're in school, check us out!

> NOTE:  Polytester is being built via [Readme Driven Development](http://tom.preston-werner.com/2010/08/23/readme-driven-development.html), so as of January 22, 2015, not everything is done yet.
> 
> But I work fast.  Expect everything here to be supported soon.

# Installation

```
pip install polytester
```

# Getting started

1. Create a tests.yml file. The following example shows django, jasmine, and protractor tests.

    ```yml
    api:
        command: python manage.py test
    js:
        command: jasmine
    e2e:
        command: karma e2e
    ```


2. Run `polytester`

    ```
    $ polytester
    Detecting...
      ✔ api detected as django tests.
      ✔ js detected as jasmine tests.
      ✔ e2e detected as karma tests.

    Running tests...
      ✔ api - 35 tests passed.
      ✔ js - 23 tests passed.
      ✔ e2e - 17 tests passed.

    ✔ All tests passed.
    ```

    Note that the status code returned is correct, so you can just dump this on your CI service, and be done.

That's it.

# Supported Parsers

As of v0.1, polytester supports the following parsers.  More are welcome via PR, and as you'll see below, writing them is easy!

- [Python Nose](https://nose.readthedocs.org/en/latest/)
- [Django](https://www.djangoproject.com/)
- [Jasmine](http://jasmine.github.io/)
- [Karma](http://karma-runner.github.io/)
- [Salad](https://github.com/salad/salad)


# Command-line options

## Running polytester.

Polytester will respond to `pt` or `polytester`.  Both do the exact same thing.

## Options

There are a variety of options to make development simple.

- `--failfast` - stops running tests when the first fail is found.
- `--verbose` - dumps all output to the shell.  To prevent collisions, when run in this mode, tests are run in serial, instead of the normal parallel execution.
- `--wip` - if supported by the test runner, runs test flagged as "work in progress"
- `--ci` - (requires watch_glob) watches a file glob, and immediately runs tests on file change. Any running tests are killed.
- `--autoreload` - alias for `--ci`
- `--parallel n m` - In parallel build test environments, only runs test chunk `n` of `m`
- `--config foo.yml` - specifies a different location for the config file.  Default is tests.yml
- `--[test_name]` - just runs the test(s) specified. I.e `--e2e`.  Comma-separating is fine.


# Advanced usage

If you want to get more out of polytester, there's more under the surface, including pass/fail counts, support for custom frameworks, autoreload and more.

Here's all the goodness.


## Specifying test frameworks

If you're using the default test command for any supported frameworks, polytester just detects the right one, and you're on your way.  However, if you're using a custom runner, or something a bit special, you can easily just specify which parser polytester should use.

Let's say for reasons too complex to explain, I have a custom wrapper around my nose script. No problem.  In my `tests.yml`, I just specify it.


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
  ✔ python passed.

✔ All tests passed.
```

Here's the full list of built-in parsers:

- `DefaultParser` (Just listens to exit codes, no support for number of tests.)
- `NoseParser`
- `DjangoParser`
- `JasmineParser`
- `KarmaParser`
- `SaladParser`

If you need a parser not in this list, you can make it simply. See [Custom parsers](#Custom-parsers) below.

### Autoreload

Having your tests auto-run when files change is super-handy.  With polytester, it's simple.

1. Specify a `watch_glob` in your `tests.yml`

```yml
python: 
    command: nosetests
    type: nose
    watch_glob: **/*.py
```

2. Run with `--autoreload`

```bash
polytester --autoreload
```

Any time you change a file that matches the glob, polytester will immediately run those the matching test suite.  Any running tests will be immediately killed.


### Custom parsers

If you've got a custom testing framework or one that's not bundled yet, no problem. 

Just write your own output parser class, stick it somewhere on your python path, put in in your `tests.yml` file, and you're good to go.  Here's an example for pep8.

**Please note:** if you're writing for a common framework, please submit a pull request!


1. Write your own parser

    my_parsers.py
    ```python
    from polytester.parsers import DefaultParser

    class Pep8Parser(DefaultParser):

        def tests_passed(self, result):
            # Required, the code below is the default in DefaultParser
            return result.retcode == 0

        def num_failed(self, result):
            # Optional.
            return re.match("<?foo_int:\d> found", result.output)

        def num_passed(self, result):
            # Optional.
            return re.match("<?foo_int:\d> found", result.output)

        def num_total(self, result):
            # Optional.
            return re.match("<?foo_int:\d> found", result.output)

        def command_matches(self):
            # Optional, used for trying to auto detect the test framework.
            # Since this is totally custom, we just return false
            return False
    ```

    For reference, `result` is an object with the following attributes:

    - `results.output` - The stdout and stderr, in the order produced while running.
    - `results.retcode` - The return code.
    - `results.parser` - An instance of the parser class. (i.e. you can call `result.parser.num_failed(result)`).
    - `results.passed` - A boolean indicating if the tests have passed. `None` until a definitive answer is known.


2. Specify it in your test.yml file

    ```yml
    pep8: 
        command: pep8
        parser: my_parsers.Pep8Parser
    ```

3. Run your tests like normal!

    ```bash
    $ polytester
    Detecting...
      ✔ pep8 specified as pep8 tests.

    Running tests...
      ✔ pep8 passed.

    ✔ All tests passed.
    ```

# When things go wrong.

When tests fail, polytester just falls back to the helpful output your test frameworks already give you:

```
$ polytester
Detecting...
  ✔ api detected as django tests.
  ✔ js detected as jasmine tests.
  ✔ e2e detected as karma tests.

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

  ✔ js - 23 tests passed.
  ✔ e2e - 17 tests passed.

✔ All tests passed.
```


# Into the Future

As with all the open-source projects I run, I leave the future pretty open to what the people who use the project request, and the PRs that are sent. 

But here's a short list of things that are rolling around in my head as future features:

- Better parsing of test outputs, to just list failed test file names and line numbers
- xUnit output
- The ability for parsers to do better parallelization introspection (based on globs, etc)
- Whatever great stuff you bring to the table!
