# c2cgeoform README

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
