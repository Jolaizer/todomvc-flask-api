# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
    app
    ~~~

    Provides the flask application
"""
from functools import partial
from json import JSONEncoder, dumps
from os import path as p, getenv

import config

from savalidation import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

from flask import Flask
from flask_cors import CORS
from flask_sslify import SSLify
from flask_caching import Cache
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager

from app.utils import jsonify

__version__ = '0.6.2'

__title__ = 'TodoMVC-Flask-API'
__package_name__ = 'todomvc-flask-api'
__author__ = 'Reuben Cummings'
__description__ = 'A TodoMVC API backend'
__email__ = 'reubano@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 Reuben Cummings'

API_EXCEPTIONS = [
    ValidationError, ValueError, AttributeError, TypeError, IntegrityError,
    OperationalError]

db = SQLAlchemy()
cache = Cache()
compress = Compress()


def create_app(config_mode=None, config_file=None):
    app = Flask(__name__)
    CORS(app, resources=r'/*', allow_headers='Content-Type')
    compress.init_app(app)
    cache_config = {}

    if config_mode:
        app.config.from_object(getattr(config, config_mode))
    elif config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar('APP_SETTINGS', silent=True)

    db.init_app(app)

    if app.config.get('SERVER_NAME'):
        SSLify(app)

    if app.config['HEROKU']:
        cache_config['CACHE_TYPE'] = 'saslmemcached'
        cache_config['CACHE_MEMCACHED_SERVERS'] = [getenv('MEMCACHIER_SERVERS')]
        cache_config['CACHE_MEMCACHED_USERNAME'] = getenv('MEMCACHIER_USERNAME')
        cache_config['CACHE_MEMCACHED_PASSWORD'] = getenv('MEMCACHIER_PASSWORD')
    elif app.config['DEBUG_MEMCACHE']:
        cache_config['CACHE_TYPE'] = 'memcached'
        cache_config['CACHE_MEMCACHED_SERVERS'] = [getenv('MEMCACHE_SERVERS')]
    else:
        cache_config['CACHE_TYPE'] = 'simple'

    cache.init_app(app, config=cache_config)

    @app.route('/', methods=['GET'])
    def home():
        return 'Welcome to the TodoMVC API!'

    @app.route('/reset/')
    def reset():
        db.drop_all()
        db.create_all()
        return jsonify({'message': 'Database reset!'})

    mgr = APIManager(app, flask_sqlalchemy_db=db)

    kwargs = {
        'methods': app.config['API_METHODS'],
        'validation_exceptions': API_EXCEPTIONS,
        'allow_functions': app.config['API_ALLOW_FUNCTIONS'],
        'allow_patch_many': app.config['API_ALLOW_PATCH_MANY'],
        'allow_delete_many': app.config['ALLOW_DELETE_MANY'],
        'max_results_per_page': app.config['API_MAX_RESULTS_PER_PAGE'],
        'url_prefix': ''}

    with app.app_context():
        mgr.create_api(Todo, **kwargs)

    return app

# put at bottom to avoid circular reference errors
from app.models import Todo  # noqa
