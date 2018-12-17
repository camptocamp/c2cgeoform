Understanding the schemas
-------------------------

`ColanderAlchemy`_ allows creating `Colander`_ schemas directly from
`SQLAlchemy`_ model classes.

Additionally, c2cgeoform provides its own classes with extended features.
A basic use case schema creation will look like:

.. code-block:: python

   from model import MyClass
   schema = GeoFormSchemaNode(MyClass)

See the following API to understand what is going on behind the scene.

.. automodule:: c2cgeoform.schema
   :members: GeoFormSchemaNode, GeoFormManyToManySchemaNode
   :member-order: bysource

.. _Colander: http://colander.readthedocs.org/en/latest/
.. _ColanderAlchemy: http://colanderalchemy.readthedocs.org/en/latest/
.. _SQLAlchemy: http://www.sqlalchemy.org/