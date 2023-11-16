from colander import null

from c2cgeoform.models import DBSession
from c2cgeoform.tests import DatabaseTestCase

from .models_test import EmploymentStatus, Person, Tag


class TestRelationSelectWidget(DatabaseTestCase):
    def test_serialize(self):
        from c2cgeoform.ext.deform_ext import RelationSelectWidget

        widget = RelationSelectWidget(EmploymentStatus, "id", "name")

        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.populate(DBSession, None)
        widget.serialize(field, null)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))

        first_value = renderer.kw["values"][0]
        self.assertEqual("0", first_value[0])
        self.assertEqual("Worker", first_value[1])

    def test_serialize_default_value(self):
        from c2cgeoform.ext.deform_ext import RelationSelectWidget

        widget = RelationSelectWidget(EmploymentStatus, "id", "name", ("", "- Select -"))

        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.populate(DBSession, None)
        widget.serialize(field, null)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))

        # first the default value
        first_value = renderer.kw["values"][0]
        self.assertEqual("", first_value[0])
        self.assertEqual("- Select -", first_value[1])

        # then the values loaded from the db
        snd_value = renderer.kw["values"][1]
        self.assertEqual("0", snd_value[0])
        self.assertEqual("Worker", snd_value[1])

    def test_serialize_order_by(self):
        from c2cgeoform.ext.deform_ext import RelationSelectWidget

        widget = RelationSelectWidget(EmploymentStatus, "id", "name", order_by="name")

        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.populate(DBSession, None)
        widget.serialize(field, null)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))

        first_value = renderer.kw["values"][0]
        self.assertEqual("3", first_value[0])
        self.assertEqual("Director", first_value[1])


class TestRelationSelect2Widget(DatabaseTestCase):
    def test_serialize_default_value(self):
        from c2cgeoform.ext.deform_ext import RelationSelect2Widget

        widget = RelationSelect2Widget(EmploymentStatus, "id", "name", ("", "- Select -"))

        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.populate(DBSession, None)
        widget.serialize(field, null)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))

        # first the default value
        first_value = renderer.kw["values"][0]
        self.assertEqual("", first_value[0])
        self.assertEqual("- Select -", first_value[1])

        # then the values loaded from the db
        snd_value = renderer.kw["values"][1]
        self.assertEqual("0", snd_value[0])
        self.assertEqual("Worker", snd_value[1])


class TestRelationRadioChoiceWidget(DatabaseTestCase):
    def test_serialize_default_value(self):
        from c2cgeoform.ext.deform_ext import RelationRadioChoiceWidget

        widget = RelationRadioChoiceWidget(EmploymentStatus, "id", "name")

        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.populate(DBSession, None)
        widget.serialize(field, null)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))

        # first the default value
        first_value = renderer.kw["values"][0]
        self.assertEqual("0", first_value[0])
        self.assertEqual("Worker", first_value[1])


class TestRelationCheckBoxListWidget(DatabaseTestCase):
    def test_serialize_empty(self):
        from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget

        widget = RelationCheckBoxListWidget(Tag, "id", "name")
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        widget.serialize(field, null)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))
        self.assertEqual(renderer.kw["cstruct"], [])

        first_value = renderer.kw["values"][0]
        self.assertEqual("0", first_value[0])
        self.assertEqual("Tag A", first_value[1])

    def test_serialize(self):
        from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget

        widget = RelationCheckBoxListWidget(Tag, "id", "name")
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        objs = [{"id": "0"}, {"id": "2"}]

        widget.serialize(field, objs)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))
        self.assertEqual(renderer.kw["cstruct"], ["0", "2"])

        first_value = renderer.kw["values"][0]
        self.assertEqual("0", first_value[0])
        self.assertEqual("Tag A", first_value[1])

    def test_serialize_wrong_mapping(self):
        from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget

        widget = RelationCheckBoxListWidget(EmploymentStatus, "id", "name")
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        objs = [{"bad_column": "101"}, {"bad_column": "102"}]

        with self.assertRaises(KeyError):
            widget.serialize(field, objs)

    def test_deserialize_empty(self):
        from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget

        widget = RelationCheckBoxListWidget(Tag, "id", "name")
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        result = widget.deserialize(field, null)
        self.assertEqual(result, [])

    def test_deserialize(self):
        from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget

        widget = RelationCheckBoxListWidget(Tag, "id", "name")
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        result = widget.deserialize(field, ["1", "2"])
        self.assertEqual(result, [{"id": "1"}, {"id": "2"}])


class TestRelationMultiSelect2Widget(DatabaseTestCase):
    def test_serialize_empty(self):
        from c2cgeoform.ext.deform_ext import RelationSelect2Widget

        widget = RelationSelect2Widget(Tag, "id", "name", multiple=True)
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        widget.serialize(field, null)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))
        self.assertEqual(renderer.kw["cstruct"], [])

        first_value = renderer.kw["values"][0]
        self.assertEqual("0", first_value[0])
        self.assertEqual("Tag A", first_value[1])

    def test_serialize(self):
        from c2cgeoform.ext.deform_ext import RelationSelect2Widget

        widget = RelationSelect2Widget(Tag, "id", "name", multiple=True)
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        objs = [{"id": "0"}, {"id": "2"}]

        widget.serialize(field, objs)
        self.assertEqual(renderer.kw["values"], _convert_values(widget.values))
        self.assertEqual(renderer.kw["cstruct"], ["0", "2"])

        first_value = renderer.kw["values"][0]
        self.assertEqual("0", first_value[0])
        self.assertEqual("Tag A", first_value[1])

    def test_serialize_wrong_mapping(self):
        from c2cgeoform.ext.deform_ext import RelationSelect2Widget

        widget = RelationSelect2Widget(EmploymentStatus, "id", "name", multiple=True)
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        objs = [{"bad_column": "101"}, {"bad_column": "102"}]

        with self.assertRaises(KeyError):
            widget.serialize(field, objs)

    def test_deserialize_empty(self):
        from c2cgeoform.ext.deform_ext import RelationSelect2Widget

        widget = RelationSelect2Widget(Tag, "id", "name", multiple=True)
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        result = widget.deserialize(field, null)
        self.assertEqual(result, [])

    def test_deserialize(self):
        from c2cgeoform.ext.deform_ext import RelationSelect2Widget

        widget = RelationSelect2Widget(Tag, "id", "name", multiple=True)
        renderer = DummyRenderer()

        field = _get_field("tags", renderer)
        widget.populate(DBSession, None)
        result = widget.deserialize(field, ["1", "2"])
        self.assertEqual(result, [{"id": "1"}, {"id": "2"}])


def _convert_values(values_tuple):
    return [(str(key), label) for (key, label) in values_tuple]


def _get_field(name, renderer):
    from colanderalchemy import SQLAlchemySchemaNode
    from deform import Form

    form = Form(SQLAlchemySchemaNode(Person), renderer=renderer)

    for field in form.children:
        if field.name == name:
            return field

    raise RuntimeError("Field not found")


class DummyRenderer:
    """A dummy renderer, borrowed from the deform tests."""

    def __init__(self, result=""):
        self.result = result

    def __call__(self, template, **kw):
        self.template = template
        self.kw = kw
        return self.result


class DummyField:
    """A dummy field, borrowed from the deform tests."""

    default = None
    error = None
    children = ()
    title = "title"
    description = "description"
    name = "name"
    cloned = False
    oid = "deformField1"
    required = True
    cstruct = null

    def __init__(self, schema=None, renderer=None, translations=None):
        self.schema = schema
        self.renderer = renderer
        self.translations = translations

    def clone(self):
        self.cloned = True
        return self

    def deserialize(self, pstruct):
        return self.widget.deserialize(self, pstruct)

    def translate(self, term):
        if self.translations is None:
            return term
        return self.translations.get(term, term)

    def render_template(self, template, **kw):
        return self.renderer(template, **kw)
