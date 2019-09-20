import Feature from 'ol/Feature'
import GeoJSONFormat from 'ol/format/GeoJSON'
import Map from 'ol/Map'
import OSM from 'ol/source/OSM'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import View from 'ol/View'
import { addClearButton } from './controls'
import { addDrawInteraction } from './interactions'
import { getDefaultStyles } from './styles'

const format = new GeoJSONFormat()
const maps = []

export function init_form(oid, options, defs) {
  const { center, zoom, fit_max_zoom } = options.view
  const geometry = options.geojson ? format.readGeometry(options.geojson) : null
  const target = document.querySelector(`#map_${oid}`)
  const input = document.querySelector(`#${oid}`)
  const type = defs.point ? 'Point' : defs.line ? 'Line' : 'Polygon'

  const map = new Map({
    layers: [new TileLayer({ source: new OSM() })],
    target,
    view: new View({ center, zoom }),
  })
  const source = new VectorSource()
  const vector = new VectorLayer({
    source: source,
    style: getDefaultStyles,
  })
  map.addLayer(vector)

  // Existing geometry
  if (geometry) {
    source.addFeature(new Feature({ geometry }))
    map.getView().fit(geometry, {
      maxZoom: fit_max_zoom || 18
    })
  }
  addClearButton(target, defs.clearTooltip, source)
  addDrawInteraction(map, source, type, input)
  maps.push(oid)
}

export function exists(oid) {
  return oid in maps
}
