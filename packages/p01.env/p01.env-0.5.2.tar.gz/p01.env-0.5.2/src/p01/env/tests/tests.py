###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 5239 2025-04-25 08:45:21Z rodrigo.ristow $
"""
from __future__ import absolute_import
from __future__ import print_function

__docformat__ = "reStructuredText"

import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             ),
        doctest.DocFileSuite('bugfix-ssl.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             ),
        doctest.DocFileSuite('checker.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             ),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
