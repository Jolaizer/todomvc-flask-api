# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
    app.tests.test_models
    ~~~~~~~~~~~~~~~~~~~~~

    Provides unit tests for the app models.
"""
import pytest

from app import create_app, db
from app.models import Todo


@pytest.fixture
def client(request):
    app = create_app(config_mode='Test')
    client = app.test_client()

    def add(**kwargs):
        with app.test_request_context():
            todo = Todo(**kwargs)
            db.session.add(todo)
            db.session.commit()

    def query():
        with app.test_request_context():
            return db.session.query(Todo).first()

    with app.test_request_context():
        db.create_all()

    client.add = add
    client.query = query
    return client


def test_string_representation(client):
    text = 'some text'
    todo = Todo(title=text)
    assert str(todo) == '<Todo: "{}" (not completed)>'.format(text)


def test_entries_get_created_unfinished(client):
    title = 'some text'
    client.add(title=title)
    todo = client.query()
    assert todo.title == title
    assert not todo.completed
