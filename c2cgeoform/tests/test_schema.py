import unittest
import unittest.mock as mock
from unittest.mock import patch

import colander
from sqlalchemy import Column, Integer, String

from c2cgeoform.models import Base
from c2cgeoform.schema import GeoFormSchemaNode


class FieldsCollection(Base):
    __tablename__ = "many_types_and_contraints_fields"

    id = Column(Integer, primary_key=True)
    text = Column(String(length=4))


class TestUniqueValidator(unittest.TestCase):
    def test_constraint_on_column_at_sql_alchemy_side_throw_colander_invalid(self):
        schema_node = GeoFormSchemaNode(FieldsCollection)
        schema_node.deserialize({"text": "foo"})
        try:
            schema_node.deserialize({"text": "more than five char"})
            assert False
        except colander.Invalid as e:
            assert "Longer than maximum length" in e.children[0].msg

    def test_custom_validator_triggered_at_serialization(self):
        schema_node = GeoFormSchemaNode(FieldsCollection)

        def side_effect(node, value):
            raise colander.Invalid(schema_node["text"], msg="test ERROR !")

        schema_node["text"].validator = side_effect
        try:
            schema_node.deserialize({"text": "foo"})
            assert False
        except colander.Invalid as e:
            assert "test ERROR !" == e.children[0].msg

    @patch("c2cgeoform.schema.unique_validator")
    def test_adding_validator_does_not_overrides_sqlalchemy_ones(self, unique_validator_mock):
        schema_node = GeoFormSchemaNode(FieldsCollection)
        schema_node.add_unique_validator(FieldsCollection.text, FieldsCollection.id)
        try:
            schema_node.deserialize({"text": "more than five char"})
            assert False
        except colander.Invalid as e:
            assert "Longer than maximum length" in e.children[0].msg[0]
            unique_validator_mock.assert_has_calls(
                [mock.call(mock.ANY, mock.ANY, mock.ANY, mock.ANY, "more than five char")]
            )

    @patch("c2cgeoform.schema.unique_validator")
    def test_adding_validator_does_not_overrides_custom_ones(self, unique_validator_mock):
        schema_node = GeoFormSchemaNode(FieldsCollection)

        def side_effect(node, value):
            raise colander.Invalid(schema_node["text"], msg="test ERROR !")

        schema_node["text"].validator = side_effect
        schema_node.add_unique_validator(FieldsCollection.text, FieldsCollection.id)
        try:
            schema_node.deserialize({"text": "foo"})
            assert False
        except colander.Invalid as e:
            assert "test ERROR !" == e.children[0].msg[0]
            unique_validator_mock.assert_has_calls([mock.call(mock.ANY, mock.ANY, mock.ANY, mock.ANY, "foo")])
