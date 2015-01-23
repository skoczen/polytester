![Polytester Logo](https://cloud.githubusercontent.com/assets/200635/5837495/4b37ce74-a1b2-11e4-8eb7-0b7e8b05e52b.png)


Polytester is a simple multi-language test runner. Groovy.

It makes it easy to run tests in your polygot projects.  Run python, javascript, ruby, java, and more side by side. Easily.

Polytester works with any testing framework that runs in the shell (yo, that's pretty much everything on earth), and ships with extra-special support for lots of common frameworks including django, jasmine, karma, and more.

Polytester was built by [Steven Skoczen](http://stevenskoczen.com) at [BuddyUp](http://buddyup.org).  If you're in school could use a buddy, check us out!

> NOTE:  Polytester is being built via [Readme Driven Development](http://tom.preston-werner.com/2010/08/23/readme-driven-development.html), so as of January 22, 2015, not everything is done yet.
> 
> But I work fast.  Expect everything here to be supported soon.
> Jan 23: Everything but --ci works.  Expect that Monday.

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
      ✔ e2e detected as karma tests.
      ✔ js detected as jasmine tests.

    Running tests...
      ✔ api - 35 tests passed.
      ✔ e2e - 17 tests passed.
      ✔ js - 23 tests passed.

    ✔ All tests passed.
    ```

    Note that the status code returned is correct, so you can just dump this on your CI service, and be done.

That's it. There is no step 3.

# Supported Frameworks

Any test framework that returns standard error codes will work out of the box.  That's pretty much everything.

In addition, polytester progressively upgrades to extra-nice output for the frameworks it has parsers for. As of v0.2, the following parsers are built-in, and it's simple to write your own.  More are very much welcome via PR, and as you [can see below](#Writing-A-Custom-Parser), writing them is easy!

- [Django](https://www.djangoproject.com/)
- [Jasmine](http://jasmine.github.io/)
- [Karma](http://karma-runner.github.io/)
- [Python Nose](https://nose.readthedocs.org/en/latest/)
- [Salad](https://github.com/salad/salad)


# Command-line options

## Running polytester.

Polytester will respond to `pt` or `polytester`.  Both do the exact same thing.

## Options

There are a variety of options to make development simple.

- `polytester foo` or `polytester foo,bar` just runs the test suite(s) specified.
- `--failfast` stops running tests when the first fail is found.
- `--verbose` dumps all output to the shell.  To prevent collisions, when run in this mode, test suites are run in serial, instead of the normal parallel execution.
- `--wip` runs tests flagged as "work in progress" by running the `wip_command` for all suites that specify it.
- `--autoreload` or `--ci` watches all files specified in a `watch_glob`, and immediately runs the relevant suite on file changes. Any running tests are killed.
- `--parallel n m` only runs test chunk `n` of `m`, for parallel build test environments. 
- `--config foo.yml` specifies a different location for the config file.  Default is tests.yml


# Advanced usage

If you want to get more out of polytester, there's more under the surface, including wip, autoreload, pass/fail counts, custom frameworks, and more.

Here's all the goodness.


## Autoreload

Having your tests auto-run when files change is super-handy.  With polytester, it's simple.

1. Specify a `watch_glob` in your `tests.yml`

```yml
python: 
    command: nosetests
    watch_glob: "**/*.py"
```

2. Run with `--autoreload`

```bash
polytester --autoreload
```

Any time you change a file that matches the glob, polytester will immediately run the matching test suite.  Any running tests for that suite will be immediately killed.

**Note:** running with `--autoreload` will only run the tests that have specified `watch_glob`s.  Which makes sense once you think about it, but might suprise you at first glance.


## WIP (Work in Progress) tests

Being able to tag certain groups of tests becomes a huge develoment time-saver for larger codebases. Polytester makes it simple.   Just specify a `wip_command`, and run with `--wip`.

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

If you need a parser not in this list, you can make it simply. See [Custom parsers](#Writing-A-Custom-Parser) below.



## All options
Here's a yml file, with everything, just for easy reference.:

```yml
python: 
    command: nosetests
    wip_command: nosetests -a wip
    watch_glob: "**/*.py"
    parser: my_parsers.MyNiftyCustomNoseParser
```


## Writing a Custom Parser

Any test framework that returns standard error codes (0 for pass, non-zero for fail) will Just Work out of the box. However, if you want fancy test counts (and someday more), writing a custom parser is easy.

Just write a class based on `DefaultParser`, stick it somewhere on your python path, put in in your `tests.yml` file, and you're good to go.  Here's an example for pep8.

**Please note:** if you're writing for a common framework/use case, please submit a pull request!


1. Write your own parser.

    my_parsers.py
    ```python
    from polytester.parsers import DefaultParser

    class Pep8Parser(DefaultParser):
        name = "my custom pep8"

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

        def command_matches(self, command_string):
            # Optional, used for trying to auto detect the test framework.
            # Since this is totally custom, we just return false
            return False
    ```

    For reference, `result` is an object with the following attributes:

    - `results.output` - The stdout and stderr, in the order produced while running.
    - `results.retcode` - The return code.
    - `results.parser` - An instance of the parser class. (i.e. you can call `result.parser.num_failed(result)`).
    - `results.passed` - A boolean indicating if the tests have passed. `None` until a definitive answer is known.


2. Specify it in your test.yml file.

    ```yml
    pep8: 
        command: pep8
        parser: my_parsers.Pep8Parser
    ```

3. Run your tests like normal!

    ```bash
    $ polytester
    Detecting...
      ✔ pep8 specified as my custom pep8 tests.

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
  ✔ e2e detected as karma tests.
  ✔ js detected as jasmine tests.

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


# Into the Future

As with all the open-source projects I run, I leave the future pretty open to what the people who use the project request, and the PRs that are sent.

But here's a short list of things that are rolling around in my head as future features:

- Better parsing of test outputs, to just list failed test file names and line numbers or other fancy niceties.
- xUnit output
- The ability for parsers to do better parallelization introspection (based on globs, etc)
- Whatever great stuff you bring to the table!

## Contributing

If you want to add support for a language or framework, those PRs are *always* welcome.  

If you have a bigger idea, just pop open an issue, and we'll talk it through, so we don't cross wires when the PR comes!

## Culture

Anyone is welcome to contribute to polytester, regardless of skill level or experience. To make polytester the best it can be, we have one big, overriding cultural principle:

**Be kind.**

Simple. Easy, right?

We've all been newbie coders, we've all had bad days, we've all been frustrated with libraries, we've all spoken a language we learned later in life. In discussions with other coders, PRs, and CRs, we just give each the benefit of the doubt, listen well, and assume best intentions. It's worked out fantastically.

This doesn't mean we don't have honest, spirited discussions about the direction to move polytester forward, or how to implement a feature. We do. We just respect one other while we do it. Not so bad, right? :)

