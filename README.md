# c2cgeoform

`c2cgeoform` is a framework easing the creation of web pages with forms. Users
of `c2cgeoform` declaratively create *models*
([example](c2cgeoform/pully/model.py)), from which the framework
can create forms, views, lists, …

`c2cgeoform` supports various data types, including *geometry* types (points,
lines, polygons). For geometry types `c2geoform` generates maps with editing
tools to create, modify or delete geometries.

`c2cgeoform` is based on [Pylons technologies](http://www.pylonsproject.org/).
More specifically, it uses
[Pyramid](http://docs.pylonsproject.org/en/latest/docs/pyramid.html),
[Colander](http://colander.readthedocs.org/en/latest/), and
[Deform](http://deform.readthedocs.org/en/latest/). For interacting with the
database it uses [SQLAlchemy](http://www.sqlalchemy.org/) and
[GeoAlchemy 2](https://geoalchemy-2.readthedocs.org/en/latest/).

Demo links: [fill in
a form](http://mapfish-geoportal.demo-camptocamp.com/c2cgeoform/wsgi/fouille/form/),
[list form
submissions](http://mapfish-geoportal.demo-camptocamp.com/c2cgeoform/wsgi/fouille/).

## Set up development environment

### Prequesites

You need to install PostgreSQL and PostGIS, and create a PostGIS database for
`c2cgeoform`. On Ubuntu, the packages `postgresql-server-dev-9.3` and
`python-dev` are required.

One option for PostGIS is to use Oslandia's [PostGIS Docker
image](http://www.oslandia.com/full-spatial-database-power-in-2-lines-en.html).
For that follow the steps below.

### Use Docker for PostGIS

First, install `docker` (`docker.io` for Debian) and add your Unix user
to the `docker` group:

```shell
$ usermod -a -G docker <username>
```

Now run the Docker image:

```shell
$ make rundb
```

This will download the Docker image if it has not been downloaded yet.

Now use `docker.io ps` to know what local port to use to access to
the container's PostgreSQL database.

### Configuration

Edit `development.ini` and modify the SQLAlchemy database connection string as
appropriate.

### Installation

Install a dev egg of `c2cgeoform` in a virtual env:

```shell
$ make install
```

(This creates the virtual env for you.)

### Initialize the DB

Initialize the database:

```shell
$ make initdb
```

### Start the dev server

Start the dev server:

```shell
$ make serve
```

### Session management configuration

By default c2cgeoform uses [pyramid_beaker](https://pypi.python.org/pypi/pyramid_beaker)
to manage its sessions. Please refer to the [documentation](http://beaker.readthedocs.org)
to adapt the configuration to your project setup.

Copyright
----------
c2cgeoform makes use of the icons by [GLYPHICONS](http://glyphicons.com).
Make sure to comply with the [usage terms](http://glyphicons.com/license/) when
utilizing c2cgeoform.
