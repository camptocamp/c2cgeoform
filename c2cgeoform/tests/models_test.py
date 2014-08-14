from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    ForeignKey
    )
from sqlalchemy.orm import relationship

import colander
import deform

from c2cgeoform.schema import register_schema
from c2cgeoform.models import Base


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
    personId = Column(Integer, ForeignKey('tests_persons.id'), info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget()
        }})


class Person(Base):
    __tablename__ = 'tests_persons'
    __colanderalchemy_config__ = {
        'title': 'A Person',
        'description': 'Tell us about you.'
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'title': 'ID',
            'widget': deform.widget.HiddenWidget()
        }})
    name = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Your name'
        }})
    firstName = Column(Text, nullable=False, info={
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
    validated = Column(Boolean, info={
        'colanderalchemy': {
            'title': 'Validation',
            'label': 'Validated',
            'admin_only': True
        }})

register_schema('tests_persons', Person)
