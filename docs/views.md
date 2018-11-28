## Create a views class for your model

There is already a views class created in your project by the scaffold, see
file `views/excavation.py`.

To ease creation of views classes, c2cgeoform comes with an abstract view class
that contains base methods to display grids and render forms, and update data
in database on form post.

Create a new views class by extending c2cgeoform's `AbstractViews`:

@view_defaults(match_param='table=excavations')
class ExcavationViews(AbstractViews):
