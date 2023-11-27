import io
import json
import os
from io import BytesIO
from typing import Any, Union

import colander
import pyproj
from colander import Invalid, SchemaType
from geoalchemy2 import WKBElement
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape
from shapely.ops import transform
from typing_extensions import Buffer


class Geometry(SchemaType):  # type: ignore[misc]
    """A Colander type meant to be used with GeoAlchemy 2 geometry columns.

    Example usage

    .. code-block:: python

        geom = Column(
            geoalchemy2.Geometry('POLYGON', 4326), info={
                'colanderalchemy': {
                    'typ': colander_ext.Geometry(
                        'POLYGON', srid=4326, map_srid=3857),
                    'widget': deform_ext.MapWidget()
                }})

    **Attributes/Arguments**

    geometry_type
        The geometry type should match the column geometry type.

    srid
        The SRID of the geometry should also match the column definition.

    map_srid
        The projection used for the OpenLayers map. The geometries will be
        reprojected to this projection.

    """

    def __init__(self, geometry_type: str = "GEOMETRY", srid: int = -1, map_srid: int = -1) -> None:
        self.geometry_type = geometry_type.upper()
        self.srid = int(srid)
        self.map_srid = int(map_srid)
        if self.map_srid == -1:
            self.map_srid = self.srid

        if self.srid != self.map_srid:
            self.project_db_to_map = pyproj.Transformer.from_crs(
                self.srid,
                self.map_srid,
                always_xy=True,
            ).transform

            self.project_map_to_db = pyproj.Transformer.from_crs(
                self.map_srid,
                self.srid,
                always_xy=True,
            ).transform

    def serialize(
        self, node: Any, appstruct: Union[colander._null, WKBElement]
    ) -> Union[colander._null, str]:
        """
        In Colander speak: Converts a Python data structure (an appstruct) into
        a serialization (a cstruct).
        Or: Converts a `WKBElement` into a GeoJSON string.
        """

        if appstruct is colander.null:
            return colander.null
        if isinstance(appstruct, WKBElement):
            geometry = to_shape(appstruct)
            if self.map_srid not in (self.srid, appstruct.srid):
                geometry = transform(self.project_db_to_map, geometry)

            return json.dumps(mapping(geometry))
        raise Invalid(node, "Unexpected value: %r" % appstruct)

    def deserialize(self, node: Any, cstruct: Union[colander._null, str]) -> Union[colander._null, str]:
        """
        In Colander speak: Converts a serialized value (a cstruct) into a
        Python data structure (a appstruct).
        Or: Converts a GeoJSON string into a `WKBElement`.
        """

        if cstruct is colander.null or cstruct == "":
            return colander.null
        try:
            # TODO Shapely does not support loading GeometryCollections from
            # GeoJSON, see https://github.com/Toblerity/Shapely/issues/115
            geometry = shape(json.loads(cstruct))
        except Exception as exception:
            raise Invalid(node, f"Invalid geometry: {cstruct!r}") from exception

        if self.srid != self.map_srid:
            geometry = transform(self.project_map_to_db, geometry)

        return from_shape(geometry, srid=self.srid)


class BinaryData(SchemaType):  # type: ignore[misc]
    """A Colander type meant to be used with ``LargeBinary`` columns.

    Example usage

    .. code-block:: python

        class Model():
            id = Column(Integer, primary_key=True)
            data = Column(LargeBinary, info={
                'colanderalchemy': {
                    'typ': colander_ext.BinaryData()
                }})

    It is usually not used directly in application models, but through
    the ``c2cgeoform.models.FileData`` mixin, which is meant to be used
    with a ``deform_ext.FileUploadWidget``.

    The serialize method just returns ``colander.null``. This is because
    the ``FileUploadWidget``'s template does not use and need the binary
    data.

    The deserialize method gets a Python ``file`` object and returns a
    bytes string that is appropriate for the database.

    """

    def serialize(
        self, node: colander.SchemaNode, appstruct: Union[colander._null, Buffer]
    ) -> Union[colander._null, io.BytesIO]:
        """
        In Colander speak: Converts a Python data structure (an appstruct) into
        a serialization (a cstruct).
        """
        del node  # unused

        if appstruct is colander.null or appstruct == "":
            return colander.null
        return BytesIO(appstruct)

    def deserialize(
        self, node: colander.SchemaNode, cstruct: Union[colander._null, str, io.IOBase]
    ) -> Union[colander._null, bytes]:
        """
        In Colander speak: Converts a serialized value (a cstruct) into a
        Python data structure (a appstruct).
        Or: Converts a Python file stream to plain binary data.
        """
        del node  # unused

        if cstruct is colander.null or cstruct == "":
            return colander.null
        assert isinstance(cstruct, io.IOBase)
        byte_array = cstruct.read()
        # set the file position back to 0, so that the file can be read again
        cstruct.seek(0, os.SEEK_SET)
        return byte_array
