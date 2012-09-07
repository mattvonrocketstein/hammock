#!/usr/bin/env python
""" setup.py for hammock

      this pattern stolen from kinbaku's setup.py
"""

import os
from os.path import expanduser

try:
    from setuptools import setup, find_packages
    have_setuptools = True
except ImportError:
    from distutils.core import setup
    def find_packages():
        return [
            'hammock',
        ]
    have_setuptools = False

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

if have_setuptools:
    add_keywords = dict( entry_points = \
                         { 'console_scripts': \
                           ['hammock = hammock.bin._hammock:entry', ]
                         }, )
else:
    add_keywords = dict( scripts = ['hammock'], )

setup(
    name         ='hammock',
    version      = '.1',
    description  = 'stuff for couchdb+flask',
    author       = 'mattvonrocketstein, in the gmails',
    url          = 'one of these days',
    license      = 'BSD License',
    package_dir  = {'': 'lib'},
    packages     = find_packages('lib'),
    long_description = __doc__,
    keywords = 'couch flask',
    platforms = 'any',
    zip_safe = False,
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 000 - Experimental',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent', ],
    cmdclass = {'build_py': build_py},
    **add_keywords
)
