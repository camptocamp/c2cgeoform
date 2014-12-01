## Defining the model for a form

The underlying schema for a `c2cgeoform` form is defined as SQLAlchemy model. A
simple definition is shown below:

```python
from sqlalchemy import (Column, Integer, Text)
import deform
from c2cgeoform.models import Base


class Comment(Base):
    __tablename__ = 'comments'
    __colanderalchemy_config__ = {
        'title': 'A very simple form'
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget(),
            'admin_list': True
        }})

    hash = Column(Text, unique=True)

    name = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Name',
            'admin_list': True
        }})

    comment = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Comment',
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
```

This SQLAlchemy model is enriched with properties for [ColanderAlchemy](
http://colanderalchemy.readthedocs.org/en/latest/), for example to set a title
for a field, to use a specific Deform [widget](http://deform2demo.repoze.org/)
or to use a Colander [validator](http://colander.readthedocs.org/en/latest/api.html#validators).

In general, every SQLAlchemy model can be used as schema for a form. The only
requirements are:

* The model class must contain exactly one primary key column. Tables with
composite primary keys are not supported.
* The table must have a `hash` column, in which a generated identifier will be
inserted for new form entries. This allows to reference a form submission
without exposing the database id. By default the hash column is assumed to be
named `hash`. But a different name can be provided using the property
`hash_column_name` when registering the schema.

A more complex example for a model can be found [here](../c2cgeoform/pully/model.py).
For more information on how to define the model, please refer to the documentation
of [SQLAlchemy](http://www.sqlalchemy.org/), [ColanderAlchemy](
http://colanderalchemy.readthedocs.org/en/latest/), [Colander](
http://colander.readthedocs.org/en/latest/) and [Deform](http://deform.readthedocs.org/en/latest/).

## The map widget

All Deform [widgets](http://deform2demo.repoze.org/) can be used with
`c2cgeoform`. Additionally, `c2cgeoform` provides a map widget for GeoAlchemy 2
geometry columns, which allows to draw and modify geometries on an OpenLayers 3
map.

Example:

    position = Column(
        geoalchemy2.Geometry('POINT', 4326, management=True), info={
            'colanderalchemy': {
                'title': 'Position',
                'typ':
                colander_ext.Geometry('POINT', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})

To customize the OpenLayers 3 map, the widget template `map.pt` has to be
overwritten.
