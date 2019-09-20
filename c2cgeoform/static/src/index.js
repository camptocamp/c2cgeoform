import GeoJSONFormat from 'ol/format/GeoJSON'
import Map from 'ol/Map'
import OSM from 'ol/source/OSM'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import View from 'ol/View'
import { get_default_styles } from './styles'

const format = new GeoJSONFormat()
const maps = []

export function init_form(oid, options) {
  const { center, zoom, fit_max_zoom } = options.view
  const geometry = format.readGeometry(options.geometry)
  const map = new Map({
    layers: [new TileLayer({ source: new OSM() })],
    target: `map_${oid}`,
    view: new View({ center, zoom }),
  })
  const source = new VectorSource()
  const vector = new VectorLayer({
    source: source,
    style: get_default_styles,
  })
  maps.push(oid)
}

export function exists(oid) {
  return oid in maps
}
