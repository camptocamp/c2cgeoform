Configure the widgets
---------------------




The map widget
~~~~~~~~~~~~~~

All Deform `widgets`_ can be used with ``c2cgeoform``. Additionally,
``c2cgeoform`` provides a map widget for GeoAlchemy 2 geometry columns,
which allows to draw and modify geometries on an OpenLayers 3 map.

Example:

.. code-block:: python

    position = Column(
        geoalchemy2.Geometry('POINT', 4326, management=True), info={
            'colanderalchemy': {
                'title': 'Position',
                'typ': colander_ext.Geometry('POINT', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})

To customize the OpenLayers 3 map, the widget template ``map.pt`` has to
be overridden in your project templates/widgets folder, see: `page`_

Override the ``c2cgeoform/widgets/map.pt`` template in your project.

.. code-block:: shell

   mkdir c2cgeoform_project/templates/widgets
   cp ../.build/venv/src/c2cgeoform/c2cgeoform/templates/widgets/map.pt c2cgeoform_project/templates/widgets/

Customize the file, for example, replace :

.. code-block:: javascript

   source: new ol.source.MapQuest({layer: 'osm'})

by :

.. code-block:: javascript

   source: new ol.source.WMTS({
       requestEncoding: 'KVP',
       url: 'http://ows.asitvd.ch/wmts?',
       layer: 'asitvd.fond_couleur',
       matrixSet: '21781',
       tileGrid: new ol.tilegrid.WMTS({
          origin: [420000, 350000],
          resolutions: [4000, 3750, 3500, 3250, 3000, 2750, 2500,
                        2250, 2000, 1750, 1500, 1250, 1000, 750,
                        650, 500, 250, 100, 50, 20, 10, 5, 2.5, 2,
                        1.5, 1, 0.5, 0.25, 0.1, 0.05],
          matrixIds: [0, 1, 2, 3, 4, 5, 6,
                      7, 8, 9, 10, 11, 12, 13,
                      14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                      24, 25, 26, 27, 28, 29]
       }),
       attributions: [
           new ol.Attribution({
               html: 'géodonnées © <a href="http://www.asitvd.ch">ASIT VD</a> & © contributeurs <a href="www.openstreetmap.org">OpenStreetMap</a>'
           })
       ]
   })

and

.. code-block:: javascript

   view: new ol.View({
       center: defaultCenter,
       zoom: defaultZoom
   }),

by :

.. code-block:: javascript

   view: new ol.View({
       center: [539000, 181000],
       resolution: 10
   }),

.. _widgets: http://deform2demo.repoze.org/
.. _page: templates
