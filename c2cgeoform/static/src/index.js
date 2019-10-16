import Feature from 'ol/Feature'
import GeoJSONFormat from 'ol/format/GeoJSON'
import Map from 'ol/Map'
import VectorSource from 'ol/source/Vector'
import View from 'ol/View'
import proj4 from 'proj4'
import { defaults } from 'ol/interaction'
import { register } from 'ol/proj/proj4'

import { addClearButton } from './controls'
import { addDrawInteraction } from './interactions'
import { createBaseLayer, createVectorLayer } from './layers.js'

register(proj4)

const format = new GeoJSONFormat()
const widgets = []

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
    addClearButton(target, defs.clearTooltip, source)
    addDrawInteraction({ map, source, type, input, multi })
  }
}

export function checkInitialized(oid) {
  const initialized = widgets.includes(oid)
  widgets.push(oid)
  return initialized
}

export function registerProjection(epsg, def) {
  proj4.defs(epsg, def)
}
