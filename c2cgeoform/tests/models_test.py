from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    ForeignKey)
from sqlalchemy.orm import relationship

import colander
import deform

from c2cgeoform.schema import register_schema
from c2cgeoform.models import Base
from c2cgeoform.ext.deform_ext import RelationSelect2Widget


class EmploymentStatus(Base):
    __tablename__ = 'tests_employment_status'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Phone(Base):
    __tablename__ = 'tests_phones'

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget()
        }})
    number = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Phone number'
        }})
    person_id = Column(Integer, ForeignKey('tests_persons.id'), info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget()
        }})
    verified = Column(Boolean)


class Tag(Base):
    __tablename__ = 'tests_tags'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class TagsForPerson(Base):
    __tablename__ = 'tests_tags_for_person'

    id = Column(Integer, primary_key=True)
    tag_id = Column(
        Integer, ForeignKey('tests_tags.id'))
    person_id = Column(
        Integer, ForeignKey('tests_persons.id'))


class Person(Base):
    __tablename__ = 'tests_persons'
    __colanderalchemy_config__ = {
        'title': 'A Person',
        'description': 'Tell us about you.'
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'title': 'ID',
            'widget': deform.widget.HiddenWidget(),
            'admin_list': True
        }})
    hash = Column(Text, unique=True)
    name = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Your name',
            'admin_list': True
        }})
    first_name = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Your first name'
        }})
    age = Column(Integer, info={
        'colanderalchemy': {
            'title': 'Your age',
            'validator': colander.Range(18,)
        }})
    phones = relationship(
        Phone,
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': 'Phone numbers',
            }})
    tags = relationship(
        TagsForPerson,
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': 'Tags',
                'widget': RelationSelect2Widget(
                    Tag,
                    'id',
                    'name',
                    order_by='name',
                    multiple=True
                )
            }})
    validated = Column(Boolean, info={
        'colanderalchemy': {
            'title': 'Validation',
            'label': 'Validated'
        }})

register_schema(
    'tests_persons', Person,
    excludes_user=['validated'],
    overrides_user={
        'name': {'title': 'The Name'},
        'phones': {'excludes': 'verified'}
    })
