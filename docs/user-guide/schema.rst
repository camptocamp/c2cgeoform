Understand the schemas
----------------------

`ColanderAlchemy`_ allows creating `Colander`_ schemas directly from
`SQLAlchemy`_ model classes.

Additionally, c2cgeoform provides his own classes with extended features.
In basic use case schema creation will look like:

.. code-block:: python

   from model import MyClass
   schema = GeoFormSchemaNode(MyClass)

See following API to understand what is going on behind the scene.

.. automodule:: c2cgeoform.schema
   :members: GeoFormSchemaNode, GeoFormManyToManySchemaNode
   :member-order: bysource

.. _Colander: http://colander.readthedocs.org/en/latest/
.. _ColanderAlchemy: http://colanderalchemy.readthedocs.org/en/latest/
.. _SQLAlchemy: http://www.sqlalchemy.org/