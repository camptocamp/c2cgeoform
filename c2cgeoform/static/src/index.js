import Feature from 'ol/Feature'
import GeoJSONFormat from 'ol/format/GeoJSON'
import Map from 'ol/Map'
import VectorSource from 'ol/source/Vector'
import View from 'ol/View'
import proj4 from 'proj4'
import { register } from 'ol/proj/proj4'
import { click, pointerMove } from 'ol/events/condition.js'
import Select from 'ol/interaction/Select.js'
import { addControls } from './controls'
import { addInteractions } from './interactions'
import { createBaseLayer, createVectorLayer } from './layers.js'
import { getDefaultIconStyle } from './styles'

const format = new GeoJSONFormat()
const widgets = []

export function initMap(target, options) {
  const source = new VectorSource()
  const url = options.url || null // base url to redirect
  let vectorLayer = createVectorLayer(source)
  vectorLayer.setStyle(function(feature) {
    return getDefaultIconStyle(feature, (options = { opacity: 0.5 }))
  })

  let map = new Map({
    layers: [createBaseLayer(options.baselayer), vectorLayer],
    target: target,
    view: new View(),
  })
  fetch(url)
    .then(resp => resp.json())
    .then(json => {
      source.addFeatures(format.readFeatures(json))
      map.getView().fit(source.getExtent())
    })
  // Change feature style on Hover
  const selectPointerMove = new Select({
    condition: pointerMove,
    style: function(feature) {
      return getDefaultIconStyle(feature, (options = { opacity: 1 }))
    },
  })
  map.addInteraction(selectPointerMove)

  // On feature click redirect to url in feature property
  map.on('click', function(evt) {
    let feature = map.forEachFeatureAtPixel(evt.pixel, function(feature) {
      return feature
    })
    if (feature) {
      window.location.href = feature.getProperties()['url']
    }
  })
  return map
}

export function initMapWidget(oid, options, defs) {
  if (checkInitialized(oid)) return
  const { center, zoom, fit_max_zoom } = options.view
  const geometry = options.geojson ? format.readGeometry(options.geojson) : null
  const target = document.querySelector(`#map_${oid}`)
  const input = document.querySelector(`#${oid}`)
  const type = defs.point ? 'Point' : defs.line ? 'Line' : 'Polygon'
  const multi = defs.isMultiGeometry

  const source = new VectorSource()
  const map = new Map({
    layers: [createBaseLayer(options.baselayer), createVectorLayer(source)],
    target,
    view: new View({ center, zoom }),
  })

  // Existing geometry
  if (geometry) {
    source.addFeature(new Feature({ geometry }))
    map.getView().fit(geometry, { maxZoom: fit_max_zoom || 18 })
  }
  if (!defs.readonly) {
    const interactions = addInteractions({ map, source, type, input, multi })
    addControls({
      target,
      interactions,
      i18n: { clear: defs.clearTooltip },
      source,
    })
  }
}

export function checkInitialized(oid) {
  const initialized = widgets.includes(oid)
  widgets.push(oid)
  return initialized
}

export function registerProjection(epsg, def) {
  proj4.defs(epsg, def)
  register(proj4)
}
