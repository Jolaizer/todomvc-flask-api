# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
    app
    ~~~

    Provides the flask application
"""
from datetime import datetime as dt

from savalidation import ValidationMixin
from savalidation.validators import validates_constraints
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app import db


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    if 'sqlite3' in str(dbapi_connection.cursor):
        """Enable foreign key constraints for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    utc_updated = db.Column(
        db.DateTime, nullable=False, default=dt.utcnow, onupdate=dt.utcnow)

    completed = db.Column(db.Boolean, default=False, nullable=False)
    title = db.Column(db.String(), nullable=False, index=True)
    validates_constraints()

    def __repr__(self):
        completed = 'completed' if self.completed else 'not completed'
        return ('<Todo: "{}" ({})>'.format(self.title, completed))
