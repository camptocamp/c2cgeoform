from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    Date
    )

import geoalchemy2

import colander
import deform
from pkg_resources import resource_filename

from .schema import register_schema
from .ext import colander_ext, deform_ext
from .models import Base
from c2cgeoform import default_search_paths


class ExcavationPermission(Base):
    __tablename__ = 'excavations'
    __colanderalchemy_config__ = {
        'title':
            'Application form for permission to carry out excavation work',
        'description':
            'Apply to your municipal authority for permission to carry out \
            excavation work.'
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'title': 'Permission Number',
            'widget': deform.widget.HiddenWidget()
        }})
    referenceNumber = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Reference Number'
        }})
    requestDate = Column(Date, nullable=True, info={
        'colanderalchemy': {
            'title': 'Request Date'
        }})

    description = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Description of the Work',
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
    motif = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Motive for the Work',
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})

    locationStreet = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Street'
        }})
    locationPostalCode = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Postal Code'
        }})
    locationTown = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Town'
        }})
    locationPosition = Column(
        geoalchemy2.Geometry('POINT', 4326, management=True), info={
            'colanderalchemy': {
                'title': 'Position',
                'typ':
                    colander_ext.Geometry('POINT', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})

    # Person in Charge for the Work
    responsibleName = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Name'
        }})
    responsiblefFirstName = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'First Name'
        }})
    responsiblefMobile = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Mobile Phone'
        }})
    responsiblefMail = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Mail',
            'validator': colander.Email()
        }})
    responsiblefCompany = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Company'
        }})

    validated = Column(Boolean, info={
        'colanderalchemy': {
            'title': 'Validation',
            'label': 'Validated'
        }})


# overwrite the form template for the user view
pully_templates = resource_filename('c2cgeoform', 'templates/pully')
templates_user = (pully_templates,) + default_search_paths

register_schema(
    'fouille',
    ExcavationPermission,
    excludes_user=['referenceNumber', 'validated'],
    templates_user=templates_user
    )
