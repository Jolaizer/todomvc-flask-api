# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
    app
    ~~~

    Provides the flask application
"""
import re

from importlib import import_module
from os import path as p, listdir
from itertools import repeat
from json import loads, dumps
from urllib.parse import urlsplit
from datetime import datetime as dt, timedelta
from functools import wraps, partial
from ast import literal_eval

import requests

from flask import (
    current_app as app, url_for as flask_url_for, make_response, request)

from http.client import responses
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.hybrid import hybrid_property
from meza import fntools as ft

from config import Config

COLUMN_TYPES = (InstrumentedAttribute, hybrid_property)
DEF_PORT = Config.DEF_PORT


def gen_columns(table, related=True):
    """Yields all the columns of the specified `table` class.

    This includes `hybrid`_ attributes.
    .. _hybrid: docs.sqlalchemy.org/en/latest/orm/extensions/hybrid.html
    """
    for superclass in table.__mro__:
        for name, column in superclass.__dict__.items():
            if isinstance(column, COLUMN_TYPES):
                if related or (not related and hasattr(column, 'type')):
                    yield (name, column)


def get_col_names(table):
    filterer = lambda name: not (name.startswith('utc') or name == 'id')
    _columns = gen_columns(table, False)
    return sorted(name for name, col in _columns if filterer(name))


def get_init_data():
    return [
        (False, 'First task'), (False, 'Second task'), (False, 'Third task')]


def url_for(table_name=None, port=DEF_PORT, **kwargs):
    if table_name:
        endpoint = '{table}api0.{table}api'.format(table=table_name)
    else:
        endpoint = 'home'

    url = flask_url_for(endpoint, _external=True, **kwargs)

    if 'localhost/' in url:
        parsed = urlsplit(url)._asdict()
        parsed['port'] = port
        url = '{scheme}://{netloc}:{port}{path}'.format(**parsed)

    return url


def post(url, data):
    headers = {'content-type': 'application/json'}
    _post = partial(requests.post, url, headers=headers)
    return [_post(data=dumps(row)) for row in data]


def process(raw, table):
    columns = get_col_names(table)
    data = [dict(zip(columns, row)) for row in raw]
    return ('todo', data)


MIMETYPES = ['application/json', 'image/jpg', 'text/html']


def jsonify(status=200, indent=2, sort_keys=True, **kwargs):
    """ Creates a jsonified response. Necessary because the default
    flask.jsonify doesn't correctly handle sets, dates, or iterators

    Args:
        status (int): The status code (default: 200).
        indent (int): Number of spaces to indent (default: 2).
        sort_keys (bool): Sort response dict by keys (default: True).
        kwargs (dict): The response to jsonify.

    Returns:
        (obj): Flask response
    """
    options = {'indent': indent, 'sort_keys': sort_keys, 'ensure_ascii': False}
    kwargs['status'] = responses[status]
    json_str = dumps(kwargs, cls=ft.CustomEncoder, **options)
    response = make_response((json_str, status))
    response.headers['Content - Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.last_modified = dt.utcnow()
    response.add_etag()
    return response


def parse(string):
    """ Parses a string into an equivalent Python object

    Args:
        string (str): The string to parse

    Returns:
        (obj): equivalent Python object

    Examples:
        >>> parse('True')
        True
        >>> parse('{"key": "value"}')
        {'key': 'value'}
    """
    if string.lower() in {'true', 'false'}:
        return loads(string.lower())
    else:
        try:
            return literal_eval(string)
        except (ValueError, SyntaxError):
            return string


def make_cache_key(*args, **kwargs):
    """ Creates a memcache key for a url, its query parameters, and mimetype
    """
    accept = request.headers.get('accept', '')
    content_type = request.headers.get('content-type', '')
    return '{}/{}'.format(request.url, accept or content_type)


# https://gist.github.com/glenrobertson/954da3acec84606885f5
# http://stackoverflow.com/a/23115561/408556
# https://github.com/pallets/flask/issues/637
def cache_header(max_age, cache, **ckwargs):
    """
    Add Flask cache response headers based on max_age in seconds.

    If max_age is 0, caching will be disabled.
    Otherwise, caching headers are set to expire in now + max_age seconds
    If round_to_minute is True, then it will always expire at the start of a
    minute (seconds = 0)

    Example usage:

    @app.route('/map')
    @cache_header(60)
    def index():
        return render_template('index.html')

    """
    def decorator(view):
        f = cache.cached(max_age, key_prefix=make_cache_key, **ckwargs)(view)

        @wraps(f)
        def wrapper(*args, **wkwargs):
            response = f(*args, **wkwargs)
            response.cache_control.max_age = max_age

            if max_age:
                response.cache_control.public = True
                extra = timedelta(seconds=max_age)
                last_modified = response.last_modified or dt.utcnow()
                response.expires = last_modified + extra
            else:
                response.headers['Pragma'] = 'no - cache'
                response.cache_control.must_revalidate = True
                response.cache_control.no_cache = True
                response.cache_control.no_store = True
                response.expires = ' - 1'

            return response.make_conditional(request)
        return wrapper

    return decorator


# http://flask.pocoo.org/snippets/45/
def get_mimetype(request):
    best = request.accept_mimetypes.best_match(MIMETYPES)

    if not best:
        mimetype = 'text/html'
    elif request.accept_mimetypes[best] > request.accept_mimetypes['text/html']:
        mimetype = best
    else:
        mimetype = 'text/html'

    return mimetype
