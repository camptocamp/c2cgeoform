import colander
import deform
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship

from c2cgeoform.ext.deform_ext import RelationSelect2Widget
from c2cgeoform.models import Base


class EmploymentStatus(Base):
    __tablename__ = "tests_employment_status"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Phone(Base):
    __tablename__ = "tests_phones"

    id = Column(Integer, primary_key=True, info={"colanderalchemy": {"widget": deform.widget.HiddenWidget()}})
    number = Column(Text, nullable=False, info={"colanderalchemy": {"title": "Phone number"}})
    person_id = Column(
        Integer,
        ForeignKey("tests_persons.id"),
        info={"colanderalchemy": {"widget": deform.widget.HiddenWidget()}},
    )
    verified = Column(Boolean)


class Tag(Base):
    __tablename__ = "tests_tags"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


person_tag = Table(
    "person_tag",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tests_tags.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("tests_persons.id"), primary_key=True),
)


class Person(Base):
    __tablename__ = "tests_persons"
    __colanderalchemy_config__ = {"title": "A Person", "description": "Tell us about you."}
    __c2cgeoform_config__ = {"duplicate": True}

    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"title": "ID", "widget": deform.widget.HiddenWidget()}},
    )
    hash = Column(Text, unique=True)
    name = Column(
        Text,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Your name",
            },
            "c2cgeoform": {"duplicate": True},
        },
    )
    first_name = Column(
        Text,
        nullable=False,
        info={"colanderalchemy": {"title": "Your first name"}, "c2cgeoform": {"duplicate": True}},
    )
    age = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Your age",
                "validator": colander.Range(
                    18,
                ),
            }
        },
    )
    phones = relationship(
        Phone,
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {
                "title": "Phone numbers",
            }
        },
    )
    tags = relationship(
        "Tag",
        secondary=person_tag,
        cascade="save-update,merge,refresh-expire",
        info={
            "colanderalchemy": {
                "title": "Tags",
                "widget": RelationSelect2Widget(Tag, "id", "name", order_by="name", multiple=True),
                "includes": ["id"],
            }
        },
    )

    validated = Column(Boolean, info={"colanderalchemy": {"title": "Validation", "label": "Validated"}})
