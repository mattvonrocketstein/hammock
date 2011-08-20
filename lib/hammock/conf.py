""" hammock.conf
"""
from hammock._flask import FlaskSettings
import os
class Settings(FlaskSettings):
    DEFAULT_SETTINGS = os.path.abspath(os.path.join(os.path.split(__file__)[0], "hammock.ini"))
