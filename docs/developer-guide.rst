.. _developer-guide:

Set up development environment
------------------------------

This page describes how to set up the development environment for working on
c2cgeoform. It is for developers working on c2cgeoform itself, not for
developers working on c2cgeoform-based applications.

Note that c2cgeoform is a framework and with a
`Pyramid  scaffold <https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/scaffolding.html>`_
to create c2cgeoform-based applications. This scaffold produce a fully
functional c2cgeoform-base project: the c2cgeoform_demo project.

When running code checks and tests, these jobs are first run on the c2cgeoform
framework itself where after the c2cgeoform_demo project is generated in `.build`
folder and finally checks and tests are launched on this project too.

Note that you should never alter the c2cgeoform_demo project itself but the
c2cgeoform scaffold and regenerate the c2cgeoform_demo project.

.. _developer-guide Prerequisites:

Prerequisites
~~~~~~~~~~~~~

You need to install PostgreSQL and PostGIS. On Ubuntu, the packages
``postgresql-server-dev-9.3`` and ``python-dev`` are required.

Clone the project
~~~~~~~~~~~~~~~~~

.. code-block:: shell

   git clone git@github.com:camptocamp/c2cgeoform.git
   cd c2cgeoform

Run the checks
~~~~~~~~~~~~~~

.. code-block:: shell

   make check

Run the tests
~~~~~~~~~~~~~

Create the tests database:

.. code-block:: shell

   sudo -u postgres psql -c "CREATE USER \"www-data\" WITH PASSWORD 'www-data';"

   export DATABASE=c2cgeoform_demo_tests
   sudo -u postgres psql -d postgres -c "CREATE DATABASE $DATABASE OWNER \"www-data\";"
   sudo -u postgres psql -d $DATABASE -c "CREATE EXTENSION postgis;"

Run the framework and demo tests:

.. code-block:: shell

   make test

Serve the c2cgeoform_demo project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create a PostGIS database. For example:

.. code-block:: shell

   export DATABASE=c2cgeoform_demo
   sudo -u postgres psql -d postgres -c "CREATE DATABASE $DATABASE OWNER \"www-data\";"
   sudo -u postgres psql -d $DATABASE -c "CREATE EXTENSION postgis;"
   make initdb

.. code-block:: shell

   make serve

You can now open the demo project in your favorite browser:
http://localhost:6543/

Here is it, you're ready to develop in c2cgeoform. Make changes in c2cgeoform,
run the checks, tests and see the results in c2cgeoform demo application.
