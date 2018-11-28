Create the views for your model
-------------------------------

There is already a views class created in your project by the scaffold,
see file ``views/excavation.py``. Let's have a look on that file content.

To ease creation of views classes, c2cgeoform comes with an abstract
class that contains base methods to display grids, render forms and save
data. This is why ExcavationViews extends AbstractViews for a specific
SQLAlchemy model and colander schema:

.. code-block:: python

   @view_defaults(match_param='table=excavations')
   class ExcavationViews(AbstractViews):

       _model = Excavation
       _base_schema = base_schema

Also note the ``@view_defaults`` which says that all the views declared in this
class will only apply when the route parameter named table will be equal to
`excavation`. The routes given by c2cgeoform have the following form:

* c2cgeoform_index: ``{table}``
* c2cgeoform_grid: ``{table}/grid.json``
* c2cgeoform_item: ``{table}/{{id}}``
* c2cgeoform_item_duplicate: ``{table}/{{id}}/duplicate``

Those routes are registered in pyramid config with module ``routes``, see file
``routes.py`` at the root of the generated project.

.. code-block:: python

   register_models(config, [
       ('excavations', Excavation)

To select records through urls, we also need a unique field, this is given by:

.. code-block:: python

   _id_field = 'hash'

And to show the grid of table records we need some grid columns definitions:

.. code-block:: python

   _list_fields = [
       _list_field('reference_number'),
       _list_field('request_date'),
       ...
   ]

After that comes the views method, for a typical use case, we could have 6
views:

* ``index``: Return HTML page with the grid.
* ``grid``: Return records as JSON for the grid.
* ``edit``: Show edit / create form for the specified record.
* ``duplicate``: Show duplication form for the specified record.
* ``delete``: Delete the specified record.
* ``save``: Save new record or modifications to existing record.

In a typical use case, those views will only call the super class method with
the same name.

Finally we can note the override of method ``_base_query`` that is there to
reduce the number of queries to the database by using SQLAlchemy Subquery Eager
Loading.
