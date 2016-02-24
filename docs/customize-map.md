## Customize the map widget

Override the `c2cgeoform/widgets/map.pt` template in your project.

```shell
cd MyProject
mkdir myproject/templates/widgets
cp ../.build/venv/src/c2cgeoform/c2cgeoform/templates/widgets/map.pt myproject/templates/widgets/
```

Customize the file, for example, replace :

```javascript
source: new ol.source.MapQuest({layer: 'osm'})
```

by :

```javascript
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
```

and

```javascript
view: new ol.View({
    center: defaultCenter,
    zoom: defaultZoom
}),
```

by :

```javascript
view: new ol.View({
    center: [539000, 181000],
    resolution: 10
}),
```
