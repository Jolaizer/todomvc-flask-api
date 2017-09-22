# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
    app.tests.test_endpoints
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides unit tests for the API enpoints.
"""
from json import loads, dumps

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from functools import partial

import pytest

from app import create_app, db
from app.models import Todo
from app.utils import process, get_init_data, url_for

JSON = 'application/json'

NOT_ALLOWED = {
    'message': 'The method is not allowed for the requested URL.',
    'status': 405
}


def get_data(response):
    raw = response.get_data(as_text=True)
    mimetype = response.headers.get('mimetype', '')
    content_type = response.headers.get('content-type', '')
    is_json = ('json' in mimetype) or ('json' in content_type)

    try:
        data = loads(raw) if is_json else raw
    except JSONDecodeError:
        if response.status_code == 405:
            data = NOT_ALLOWED
        elif raw:
            raise
        else:
            data = {}

    return data


@pytest.fixture
def client(request):
    app = create_app(config_mode='Test')
    client = app.test_client()
    headers = {'accept': JSON}
    client_post = client.post
    client_patch = client.patch

    def client_url_for(table_name=None, **kwargs):
        with app.test_request_context():
            kwargs['instid'] = kwargs.pop('id', None)
            return url_for(table_name, **kwargs)

    def post(url, data):
        return client_post(url, data=dumps(data), content_type=JSON)

    def patch(url, data):
        return client_patch(url, data=dumps(data), content_type=JSON)

    client.get = partial(client.get, headers=headers)
    client.delete = partial(client.delete, headers=headers)
    client.post = post
    client.patch = patch
    client.url_for = client_url_for

    with app.test_request_context():
        db.create_all()

    raw = get_init_data()
    name, data = process(raw, Todo)
    client.todo_url = partial(client_url_for, name)

    def get_num_todos():
        r = client.get(client.todo_url())
        return get_data(r)['num_results']

    client.get_num_todos = get_num_todos

    for row in data:
        r = post(client.todo_url(), data=row)
        assert r.status_code == 201
        assert client.get_num_todos() > 0

    return client


def test_index(client):
    r = client.get(client.url_for())
    assert r.status_code == 200


def test_delete_todo(client):
    old = client.get_num_todos()
    r = client.delete(client.todo_url(id=1))
    assert r.status_code == 204
    assert client.get_num_todos() == old - 1


def test_cors_headers(client):
    headers = {'Origin': 'www.example.com'}
    r = client.get(client.url_for(), headers=headers)
    assert r.headers['Access-Control-Allow-Origin'] == 'www.example.com'


def test_new_todos_properties(client):
    data = {'title': 'different text'}
    r = client.post(client.todo_url(), data=data)
    assert r.status_code == 201
    json = get_data(r)
    assert set(json).issuperset({'completed', 'id'})
    assert json['completed'] is False


def test_todos_properties(client):
    r = client.get(client.todo_url())
    json = get_data(r)['objects'][0]
    assert set(json).issuperset({'completed', 'id'})


def test_patching_todo_title(client):
    url = client.todo_url(id=1)
    r = client.get(url)
    assert get_data(r)['title'] == 'First task'

    data = {'title': 'different text'}
    r = client.patch(url, data=data)
    assert r.status_code == 200
    assert get_data(r)['title'] == data['title']

    r = client.get(url)
    assert get_data(r)['title'] == data['title']


def test_patching_todo_completedness(client):
    url = client.todo_url(id=1)
    r = client.get(url)
    assert get_data(r)['completed'] is False

    data = {'completed': True}
    r = client.patch(url, data=data)
    assert get_data(r)['completed'] is True

    r = client.get(url)
    assert get_data(r)['completed'] is True


def test_todo_delete(client):
    url = client.todo_url(id=1)
    r = client.delete(url)
    assert r.status_code == 204
    assert get_data(r) == {}

    r = client.get(url)
    assert r.status_code == 404
    assert not get_data(r)


def test_todo_delete_only_deletes_referenced_todo(client):
    r = client.delete(client.todo_url(id=1))
    assert r.status_code == 204

    r = client.get(client.todo_url(id=2))
    assert r.status_code == 200
