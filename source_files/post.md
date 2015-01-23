FB: Geek warning: just finished up this new open-source tool at work. If you're a web programmer, you'll want it.  If you're everybody else, just appreciate the pun.

"Wait, what?", you're asking?  You don't just travel all the time?  Nope. I work a regular job, just like you. In Thailand. :)

Everybody, meet polytester.



One of the things I've enjoyed most at the jobs I've held has been building fantastic internal development tools, and a lot of the time, open sourcing them.  Things like [will]() and [salad](), [django-seo-js](), and [django-ajax-uploader]().  These sorts of projects are great fun, and as it's turned out, really useful to other developers.

I'm really lucky to be able to continue that work at [BuddyUp](http://www.buddyup.org), and today, there's a new one to add: polytester.

Polytester solves a really annoying small problem that I've personally seen and solved with custom code at half a dozen companies: how do we easily run *all* of our tests and get nice output, in the polygot projects we all live in?

Most folks I know these days are running some sort of js framework on the front (and therefore have some jasmine or mocha tests), some kind of backend (and have python, java, or ruby tests), and often an e2e runner like salad or protractor to assure the whole thing works.  Easily firing these up is a pain.  

Polytester soothes that pain like a 70's slow jam.

It's this easy:

```
$ pip install polytester

$ echo "
api:
    command: python manage.py test
js:
    command: jasmine
e2e:
    command: karma e2e
" > tests.yml

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

You're done.

Any test runner that outputs valid status codes (pretty much everything on earth) works out of the box, and extended support is available for a handful of languages. (And growing! Submit a PR - it's four simple functions!)

There's also support for lots of really useful dev shortcuts, like `--ci`, `--wip`, `--parallel`, and [more]().  And of course, you can easily run subsets.

```
$ polytester api,e2e
Detecting...
  ✔ api detected as django tests.
  ✔ e2e detected as karma tests.
  - js skipped.

Running tests...
  ✔ api - 35 tests passed.
  ✔ e2e - 17 tests passed.

✔ All tests passed.
```

When things go wrong, polytester just drops you back to the output you're already getting:

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

  ✔ js - 23 tests passed.
  ✔ e2e - 17 tests passed.

✘ Tests failed
```

Meet polytester.  Finally, you can dump that painful shell/fabric/rake/gulp command you've been lugging around and disco dance your bad self on to better things.