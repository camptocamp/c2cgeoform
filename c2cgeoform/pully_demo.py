from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean
    )

import colander
import deform

from .schema import register_schema
from .models import Base


class Person(Base):
    __tablename__ = 'models'
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
    validated = Column(Boolean, info={
        'colanderalchemy': {
            'title': 'Validation',
            'label': 'Validated'
        }})

register_schema('persons', Person, excludes_user=['validated'])
