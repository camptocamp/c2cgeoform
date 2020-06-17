import OSM from 'ol/source/OSM'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import VectorLayer from 'ol/layer/Vector'
import TileLayer from 'ol/layer/Tile'
import Image from 'ol/layer/Image'
import XYZ from 'ol/source/XYZ'
import ImageWMS from 'ol/source/ImageWMS'

const DEFAULT_OPACITY = 0.8

export function createLayer(config) {
  let source
  switch (config.type_) {
    case 'WMTS':
      const { type_, tileGrid, ...options } = config
      if (tileGrid) options.tileGrid = new WMTSTileGrid(tileGrid)
      source = new WMTS(options)
      break
    case 'XYZ':
      source = new XYZ({
        url: config.url,
      })
      break
    case 'WMS':
      source = new ImageWMS({
        url: config.url,
      })
      return new Image({ source })
    case 'OSM':
    default:
      source = new OSM()
  }
  return new TileLayer({ source, opacity: config.opacity || DEFAULT_OPACITY })
}

export function createVectorLayer(source, style) {
  return new VectorLayer({ source, style })
}
