# coding=utf-8
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    Boolean,
    Date,
    ForeignKey)
from sqlalchemy.orm import relationship
import geoalchemy2

import colander
import deform
from translationstring import TranslationStringFactory

from c2cgeoform.ext import colander_ext, deform_ext
from c2cgeoform.models import Base, FileData

_ = TranslationStringFactory('pully')


# FIXME a file upload memory store is not appropriate for production
# See http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html#deform.interfaces.FileUploadTempStore  # noqa
class FileUploadTempStore(dict):
    def preview_url(self, name):
        return None

_file_upload_temp_store = FileUploadTempStore()


class District(Base):
    __tablename__ = 'district'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    label = Column(Text, nullable=False)


class ContactPerson(Base):
    __tablename__ = 'contact_person'
    __colanderalchemy_config__ = {
        'title': _('Contact Person')
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget()
        }})
    first_name = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('First name')
        }})
    last_name = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Last name')
        }})
    permission_id = Column(Integer, ForeignKey('excavations.id'), info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget()
        }})
    verified = Column(Boolean)


class Photo(FileData, Base):
    __tablename__ = 'photo'
    # Setting unknown to 'preserve' is required in classes used as a
    # FileUpload field.
    __colanderalchemy_config__ = {
        'title': _('Photo'),
        'unknown': 'preserve',
        'widget': deform_ext.FileUploadWidget(_file_upload_temp_store)
    }
    permission_id = Column(Integer, ForeignKey('excavations.id'))


class Situation(Base):
    __tablename__ = 'situation'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    name_fr = Column(Text, nullable=False)


class SituationForPermission(Base):
    __tablename__ = 'situation_for_permission'

    id = Column(Integer, primary_key=True)
    situation_id = Column(
        Integer, ForeignKey('situation.id'))
    permission_id = Column(
        Integer, ForeignKey('excavations.id'))


# This is the main model class which is used to register a schema.
class ExcavationPermission(Base):
    __tablename__ = 'excavations'
    __colanderalchemy_config__ = {
        'title':
        _('Application form for permission to carry out excavation work')
    }

    id = Column(Integer, primary_key=True, info={
        # the `colanderalchemy` property allows to set a custom title for the
        # column or to use a specific widget.
        'colanderalchemy': {
            'title': _('Permission Number'),
            'widget': deform.widget.HiddenWidget(),
            # if the `admin_list` property is enabled for a column on the main
            # model, then this column will be shown in the admin list grid.
            'admin_list': True
        }})
    # the hash column is required for all main models
    hash = Column(Text, unique=True)
    reference_number = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Reference Number')
        }})
    request_date = Column(Date, nullable=True, info={
        'colanderalchemy': {
            'title': _('Request Date'),
            'admin_list': True
        }})

    description = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Description of the Work'),
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
    motif = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Motive for the Work'),
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
    situations = relationship(
        SituationForPermission,
        # by setting the `cascade` property to 'delete-orphan', situation
        # entities are deleted when they are removed from the relation.
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': _('Situation'),
                # this widget type shows a select widget where the values are
                # loaded from a database table. in this case the select options
                # are generated from the Situation table.
                'widget': deform_ext.RelationSelect2Widget(
                    Situation,
                    'id',
                    'name',
                    order_by='name',
                    multiple=True
                )
            }})
    # by default a Deform sequence widget is used for relationship columns,
    # which, for example, allows to create new contact persons in a sub-form.
    contact_persons = relationship(
        ContactPerson,
        # make sure persons are deleted when removed from the relation
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': _('Contact Persons')
            }})
    location_district_id = Column(Integer, ForeignKey('district.id'), info={
        'colanderalchemy': {
            'title': _('District'),
            'widget': deform_ext.RelationSelect2Widget(
                District,
                'id',
                # if the name for the options should be internationalized, one
                # can create columns like 'name_fr' and 'name_de' in the table
                # 'District'. then in the translation files, the column name
                # can be "translated" (e.g. the French "translation" for the
                # column name would be 'name_fr'). to apply the translation use
                # the label `_('name'))` instead of `name`.
                'name',
                order_by='name',
                default_value=('', _('- Select -')),
            )
        }})
    location_street = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Street')
        }})
    location_postal_code = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Postal Code')
        }})
    location_town = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Town')
        }})
    # this is a search field to search for an address
    address_id = Column(Integer, ForeignKey('address.id'), info={
        'colanderalchemy': {
            'title': _('Address'),
            'widget': deform_ext.RelationSearchWidget(
                url=lambda request: request.route_url('addresses'),
                model=Address,
                min_length=1,
                id_field='id',
                label_field='label'
            )
        }})
    # to show a map for a geometry column, the column has to be defined as
    # follows.
    location_position = Column(
        geoalchemy2.Geometry('POINT', 4326, management=True), info={
            'colanderalchemy': {
                'title': _('Position'),
                'typ':
                colander_ext.Geometry('POINT', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})

    # Person in Charge for the Work
    responsible_title = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Title'),
            'validator': colander.OneOf(['mr', 'mrs']),
            'widget': deform.widget.SelectWidget(values=(
                ('', _('- Select -')),
                ('mr', _('Mr.')),
                ('mrs', _('Mrs.'))
            ))
        }})
    responsible_name = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Name'),
            'admin_list': True
        }})
    responsible_first_name = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('First Name'),
            'admin_list': True
        }})
    responsible_mobile = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Mobile Phone')
        }})
    responsible_mail = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Mail'),
            'validator': colander.Email()
        }})
    responsible_company = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Company')
        }})

    validated = Column(Boolean, info={
        'colanderalchemy': {
            'title': _('Validation'),
            'label': _('Validated')
        }})

    # Work footprint
    work_footprint = Column(
        geoalchemy2.Geometry('MULTIPOLYGON', 4326, management=True), info={
            'colanderalchemy': {
                'title': _('Footprint for the Work'),
                'typ': colander_ext.Geometry(
                    'MULTIPOLYGON', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})

    # Photo
    photos = relationship(
        Photo,
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': _('Photo')
            }})


class BusStop(Base):
    __tablename__ = 'bus_stops'

    id = Column(BigInteger, primary_key=True)
    name = Column(Text)
    geom = Column(geoalchemy2.Geometry('POINT', 4326, management=True))


class Comment(Base):
    __tablename__ = 'comments'
    __colanderalchemy_config__ = {
        'title': 'A very simple form'
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'widget': deform.widget.HiddenWidget(),
            'admin_list': True
        }})
    hash = Column(Text, unique=True)
    name = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': 'Name'
        }})
    comment = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': 'Comment',
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
    bus_stop_id = Column(BigInteger, ForeignKey('bus_stops.id'), info={
        'colanderalchemy': {
            'title': 'Bus stop',
            'widget': deform_ext.RelationSelectMapWidget(
                label_field='name',
                url=lambda request: request.route_url('bus_stops')
            )
        }})


def setup_test_data(settings):
    from c2cgeoform.models import DBSession
    import transaction

    if DBSession.query(District).get(0) is None:
        DBSession.add(District(id=0, name="Pully"))
        DBSession.add(District(id=1, name="Paudex"))
        DBSession.add(District(id=2, name="Belmont-sur-Lausanne"))
        DBSession.add(District(id=3, name="Trois-Chasseurs"))
        DBSession.add(District(id=4, name="La Claie-aux-Moines"))
        DBSession.add(District(id=5, name="Savigny"))
        DBSession.add(District(id=6, name="Mollie-Margot"))

    if DBSession.query(Situation).get(0) is None:
        DBSession.add(Situation(id=0, name="Road", name_fr="Route"))
        DBSession.add(Situation(id=1, name="Sidewalk", name_fr="Trottoir"))
        DBSession.add(Situation(id=2, name="Berm", name_fr="Berme"))
        DBSession.add(Situation(
            id=3, name="Vegetated berm", name_fr="Berme végétalisée"))
        DBSession.add(Situation(id=4, name="Green zone", name_fr="Zone verte"))
        DBSession.add(Situation(id=5, name="Cobblestone", name_fr="Pavés"))

    if DBSession.query(BusStop).count() == 0:
        _add_bus_stops(DBSession, settings['bus_stops_file'])

    if DBSession.query(Address).get(0) is None:
        DBSession.add(Address(id=0, label="Bern"))
        DBSession.add(Address(id=1, label="Lausanne"))
        DBSession.add(Address(id=2, label="Genève"))
        DBSession.add(Address(id=3, label="Zurich"))
        DBSession.add(Address(id=4, label="Lugano"))

    transaction.commit()


def _add_bus_stops(session, filepath):
    """
    Load test data from a GeoJSON file.
    """
    import json
    from shapely.geometry import shape

    file = open(filepath)
    geojson = json.load(file)
    file.close()

    bus_stops = []
    for feature in geojson['features']:
        id = feature['id'].replace('node/', '')
        geometry = shape(feature['geometry'])
        name = feature['properties']['name'] \
            if 'name' in feature['properties'] else ''
        bus_stop = BusStop(
            id=long(float(id)),
            geom='SRID=4326;' + geometry.wkt,
            name=name)
        bus_stops.append(bus_stop)

    session.add_all(bus_stops)
