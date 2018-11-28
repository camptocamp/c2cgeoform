## Creating a `c2cgeoform` project

This page describes how to create a `c2cgeoform` project. A `c2cgeoform`
project is basically a Pyramid project with `c2cgeoform` enabled in the
project.

### System requirements

The following system packages must be installed on your system:

* `python-virtualenv`
* `libpq-dev` (header files for PostgreSQL)
* `gettext`

On Windows, you should install `make` using Cygwin (and put the bin folder
into the path). For Python, please use Python >= 3.x.


### Install c2cgeoform

```shell
git clone git@github.com:camptocamp/c2cgeoform.git
cd c2cgeoform
make build
```

On Windows, you should use the https way to clone the repository:

```shell
git clone https://github.com:camptocamp/c2cgeoform.git
```

### Create a Pyramid project using c2cgeoform scaffold

Creating a `c2cgeoform` is creating a pyramid project using the c2cgeoform scaffold.

Note that if PYTHONPATH does not exists as an environment variable,
template files (*_tmpl) do not render in new project folder.

```shell
export PYTHONPATH=$PYTHONPATH
.build/venv/bin/pcreate -s c2cgeoform ../c2cgeoform_project
```

### Initialize a git repository

Make your new project folder a git repository.

```shell
cd ../c2cgeoform_project
git init
git add .
git commit -m 'Initial commit'
```

### Install the project and its dependencies

```shell
make build
```

### Set up database

First of all you need to have a PostGIS database for the project. See the
[Prerequesites](developer-guide.md#prerequesites) of the Developer Guide to
know how to do that.

Create the database:

```shell
sudo -u postgres createdb c2cgeoform_project
sudo -u postgres psql -d c2cgeoform_project -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -c 'GRANT ALL ON DATABASE c2cgeoform_project TO "www-data";'
```

When you do have a Postgres role and a PostGIS database edit the
`development.ini` and `production.ini` files and set `sqlachemy.url` as appropriate.
For example:

```py
sqlalchemy.url = postgresql://www-data:www-data@localhost:5432/c2cgeoform_project
```

Now create the tables:

```shell
make initdb
```

Note that this execute the python script `c2cgeoform_project/scripts/initializedb.py`.
You will have to customize this thereafter.

### Run the development server

You're now ready to run the application:

```shell
make serve
```

Visit the following ULRs to verify that the application works correctly:
[http://localhost:6543/excavations/new](http://localhost:6543/excavations/new) and
[http://localhost:6543/excavations](http://localhost:6543/excavations).

### Customise the model

As a `c2cgeoform` application developer your main task is to define a *model*.
See the "Defining a model for a form page" [page](model.md) to know how to do
this.

Edit the file `c2cgeoform_project/models.py`.

### Customise the form template

As a `c2cgeoform` application developer you also need to define a *form
template*.

Edit the file `c2cgeoform_project/templates/form.pt`.

### Update translations

Update the catalogue files :

```shell
make update-catalog
```

Now you can edit translation catalogues with `.po` extension
in `c2cgeoform_project/locale` folder.

`c2cgeoform` is installed from source (as opposed to being installed as an
egg). For that reason it is required to manually compile the `c2cgeoform`
catalog:

```shell
msgfmt ../venv/src/c2cgeoform/c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.po  --output-file=../venv/src/c2cgeoform/c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.mo
msgfmt ../venv/src/c2cgeoform/c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.po  --output-file=../venv/src/c2cgeoform/c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.mo
```

### Session management configuration

By default `c2cgeoform` uses [pyramid_beaker](https://pypi.python.org/pypi/pyramid_beaker)
to manage its sessions. Please refer to the [documentation](http://beaker.readthedocs.org)
to adapt the configuration to your project setup.
