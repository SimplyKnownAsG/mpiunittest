======
MPI Unit Test
======

Tired of having your tests take too long?

Need to test MPI protocols within a given method?

Usage
=====
`mut` supports the same command line options as `unittest`. In fact, it is
completely compatible with `unittest`.

This is slow, it's not parallel at all!
-----
Couple notes on `mut`'s parallelism:

- In order for `mut` to actually run in parallel, more than 2 processors need to
  be used. This is because the master node does not perform any work, it is only
  a dispatcher, and logger (i.e. there is only one process writing to `stdout`
  or `stderr`).
- `mut` only parallelizes test suites, or groups of tests. This means that if a
  test file contains only one `unittest.TestCase`, it won't be parallelized.
  This is a good assumption for `mut`, because a `unittest.TestCase` may contain
  `setUp`, `setUpClass` or asscoated `tearDown`s which would not make sense to
  perform more than once.

Find all tests below
----
Again, basically the same as `unittest`

    $ mpiexec -n 5 python -m mpiunittest discover

This will, by default, search for files starting with `test_`.

Run a specific test file
----
Please refer to notes on parallelism from above. Basically, unless there are a
bunch of `unittest.TestCase`s in a specific test file, you'd be better off just
using `python -m unittest $*`, where `$*` is all subsequent arguments. Now,
`mut` should be nearly as fast as `unittest` in all instances, but there is some
additional overhead.

    $ mpiexec -n 5 python -m mpiunittest "a specific test file"

Features
=====

    [-] Fully compatible with `unittest`
        [X] Things I think are working
        [X] Error conditions are properly handled.
        [ ] Not sure about skips
        [ ] Not sure what happens when result.shouldStop
    [X] Only one process writes to the standard stream, so the output does not
        appear garbled.
    [ ] Custom decorators -- I think they will need to be class decorators
        [ ] `@mut.mut(<# of processors>)` -- runs the test class with the
            specified number of processors, or skips the test if there are not
            enough processors
        [ ] `@mut.long(<ranking>)` -- indicates the test class takes a long
            time to run. Highest rank is run first.
    [X] Asynchronous MPI. -- The master node asynchronously distributes tasks
        to the workers nodes.
