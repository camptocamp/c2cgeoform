Creating a ``c2cgeoform`` project
---------------------------------

This page describes how to create a ``c2cgeoform`` project. A
``c2cgeoform`` project is basically a Pyramid project with
``c2cgeoform`` enabled in the project.

System requirements
~~~~~~~~~~~~~~~~~~~

The following system packages must be installed on your system:

-  ``python-virtualenv``
-  ``libpq-dev`` (header files for PostgreSQL)
-  ``gettext``

On Windows, you should install ``make`` using Cygwin (and put the bin
folder into the path). For Python, please use Python >= 3.x.

Install c2cgeoform
~~~~~~~~~~~~~~~~~~

.. code:: shell

   git clone git@github.com:camptocamp/c2cgeoform.git
   cd c2cgeoform
   make build

On Windows, you should use the https way to clone the repository:

.. code:: shell

   git clone https://github.com:camptocamp/c2cgeoform.git

Create a Pyramid project using c2cgeoform scaffold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating a ``c2cgeoform`` is creating a pyramid project using the
c2cgeoform scaffold.

Note that if PYTHONPATH does not exists as an environment variable,
template files (*_tmpl) do not render in new project folder.

.. code:: shell

   export PYTHONPATH=$PYTHONPATH
   .build/venv/bin/pcreate -s c2cgeoform ../c2cgeoform_project

Initialize a git repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make your new project folder a git repository.

.. code:: shell

   cd ../c2cgeoform_project
   git init
   git add .
   git commit -m 'Initial commit'

Install the project and its dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   make build

Set up database
~~~~~~~~~~~~~~~

First of all you need to have a PostGIS database for the project. See
the `Prerequesites`_ of the Developer Guide to know how to do that.

Create the database:

.. code:: shell

   sudo -u postgres createdb c2cgeoform_project
   sudo -u postgres psql -d c2cgeoform_project -c 'CREATE EXTENSION postgis;'
   sudo -u postgres psql -c 'GRANT ALL ON DATABASE c2cgeoform_project TO "www-data";'

When you do have a Postgres role and a PostGIS database edit the
``development.ini`` and ``production.ini`` files and set
``sqlachemy.url`` as appropriate. For example:

.. code:: py

   sqlalchemy.url = postgresql://www-data:www-data@localhost:5432/c2cgeoform_project

Now create the tables:

.. code:: shell

   make initdb

Note that this execute the python script
``c2cgeoform_project/scripts/initializedb.py``. You will have to
customize this thereafter.

Run the development server
~~~~~~~~~~~~~~~~~~~~~~~~~~

You’re now ready to run the application:

.. code:: shell

   make serve

Visit the following ULRs to verify that the application works correctly:
http://localhost:6543/excavations/new and
http://localhost:6543/excavations.

Customise the model
~~~~~~~~~~~~~~~~~~~

As a ``c2cgeoform`` application developer your main task is to define a
*model*. See the “Defining a model for a form page” `page`_ to know how
to do this.

Edit the file ``c2cgeoform_project/models.py``.

Customise the form template
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a ``c2cgeoform`` application developer you also need to define a
*form template*.

Edit the file ``c2cgeoform_project/templates/form.pt``.

Update translations
~~~~~~~~~~~~~~~~~~~

Update the

.. _Prerequesites: developer-guide.md#prerequesites
.. _page: model.md