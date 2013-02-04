""" hammock.runner

    TODO: not generic
"""
import platform

from corkscrew.runner import tornado, flask
from hammock.utils import report

if platform.node() in ['dosojin']: # fixme: abstract
    report("Using flask default as server")
    run = flask
else:
    report("Using tornado as server")
    run = tornado
