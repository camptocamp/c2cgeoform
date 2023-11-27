# c2cgeoform

c2cgeoform is a framework easing the creation of web pages with forms. Users
of c2cgeoform declaratively create _models_, from which the framework
can create forms, views, lists, ...

c2cgeoform supports various data types, including _geometry_ types (points,
lines, polygons). For geometry types `c2geoform` generates maps with editing
tools to create, modify or delete geometries.

c2cgeoform is based on [Pylons technologies](http://www.pylonsproject.org/).
More specifically, it uses
[Pyramid](http://docs.pylonsproject.org/en/latest/docs/pyramid.html),
[Colander](http://colander.readthedocs.org/en/latest/), and
[Deform](http://deform.readthedocs.org/en/latest/). For interacting with the
database it uses [SQLAlchemy](http://www.sqlalchemy.org/) and
[GeoAlchemy 2](https://geoalchemy-2.readthedocs.org/en/latest/).

Documentation: https://c2cgeoform.readthedocs.io/en/latest/

Demo: https://geomapfish-demo.camptocamp.com/c2cgeoform

## Copyright

c2cgeoform makes use of the icons by [GLYPHICONS](http://glyphicons.com).
Make sure to comply with the [usage terms](http://glyphicons.com/license/) when
utilizing c2cgeoform.

## Contributing

Install the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install --allow-missing-config
```
