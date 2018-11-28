Set up development environment
------------------------------

This page describes how to set up the development environment for
working on ``c2cgeoform``. It is for developers working on
``c2cgeoform`` itself, not for developers working on
``c2cgeoform``-based applications.

Prerequisites
~~~~~~~~~~~~~

You need to install PostgreSQL and PostGIS. On Ubuntu, the packages
``postgresql-server-dev-9.3`` and ``python-dev`` are required.

You need to create a role. For example:

.. code:: shell

   sudo su - postgres
   createuser --pwprompt c2cgeoform

You need to create a PostGIS database. For example:

.. code:: shell

   createdb --owner=c2cgeoform c2cgeoform
   psql -d c2cgeoform -c "CREATE EXTENSION postgis;"

Configuration
~~~~~~~~~~~~~

Edit ``tests.ini`` and modify the SQLAlchemy database connection string
as appropriate.

For example:

.. code:: py

   sqlalchemy.url = postgresql://c2cgeoform:c2cgeoform@localhost:5432/c2cgeoform

Installation
~~~~~~~~~~~~

Install a dev egg of ``c2cgeoform`` in a virtual env:

.. code:: shell

   $ make install

(This creates the virtual env for you.)

Just run ``make`` to know about the possible targets.

Initialize the DB
~~~~~~~~~~~~~~~~~

Initialize the database:

.. code:: shell

   $ make initdb

Run the tests
~~~~~~~~~~~~~

Run the tests:

Create the tests database:

::

   sudo -u postgres psql -c "CREATE USER \"www-data\" WITH PASSWORD 'www-data';"

   export DATABASE=c2cgeoform_demo_tests
   sudo -u postgres psql -d postgres -c "CREATE DATABASE $DATABASE OWNER \"www-data\";"
   sudo -u postgres psql -d $DATABASE -c "CREATE EXTENSION postgis;"

Run the framework and demo tests:

.. code:: shell

   make test
