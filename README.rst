todomvc-flask-api |travis|
==========================

.. |travis| image:: https://img.shields.io/travis/reubano/todomvc-flask-api/master.svg
    :target: https://travis-ci.org/reubano/todomvc-flask-api

Introduction
------------

`TodoMVC-Flask-API <http://todomvc-flask-api.herokuapp.com>`_ is a `Flask <http://flask.pocoo.org>`_ (`About Flask`_) powered `TodoMVC RESTful API backend <http://todobackend.com>`_ written in Python.

Requirements
------------

TodoMVC-Flask-API has been tested and known to work on the following configurations:

- MacOS X 10.9.5
- Ubuntu 14.04 LTS
- Python 3.6

Framework
---------

Flask Extensions
^^^^^^^^^^^^^^^^

- Database abstraction with `SQLAlchemy <http://www.sqlalchemy.org>`_.
- Script support with `Flask-Script <http://flask-script.readthedocs.org/en/latest/>`_.
- Database validation with `SAValidation <https://pypi.python.org/pypi/SAValidation>`_
- RESTful API generation with `Flask-Restless <http://flask-restless.readthedocs.org/>`_

Production Server
^^^^^^^^^^^^^^^^^

- `PostgreSQL <http://postgresql.org/>`_
- `gunicorn <http://gunicorn.org/>`_
- `gevent <http://www.gevent.org/>`_

Quick Start
-----------

Preparation
^^^^^^^^^^^

Check that the correct version of Python is installed

.. code-block:: bash

    python -V

Activate your `virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenvironments-ref>`_

Installation
^^^^^^^^^^^^

*Clone the repo*

.. code-block:: bash

    git clone git@github.com:reubano/todomvc-flask-api.git

*Install requirements*

.. code-block:: bash

    cd todomvc-flask-api
    pip install -r base-requirements.txt

*Run API server*

.. code-block:: bash

    manage serve

Now *view the API documentation* at ``http://localhost:5000``

Scripts
-------

TodoMVC-Flask-API comes with a built in script manager ``manage.py``. Use it to start the
server, run tests, and initialize the database.

Usage
^^^^^

.. code-block:: bash

    manage <command> [command-options] [manager-options]

Examples
^^^^^^^^

*Start server*

.. code-block:: bash

    manage serve

*Run tests*

.. code-block:: bash

    manage test

*Run linters*

.. code-block:: bash

    manage lint

*Initialize the dev database*

.. code-block:: bash

    manage initdb

*Populate the production database*

.. code-block:: bash

    manage popdb -m Production

Manager options
^^^^^^^^^^^^^^^

      -m MODE, --cfgmode=MODE  set the configuration mode, must be one of
                               ['Production', 'Development', 'Test'] defaults
                               to 'Development'. See `config.py` for details
      -f FILE, --cfgfile=FILE  set the configuration file (absolute path)

Commands
^^^^^^^^

      runserver           Runs the flask development server
      serve               Runs the flask development server
      check               Check staged changes for lint errors
      lint                Check style with linters
      test                Run nose, tox, and script tests
      createdb            Creates database if it doesn't already exist
      cleardb             Removes all content from database
      initdb              Removes all content from database and creates new
                          tables
      popdb               Populates the database with sample data
      add_keys            Add SSH keys to heroku
      deploy              Deploy app to heroku
      shell               Runs a Python shell inside Flask application context.

Command options
^^^^^^^^^^^^^^^

Type ``manage <command> --help`` to view any command's options

.. code-block:: bash

    manage serve --help

Output

    usage: manage serve [-?] [-t] [-T TIMEOUT] [-l] [-o] [-p PORT] [-h HOST]

    Runs the flask development server

    optional arguments:
      -?, --help            show this help message and exit
      -t, --threaded        Run multiple threads
      -p PORT, --port PORT  The server port
      -h HOST, --host HOST  The server host

Example
^^^^^^^

*Start production server on port 1000*

.. code-block:: bash

    manage serve -p 1000 -m Production

Configuration
-------------

Config Variables
^^^^^^^^^^^^^^^^

The following configurations settings are available in ``config.py``:

======================== ================================================================ =========================================
variable                 description                                                      default value
======================== ================================================================ =========================================
__YOUR_EMAIL__           your email address                                               <user>@gmail.com
API_METHODS              allowed HTTP verbs                                               ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
API_ALLOW_FUNCTIONS      allow sqlalchemy function evaluation                             TRUE
API_ALLOW_PATCH_MANY     allow patch requests to effect all instances of a given resource TRUE
API_MAX_RESULTS_PER_PAGE the maximum number of results returned per page                  1000
======================== ================================================================ =========================================

See the `Flask-Restless docs <http://flask-restless.readthedocs.org/en/latest/customizing.html>`_ for a complete list of settings.

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

TodoMVC-Flask-API will reference the ``SECRET_KEY`` environment variable in ``config.py`` if it is set on your system.

To set this environment variable, *do the following*:

.. code-block:: bash

    echo 'export SECRET_KEY=value' >> ~/.profile

Documentation
-------------

For a list of available resources, example requests and responses, and code samples,
view the `online documentation <https://todomvc-flask-api.herokuapp.com/>`_. View the `Flask-Restless guide <http://flask-restless.readthedocs.org>`_ for more `request/response examples <http://flask-restless.readthedocs.org/en/latest/requestformat.html>`_ and directions on `making search queries. <http://flask-restless.readthedocs.org/en/latest/searchformat.html>`_

Production Server
^^^^^^^^^^^^^^^^^

Preparation
~~~~~~~~~~~

Getting ``gevent`` up and running is a bit tricky so follow these instructions carefully.

To use ``gevent``, you first need to install ``libevent``.

*Linux*

.. code-block:: bash

    apt-get install libevent-dev

*Mac OS X via* `homebrew <http://mxcl.github.com/homebrew/>`_

.. code-block:: bash

    brew install libevent

*Mac OS X via* `macports <http://www.macports.com/>`_

.. code-block:: bash

    sudo port install libevent

*Mac OS X via DMG*

`download on Rudix <http://rudix.org/packages-jkl.html#libevent>`_


Installation
~~~~~~~~~~~~

Now that libevent is handy, *install the remaining requirements*

.. code-block:: bash

    sudo pip install -r requirements.txt

Or via the following if you installed libevent from macports

.. code-block:: bash

    sudo CFLAGS="-I /opt/local/include -L /opt/local/lib" pip install gevent
    sudo pip install -r requirements.txt

Foreman
~~~~~~~

Finally, *install foreman*

.. code-block:: bash

    sudo gem install foreman

Now, you can *run the application* locally

.. code-block:: bash

    foreman start

You can also *specify what port you'd prefer to use*

.. code-block:: bash

    foreman start -p 5555

Deployment
^^^^^^^^^^

If you haven't `signed up for Heroku <https://api.heroku.com/signup>`_, go
ahead and do that. You should then be able to `add your SSH key to
Heroku <http://devcenter.heroku.com/articles/quickstart>`_, and also
`heroku login` from the commandline.

*Install heroku and create your app*

.. code-block:: bash

    sudo gem install heroku
    heroku create -s cedar app_name

*Add the database*

.. code-block:: bash

    heroku addons:add heroku-postgresql:dev
    heroku pg:promote HEROKU_POSTGRESQL_COLOR

*Push to Heroku and initialize the database*

.. code-block:: bash

    git push heroku master
    heroku run python manage.py createdb -m Production

*Start the web instance and make sure the application is up and running*

.. code-block:: bash

    heroku ps:scale web=1
    heroku ps

Now, we can *view the application in our web browser*

.. code-block:: bash

    heroku open

And anytime you want to redeploy, it's as simple as ``git push heroku master``.
Once you are done coding, deactivate your virtualenv with ``deactivate``.

Directory Structure
-------------------

.. code-block:: bash

    tree . | sed 's/+----/├──/' | sed '/.pyc/d' | sed '/.DS_Store/d'
    .
    ├── LICENSE
    ├── MANIFEST.in
    ├── Procfile
    ├── README.rst
    ├── app
    │   ├── __init__.py
    │   ├── models.py
    │   ├── order.py
    │   └── utils.py
    ├── app.db
    ├── base-requirements.txt
    ├── config.py
    ├── dev-requirements.txt
    ├── helpers
    │   ├── check-stage
    │   ├── clean
    │   ├── pippy
    │   ├── srcdist
    │   └── wheel
    ├── manage.py
    ├── requirements.txt
    ├── runtime.txt
    ├── setup.cfg
    ├── setup.py
    ├── tests
    │   ├── standard.rc
    │   ├── test.sh
    │   ├── test_endpoints.py
    │   └── test_models.py
    └── tox.ini

Contributing
------------

*First time*

1. Fork
2. Clone
3. Code (if you are having problems committing because of git pre-commit
   hook errors, just run ``manage check`` to see what the issues are.)
4. Use tabs **not** spaces
5. Add upstream ``git remote add upstream https://github.com/reubano/todomvc-flask-api.git``
6. Rebase ``git rebase upstream/master``
7. Test ``manage test``
8. Push ``git push origin master``
9. Submit a pull request

*Continuing*

1. Code (if you are having problems committing because of git pre-commit
   hook errors, just run ``manage check`` to see what the issues are.)
2. Use tabs **not** spaces
3. Update upstream ``git fetch upstream``
4. Rebase ``git rebase upstream/master``
5. Test ``manage test``
6. Push ``git push origin master``
7. Submit a pull request

Contributors
------------

.. code-block:: bash

    $ git shortlog -sn
        89  Faerbit
        48  requires.io
        17  Fabian
         6  Reuben Cummings

About Flask
-----------

`Flask <http://flask.pocoo.org>`_ is a BSD-licensed microframework for Python based on
`Werkzeug <http://werkzeug.pocoo.org/>`_, `Jinja2 <http://jinja.pocoo.org>`_ and good intentions.

License
-------

TodoMVC-Flask API is distributed under the `MIT License <http://opensource.org/licenses/mit-license.php>`_.
