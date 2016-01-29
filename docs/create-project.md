## Creating a `c2cgeoform` project

This page describes how to create a `c2cgeoform` project. A `c2cgeoform`
project is basically a Pyramid project with `c2cgeoform` enabled in the
project.

### System requirements

The following system packages must be installed on your system:

* `python-virtualenv`
* `libpq-dev` (header files for PostgreSQL)
* `gettext`

### Install c2cgeoform

```shell
$ git clone git@github.com:camptocamp/c2cgeoform.git
$ git checkout scaffold  # until scaffold branch is merged into master
$ make install
```

### Create a Pyramid project using c2cgeoform scaffold

Creating a `c2cgeoform` is creating a pyramid project using the c2cgeoform scaffold.

```shell
cd c2cgeoform
.build/venv/bin/pcreate -s c2cgeoform ../MyProject
```

### Install the project and its dependencies

```shell
$ cd ../MyProject
$ make install
```

### Set up database

First of all you need to have a PostGIS database for the project. See the
[Prerequesites](developer-guide.md#prerequesites) of the Developer Guide to
know how to do that.

Create the database :

```shell
$ sudo -u postgres createdb myproject -T template_postgis
$ sudo -u postgres psql -c "GRANT ALL ON DATABASE myproject TO "www-data";'
```

When you do have a Postgres role and a PostGIS database edit the
`development.ini` file and set `sqlachemy.url` as appropriate. For example:

```py
sqlalchemy.url = postgresql://myproject:myproject@localhost:5432/myproject
```

Now create the tables:

```shell
$ make initdb
```

Note that this execute the python script `myproject/scripts/initializedb.py`.
You will have to customize this thereafter.

### Run the development server

You're now ready to run the application:

```shell
$ make serve
```

Visit the following ULRs to verify that the application works correctly:
[http://localhost:6543/fouille/form/](http://localhost:6543/fouille/form/) and
[http://localhost:6543/fouille/](http://localhost:6543/fouille/).


### Customise the model

As a `c2cgeoform` application developer your main task is to define a *model*.
See the "Defining a model for a form page" [page](model.md) to know how to do
this.

Edit the file `myproject/models.py`.

### Customise the form template

As a `c2cgeoform` application developer you also need to define a *form
template*.

Edit the file `myproject/templates/form.pt`.

### Update translations

Update the catalogue files :

```shell
$ make update-catalog
```

Now you can edit translation catalogues with `.po` extension
in `myproject/locale` folder.

`c2cgeoform` is installed from source (as opposed to being installed as an
egg). For that reason it is required to manually compile the `c2cgeoform`
catalog:

```shell
$ msgfmt ../venv/src/c2cgeoform/c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.po --output-file=../venv/src/c2cgeoform/c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.mo
$ msgfmt ../venv/src/c2cgeoform/c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.po --output-file=../venv/src/c2cgeoform/c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.mo
```

### Session management configuration

By default `c2cgeoform` uses [pyramid_beaker](https://pypi.python.org/pypi/pyramid_beaker)
to manage its sessions. Please refer to the [documentation](http://beaker.readthedocs.org)
to adapt the configuration to your project setup.
