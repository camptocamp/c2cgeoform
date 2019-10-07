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

proj4.defs(
  'EPSG:21781',
  `+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1
  +x_0=600000 +y_0=200000 +ellps=bessel
  +towgs84=660.077,13.551,369.344,2.484,1.783,2.939,5.66 +units=m +no_defs`
)
register(proj4)

const format = new GeoJSONFormat()
const maps = []

export function init_form(oid, options, defs) {
  const { center, zoom, fit_max_zoom } = options.view
  const geometry = options.geojson ? format.readGeometry(options.geojson) : null
  const target = document.querySelector(`#map_${oid}`)
  const input = document.querySelector(`#${oid}`)
  const type = defs.point ? 'Point' : defs.line ? 'Line' : 'Polygon'

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
    addDrawInteraction(map, source, type, input)
  }
  maps.push(oid)
}

export function exists(oid) {
  return oid in maps
}

// Backwards compatibility
export const searchfields = {}
