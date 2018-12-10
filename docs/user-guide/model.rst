.. _model:

Defining the model for a form
-----------------------------

The underlying schema for a ``c2cgeoform`` form is defined as SQLAlchemy
model. A simple definition is shown below:

.. code-block:: python

   from sqlalchemy import (Column, Integer, Text)
   import deform
   from uuid import uuid4

   from c2cgeoform.models import Base


   class Comment(Base):
       __tablename__ = 'comments'
       __colanderalchemy_config__ = {
           'title': 'A very simple form'
       }

       id = Column(Integer, primary_key=True, info={
           'colanderalchemy': {
               'widget': deform.widget.HiddenWidget()
           }})

       hash = Column(Text, unique=True, default=lambda: str(uuid4(), info={
           'colanderalchemy': {
               'widget': HiddenWidget()
           }})

       name = Column(Text, nullable=False, info={
           'colanderalchemy': {
               'title': 'Name'
           }})

       comment = Column(Text, nullable=True, info={
           'colanderalchemy': {
               'title': 'Comment',
               'widget': deform.widget.TextAreaWidget(rows=3),
           }})

This SQLAlchemy model is enriched with properties for
`ColanderAlchemy`_, for example to set a title for a field, to use a
specific Deform `widget`_ or to use a Colander `validator`_.

In general, every SQLAlchemy model can be used as schema for a form. The
only requirements are:

-  The model class must contain exactly one primary key column. Tables
   with composite primary keys are not supported.

A more complex example for a model can be found `here`_. For more
information on how to define the model, please refer to the
documentation of `SQLAlchemy`_, `ColanderAlchemy`_, `Colander`_ and
`Deform`_.

.. _ColanderAlchemy: http://colanderalchemy.readthedocs.org/en/latest/
.. _widget: http://deform2demo.repoze.org/
.. _validator: http://colander.readthedocs.org/en/latest/api.html#validators
.. _here: https://github.com/camptocamp/c2cgeoform/blob/master/c2cgeoform/scaffolds/c2cgeoform/%2Bpackage%2B/models/c2cgeoform_demo.py_tmpl
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Colander: http://colander.readthedocs.org/en/latest/
.. _Deform: http://deform.readthedocs.org/en/latest/
