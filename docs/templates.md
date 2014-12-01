## Using custom templates

To customize applications built with `c2cgeoform`, the [Chameleon](
https://chameleon.readthedocs.org/en/latest/) templates can be overwritten.
`c2cgeoform` distinguishes between two types of templates: **site** templates
and Deform **form** templates. Site templates are used by the views and
provide the site structure. Form templates are templates for the Deform
form and field widgets.

### Overwriting site templates

The default `c2cgeoform` templates are located in [templates/sites](
../c2cgeoform/templates/sites). To use custom templates, the templates
asset has to be overwritten, for example like this:

    config.override_asset(
        to_override='c2cgeoform:templates/sites/',
        override_with='myproject:templates/sites/')

For more information please refer to the Pyramid documentation (["Static Assets:
The override_asset API"](http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/assets.html#the-override-asset-api)).

### Overwriting form templates

To overwrite the [Deform templates](https://github.com/Pylons/deform/tree/master/deform/templates)
or the templates of `c2cgeoform` widgets (like the map widget), a custom
template directory can be provided when registering a schema:

    register_schema(
        'person',
        model.Person,
        templates_user=resource_filename('myproject', 'templates_user')
        templates_admin=resource_filename('myproject', 'templates_admin'))

Because several `c2cgeoform` views use forms and to make it possible to
customize the forms in these different views, `c2cgeoform` uses separate form
templates for each view. The mapping between view and form template is as
follows:

* View `form`: `[templates_user/]form.pt`
* View `confirmation`: `[templates_user/]readonly/form_confirmation.pt`
* View `view_user`: `[templates_user/]readonly/form_view_user.pt`
* View `edit` (admin): `[templates_admin/]form.pt`
* View `view_admin` (admin): `[templates_admin/]readonly/form.pt`
