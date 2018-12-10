Configure the grid
------------------

Grid columns can be configured using the ``_list_fields`` property of the views
class, which is an ordered list of ``ListField`` objects, one for each column.

The ``ListField`` constructor take some parameters:

* ``model``: the SQLAlchemy mapper (required if attr is an attribute name).
* ``attr``: the model attribute name to use or an SQLAlchemy InstrumentedAttribute.
* ``key``: an identifier for the column, default to ``attribute.key``.
* ``label``: text for the column header, default to colanderalchemy title for the field.
* ``renderer``: callable that take an entity of the SQLAlchemy mapper and
  return a string value.
* ``sort_column``: An ``IntrumentedAttribute`` to use in ``sort_by``.
* ``filter_column``: An ``IntrumentedAttribute`` to filter with.
* ``visible``: Is the column visible by default.

Each time the table index page will ask for data to your grid view, the
``AbstractView`` will create a default query using ``AbstractViews._base_query`` method.


If you use columns coming from relationships, this might result in sending one
request to the database for each relationship and each record.
In such cases, to avoid such performance issue you should override the
``_base_query`` method to use eager loading for those relationships, for example:

.. code-block:: python

   def _base_query(self):
       return self._request.dbsession.query(Excavation).distinct(). \
           join('situations'). \
           options(subqueryload('situations'))

Note that you also need to ``join`` the relationships you use for sorting and filtering.
