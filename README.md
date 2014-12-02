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

## Documentation

This section provides links to various parts of the documentation.

* [Create a c2cgeoform project](docs/create-project.md)
* [Defining the model for a form](docs/model.md)
* [Using custom templates](docs/templates.md)
* [Guide for c2cgeoform developers](docs/developer-guide.md)

## Copyright

c2cgeoform makes use of the icons by [GLYPHICONS](http://glyphicons.com).
Make sure to comply with the [usage terms](http://glyphicons.com/license/) when
utilizing c2cgeoform.
