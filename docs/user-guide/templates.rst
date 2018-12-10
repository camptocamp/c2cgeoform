.. _templates:

Using custom templates
----------------------

c2cgeoform distinguishes between two types of templates: **views** templates
and **widget** templates.
- Views templates are used directly by Pyramid and provide the site structure.
- Widgets templates are used by Deform to render the forms.

Default views templates
~~~~~~~~~~~~~~~~~~~~~~~

The default c2cgeoform views templates are located in the ``templates``
folder and use `jinja2`_ syntax.

c2cgeoform comes with partial templates that are included in views templates
of your project.

.. _Jinja2: http://jinja.pocoo.org/

Overriding widgets templates globally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deform widget templates are located in the ``templates/widgets`` folder and
use the `chameleon`_ syntax.

At rendering time, Deform will search for the templates as configured in Form
class renderer ``search_path``. c2cgeoform configure it to:

.. code-block:: python

   default_search_paths = (
       resource_filename('c2cgeoform', 'templates/widgets'),
       resource_filename('deform', 'templates'))

But you can add you own widgets folder, in your package ``__init__.py`` file
before including ``c2cgeoform`` using:

.. code-block:: python

   import c2cgeoform
   search_paths = (
       (resource_filename(__name__, 'templates/widgets'),) +
       c2cgeoform.default_search_paths
   )
   c2cgeoform.default_search_paths = search_paths

With this, to overwrite globally the `Deform templates`_ or the templates coming from
``c2cgeoform`` (like the map widget), you just need to copy the template to your application
``templates/widgets`` folder.

.. _Chameleon: https://chameleon.readthedocs.org/en/latest/
.. _Deform templates: https://github.com/Pylons/deform/tree/master/deform/templates

Use a custom template for a form or a specific widget in a form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The form main template as each widget template can be changed locally by for a
given model by giving a ``template`` property to the ``Widget``.

.. code-block:: python

   base_schema = GeoFormSchemaNode(
       Comment,
       widget=FormWidget(template='comment'))

Note that it is possible to create a layout for the form fields without completely
overriding the form template by giving a ``fields_template`` to the form schema.

.. code-block:: python

   base_schema = GeoFormSchemaNode(
       Comment,
       widget=FormWidget(fields_template='comment_fields'))

Here is the default one: https://github.com/camptocamp/c2cgeoform/blob/master/c2cgeoform/templates/widgets/mapping_fields.pt
