##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup

$Id: setup.py 5450 2025-07-10 14:00:34Z roger.ineichen $
"""
from __future__ import absolute_import
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='p01.env',
    version='0.5.2',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "Helper methods for setup a production server environment",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "p01 bootstrap setup Zope3",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/p01.env',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require = dict(
        test = [
            'p01.checker',
            ],
        ssl = [
            'backports.ssl_match_hostname',
            'ipaddress',
            ],
        gevent = [
            'gevent',
            ],
        ),
    install_requires = [
        'setuptools',
        ],
    zip_safe = False,
    )
