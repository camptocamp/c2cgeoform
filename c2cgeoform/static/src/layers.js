import OSM from 'ol/source/OSM'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import VectorLayer from 'ol/layer/Vector'
import TileLayer from 'ol/layer/Tile'
import { getDefaultStyle } from './styles'

export function createBaseLayer(config) {
  let source
  switch (config.type_) {
    case 'WMTS':
      const { type_, tileGrid, ...options } = config
      if (tileGrid) options.tileGrid = new WMTSTileGrid(tileGrid)
      source = new WMTS(options)
      break
    case 'OSM':
    default:
      source = new OSM()
  }
  return new TileLayer({ source })
}

export function createVectorLayer(source) {
  return new VectorLayer({ source, style: getDefaultStyle() })
}