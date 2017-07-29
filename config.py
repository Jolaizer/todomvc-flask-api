# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Provides the flask config options
"""
from os import getenv, path as p
from pkutils import parse_module

PARENT_DIR = p.abspath(p.dirname(__file__))
app = parse_module(p.join(PARENT_DIR, 'app', '__init__.py'))
user = getenv('USER', 'user')

__APP_NAME__ = app.__package_name__
__EMAIL__ = app.__email__
__DOMAIN__ = 'api.todomvc.com'
__SUB_DOMAIN__ = __APP_NAME__.split('-')[-1]


class Config(object):
    HEROKU = getenv('DATABASE_URL', False)
    DEBUG = False
    TESTING = False
    DEBUG_MEMCACHE = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = frozenset([__EMAIL__])
    HOST = '127.0.0.1'

    if HEROKU:
        SERVER_NAME = '{}.herokuapp.com'.format(__APP_NAME__)
    elif getenv('DIGITALOCEAN'):
        SERVER_NAME = '{}.{}'.format(__SUB_DOMAIN__, __DOMAIN__)
        SSLIFY_SUBDOMAINS = True

    SECRET_KEY = getenv('SECRET_KEY', 'secret')
    API_METHODS = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
    API_ALLOW_FUNCTIONS = True
    API_ALLOW_PATCH_MANY = True
    ALLOW_DELETE_MANY = True
    API_RESULTS_PER_PAGE = 32
    API_MAX_RESULTS_PER_PAGE = 1024
    DEF_PORT = 5000


class Production(Config):
    db = __APP_NAME__.replace('-', '_')
    defaultdb = 'postgres://{}@localhost/{}'.format(user, db)
    DOMAIN = __DOMAIN__
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL', defaultdb)
    HOST = '0.0.0.0'


class Development(Config):
    base = 'sqlite:///{}?check_same_thread=False'
    SQLALCHEMY_DATABASE_URI = base.format(p.join(PARENT_DIR, 'app.db'))
    DEBUG = True
    DEBUG_MEMCACHE = False


class Test(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True
    DEBUG_MEMCACHE = False
