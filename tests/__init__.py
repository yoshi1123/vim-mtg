# Discovery works with just this file (e.g., `python3 -m unittest`).
#
# Add to file for non-discovery execution (e.g., `python3 -m unittest
# test_file.py`):
#
#   from tests import load_tests
#   load_tests.__module__ = __name__

import os
import sys
import unittest
from fnmatch import fnmatchcase
from inspect import findsource


def sort_suite_by_line(tests):
    def tcase_line(c):
        return findsource(list(c)[0].__class__)[1]

    def tfn_line(f):
        return getattr(f.__class__,
                       f._testMethodName).__code__.co_firstlineno
    cases = []
    for tc in tests:
        if len(list(tc)) > 0:
            cases.append(tc)
            # import ipdb; ipdb.set_trace()
    cases = sorted(cases, key=tcase_line)
    suite = unittest.TestSuite()
    for tms in cases:
        suite.addTests(sorted(tms, key=tfn_line))
    return suite


class OrderLoader(unittest.TestLoader):
    """TestLoader that sorts tests by their order in file."""

    def loadTestsFromModule(self, module, *args, pattern=None, **kws):
        """Return a suite of all test cases contained in the given module"""
        tests = super(OrderLoader, self).loadTestsFromModule(module, pattern=pattern)
        tests = [tests]
        return sort_suite_by_line(tests)


def load_tests(loader, tests, pattern):
    # tests: [TestSuite1, TestSuite2]
    # TestSuite: [testMethod1, testMethod2]
    # [ [testMethod1, testMethod2], ... ]
    #
    # A list of `TestSuite`s. Each `TestSuite` represents a `TestCase`, with a
    # list of methods in the `TestCase`.

    if load_tests.__module__ != 'tests':

        # a module (tests already loaded without discovery)
        # return reordered test cases
        return sort_suite_by_line(tests)

    else:

        # discovery
        this_dir = os.path.dirname(__file__)
        orderloader = OrderLoader()
        orderloader.testNamePatterns = loader.testNamePatterns
        tests = orderloader.discover(start_dir=this_dir, pattern=pattern)
        return tests
