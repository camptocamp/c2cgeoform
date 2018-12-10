Creating a c2cgeoform project
-----------------------------

This page describes how to create a c2cgeoform project. A
c2cgeoform project is basically a Pyramid project with
c2cgeoform enabled in the project.

Install c2cgeoform
~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   git clone git@github.com:camptocamp/c2cgeoform.git
   cd c2cgeoform
   make build

On Windows, you should use the https way to clone the repository:

.. code-block:: shell

   git clone https://github.com:camptocamp/c2cgeoform.git

Create a Pyramid project using c2cgeoform scaffold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating a ``c2cgeoform`` is creating a pyramid project using the
c2cgeoform scaffold.

Note that if PYTHONPATH does not exists as an environment variable,
template files (\*_tmpl) do not render in new project folder.

.. code-block:: shell

   export PYTHONPATH=$PYTHONPATH
   .build/venv/bin/pcreate -s c2cgeoform ../c2cgeoform_project

Initialize a git repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make your new project folder a git repository.

.. code-block:: shell

   cd ../c2cgeoform_project
   git init
   git add .
   git commit -m 'Initial commit'

Install the project and its dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   make build

Set up database
~~~~~~~~~~~~~~~

First of all you need to have a PostGIS database for the project.
Create the database:

.. code-block:: shell

   sudo -u postgres createdb c2cgeoform_project
   sudo -u postgres psql -d c2cgeoform_project -c 'CREATE EXTENSION postgis;'
   sudo -u postgres psql -c 'GRANT ALL ON DATABASE c2cgeoform_project TO "www-data";'

When you do have a Postgres role and a PostGIS database edit the
``development.ini`` and ``production.ini`` files and set
``sqlachemy.url`` as appropriate. For example:

.. code-block:: ini

   sqlalchemy.url = postgresql://www-data:www-data@localhost:5432/c2cgeoform_project

Now create the tables:

.. code-block:: shell

   make initdb

Note that this execute the python script
``c2cgeoform_project/scripts/initializedb.py``. You will have to
customize this thereafter.

Run the development server
~~~~~~~~~~~~~~~~~~~~~~~~~~

You’re now ready to run the application:

.. code-block:: shell

   make serve

Visit the following ULRs to verify that the application works correctly:
http://localhost:6543/excavations/new and
http://localhost:6543/excavations.
