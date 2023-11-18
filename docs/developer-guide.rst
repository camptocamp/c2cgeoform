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

Install the pre-commit hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   pip install --user pre-commit
   pre-commit install --allow-missing-config

Install poetry
~~~~~~~~~~~~~~

.. code-block:: shell

   sudo apt install pipx
   pipx install poetry

Install or select Node.js 10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   nvm use 10

Build runtime resources
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   make build

Run the tests
~~~~~~~~~~~~~

Run the framework and demo tests:

.. code-block:: shell

   make test

.. _developer-guide Serve_development_version:

Serve the c2cgeoform_demo project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create a PostGIS database. For example:

.. code-block:: shell

   make initdb

Run the development server:

.. code-block:: shell

   make serve

You can now open the demo project in your favorite browser:
http://localhost:6543/

And there you go, you're ready to develop, make changes in c2cgeoform, run
checks and tests in c2cgeoform. And finally see the results in c2cgeoform demo
application.

Build documentation
~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   make docs

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
