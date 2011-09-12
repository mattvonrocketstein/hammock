""" hammock.runner
"""
import platform

from corkscrew.runner import tornado, flask
from hammock.utils import report

if platform.node() in ['dosojin']:
    report("Using flask default as server")
    run = naive
else:
    report("Using tornado as server")
    run = tornado
