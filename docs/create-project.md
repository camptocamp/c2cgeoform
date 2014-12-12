## Creating a `c2cgeoform` project

This page describes how to create a `c2cgeoform` project. A `c2cgeoform`
project is basically a Pyramid project with `c2cgeoform` enabled in the
project.

### System requirements

The following system packages must be installed on your system:

* `python-virtualenv`
* `libpq-dev` (header files for PostgreSQL)
* `gettext`

### Create a Pyramid project

Creating a `c2cgeoform` project requires creating a Pyramid project. So
creating a Pyramid project is the first step.

Let's install Pyramid in a virtual environment first:

```shell
$ virtualenv venv
$ ./venv/bin/pip install "pyramid==1.5.2"
```

Now create the Pyramid project using Pyramid's `alchemy` scaffold. For
example, to create a project named `MyProject`:

```shell
$ ./venv/bin/pcreate -s alchemy MyProject
```

Remove files you won't need:

```shell
$ rm MyProject/myproject/models.py MyProject/myproject/tests.py MyProject/myproject/views.py MyProject/myproject/templates/mytemplate.pt
```

### Make `c2cgeoform` a dependency of the project

`c2cgeoform` will be a dependency of the project. To indicate this edit
`setup.py` and add `c2cgeoform` to the `requires` list:

```py
requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'c2cgeoform',
    ]
```

The `c2cgeoform` is not on the official Python Package Index so it will
installed directly from GitHub using `pip`. For this create
a `requirements.txt` file at the root of the project (in the `MyProject`
directory) with the following content:

```
-e git+https://github.com/camptocamp/c2cgeoform#egg=c2cgeoform
-e .
```

### Install `c2cgeoform` and the project

Install `c2cgeoform` and the project in the virtual environment using `pip`:

```shell
cd MyProject
../venv/bin/pip install -r requirements.txt
```

### Create model

As a `c2cgeoform` application developer your main task is to define a *model*.
See the "Defining a model for a form page" [page](model.md) to know how to do
this.

Here, as an example, and to be able to complete the project creation, we're
going to use the demo model included in the `c2cgeoform` package.

To copy the `c2cgeoform` demo model into the project:

```shell
cp ../venv/src/c2cgeoform/c2cgeoform/pully/model.py myproject
```

Now edit the `myproject/model.py` file and change the line

```py
_ = TranslationStringFactory('pully')
```

to

```py
_ = TranslationStringFactory('myproject')
```

And change the line

```py
file = open('c2cgeoform/pully/data/osm-lausanne-bus-stops.geojson')
```

to

```py
file = open('myproject/data/osm-lausanne-bus-stops.geojson')
```

This model example uses widgets, namely the `RelationMapWidget` and the
`RelationSearchWidget`, that rely on specific web services. So the
corresponding Pyramid views should also be copied from the demo project:

```shell
mkdir -p myproject/views
cp ../venv/src/c2cgeoform/c2cgeoform/pully/views/*.py myproject/views/
mkdir -p myproject/data
cp ../venv/src/c2cgeoform/c2cgeoform/pully/data/*.geojson myproject/data/
```

### Create form template

As a `c2cgeoform` application developer you also need to define a *form
template*. But here again we're going to use the demo form template that
is included in the `c2cgeoform` package.

Copy the `c2cgeform` demo form template into the project:

```shell
cp ../venv/src/c2cgeoform/c2cgeoform/pully/templates/form.pt myproject/templates
```

Now edit the `myproject/templates/form.pt` file and replace every occurence of
`pully` to `myproject`.

```py
_ TranslationStringFactory('pully');"
```

should be changed to:

```py
_ TranslationStringFactory('myproject');"
```

And every occurence of

```
i18n:domain="pully"
```

should be changed to:

```
i18n:domain="myproject"
```

### Set up internationalization

At the root of the project create a `lingua.cfg` file with the following
content:

```
[extensions]
.html = xml
.pt = xml
.py = python
```

Extract messages:

```shell
$ mkdir -p myproject/locale
$ ../venv/bin/pot-create -c lingua.cfg -o myproject/locale/myproject.pot myproject
```

Initialize the message catalog:

```shell
$ cd myproject/locale
$ mkdir -p fr/LC_MESSAGES
$ msginit -l fr -o fr/LC_MESSAGES/myproject.po
```

Update the catalog files with:

```shell
$ msgmerge --update fr/LC_MESSAGES/myproject.po myproject.pot
```

Compile catalog (from the root of the project):

```shell
$ cd ../..
$ msgfmt myproject/locale/fr/LC_MESSAGES/myproject.po --output-file=myproject/locale/fr/LC_MESSAGES/myproject.mo
```

`c2cgeoform` is installed from source (as opposed to being installed as an
egg). For that reason it is required to manually compile the `c2cgeoform`
catalog:

```shell
$ msgfmt ../venv/src/c2cgeoform/c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.po --output-file=../venv/src/c2cgeoform/c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.mo
$ msgfmt ../venv/src/c2cgeoform/c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.po --output-file=../venv/src/c2cgeoform/c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.mo
```

### Enable `c2cgeoform` in the project

To enable `c2cgeoform` in the project the project's `main` function should be
edited.

Edit `myproject/__init__.py` and replace its content with the following:

```py
from pkg_resources import resource_filename
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from c2cgeoform.schema import register_schema
from c2cgeoform.models import Base, DBSession
from . import model


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')

    # enable c2cgeoform in the project
    config.include('c2cgeoform')

    # add "locale" as a translation dir for the application
    config.add_translation_dirs('locale')

    # register the "fouille" schema on the ExcavationPermission model
    register_schema(
        'fouille',
        model.ExcavationPermission,
        templates_user=resource_filename('myproject', 'templates'),
        excludes_user=['reference_number', 'validated'],
        overrides_user={
            # override the title for a field in the user form
            'request_date': {'title': 'Date'},
            # do not show the 'verified' field of ContactPerson for the user
            'contact_persons': {'excludes': ['verified']}
        })

    # insert test data into the database. To be removed in the final
    # application.
    model.setup_test_data()

    # register the "comment" schema on the Comment model
    register_schema('comment', model.Comment, show_confirmation=False)

    config.add_route('bus_stops', '/bus_stops')
    config.add_view('myproject.views.bus_stops.bus_stops',
                    route_name='bus_stops', renderer='json',
                    request_method='GET')

    config.add_route('addresses', '/addresses')
    config.add_view('myproject.views.addresses.addresses',
                    route_name='addresses', renderer='json',
                    request_method='GET')

    config.scan('myproject')

    # add the c2cgeoform views
    config.add_c2cgeoform_views()

    return config.make_wsgi_app()
```

### Set up database

First of all you need to have a PostGIS database for the project. See the
[Prerequesites](developer-guide.md#prerequesites) of the Developer Guide to
know how to do that.

When you do have a Postgres role and a PostGIS database edit the
`development.ini` file and set `sqlachemy.url` as appropriate. For example:

```py
sqlalchemy.url = postgresql://c2cgeoform:c2cgeoform@localhost:5432/c2cgeoform
```

Now edit `myproject/scripts/initializedb.py` and replace its content by the following:

```py
import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from c2cgeoform.models import Base, DBSession

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
```

Now you're ready to initialize the database (that is create the database
schema):

```shell
$ ../venv/bin/initialize_MyProject_db development.ini
```

### Run the development server

You're now ready to run the application:

```shell
$ ../venv/bin/pserve development.ini
```

Visit the following ULRs to verify that the application works correctly:
[http://localhost:6543/fouille/form/](http://localhost:6543/fouille/form/) and
[http://localhost:6543/fouille/](http://localhost:6543/fouille/).

### Session management configuration

By default `c2cgeoform` uses [pyramid_beaker](https://pypi.python.org/pypi/pyramid_beaker)
to manage its sessions. Please refer to the [documentation](http://beaker.readthedocs.org)
to adapt the configuration to your project setup.
