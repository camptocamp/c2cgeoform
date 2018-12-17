.. _developer-guide:

Developer guide
---------------

This page describes how to set up the development environment for working on
c2cgeoform. It is for developers working on c2cgeoform itself, not for
developers working on c2cgeoform-based applications.

Note that c2cgeoform is a framework with a
`Pyramid  scaffold <https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/scaffolding.html>`_
used to create c2cgeoform-based applications. This scaffold produce a fully
functional c2cgeoform-base project: the c2cgeoform_demo project.

When running code checks and tests, these jobs are first run on the c2cgeoform
framework itself. Then the c2cgeoform_demo project is generated in `.build`
folder. Finally, the checks and tests are launched in this project.

Note that you should never alter the c2cgeoform_demo project itself but the
c2cgeoform scaffold and regenerate the c2cgeoform_demo project.

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

.. _developer-guide Serve_development_version:

Serve the c2cgeoform_demo project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create a PostGIS database. For example:

.. code-block:: shell

   export DATABASE=c2cgeoform_demo
   sudo -u postgres psql -d postgres -c "CREATE DATABASE $DATABASE OWNER \"www-data\";"
   sudo -u postgres psql -d $DATABASE -c "CREATE EXTENSION postgis;"
   make initdb

Run the development server:

.. code-block:: shell

   make serve

You can now open the demo project in your favorite browser:
http://localhost:6543/

And there you go, you're ready to develop, make changes in c2cgeoform, run
checks and tests in c2cgeoform. And finally see the results in c2cgeoform demo
application.

Deploy the c2cgeoform_demo on demo server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prepare the demo project:

.. code-block:: shell

   # open a ssh connection with the GMF 2.3 server
   ssh -A geomapfish-demo.camptocamp.com

   # clone the c2cgeoform repository
   cd /var/www/vhosts/geomapfish-demo/private
   git clone git@github.com:camptocamp/c2cgeoform.git

   # generate the c2cgeoform_demo project with mod_wsgi related files
   APACHE_ENTRY_POINT=c2cgeoform make modwsgi

Create the database as to serve the development version, see:
:ref:`developer-guide Serve_development_version`

Include the demo project in Apache virtual host configuration:

.. code-block:: shell

   echo "IncludeOptional $PWD/.build/c2cgeoform_demo/.build/apache.conf" > /var/www/vhosts/geomapfish-demo/conf/c2cgeoform_demo.conf
   sudo apache2ctl configtest

If everything goes fine, restart apache:

.. code-block:: shell

   sudo apache2ctl graceful

You can now open the demo project in your favorite browser:
https://geomapfish-demo.camptocamp.com/c2cgeoform/
