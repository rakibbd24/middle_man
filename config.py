""" Flask configuration."""
import os
import sys


class ProdConfig():
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class DevConfig():
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True