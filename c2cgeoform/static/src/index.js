import Feature from 'ol/Feature'
import GeoJSONFormat from 'ol/format/GeoJSON'
import Map from 'ol/Map'
import VectorSource from 'ol/source/Vector'
import View from 'ol/View'
import proj4 from 'proj4'
import { register } from 'ol/proj/proj4'
import { addControls, addGeolocation } from './controls'
import { addInteractions } from './interactions'
import { createBaseLayer, createVectorLayer } from './layers.js'
import { getStyleFunction } from './styles'

const format = new GeoJSONFormat()
const widgets = []
let itemIcon

export function initMap(target, options) {
  const source = new VectorSource()
  source.on('addfeature', () => map.getView().fit(source.getExtent()))
  let vectorLayer = createVectorLayer(source)
  const context = { feature: null }
  vectorLayer.setStyle(getStyleFunction({ opacity: 0.5, context }))

  let map = new Map({
    layers: [createBaseLayer(options.baselayer), vectorLayer],
    target,
    view: new View(),
  })
  if (options.url)
    fetch(options.url)
      .then(resp => resp.json())
      .then(json => format.readFeatures(json))
      .then(features => {
        source.addFeatures(features)
        options.onFeatureLoad(features)
      })

  // Change feature style on Hover
  map.on('pointermove', e => {
    if (e.dragging) return
    let feature
    map.forEachFeatureAtPixel(e.pixel, f => (feature = f), { hitTolerance: 3 })
    map.getTargetElement().classList.toggle('hovering', !!feature)
    context.feature = feature
    vectorLayer.changed()
  })

  // On feature click redirect to url in feature property
  map.on('click', e =>
    map.forEachFeatureAtPixel(
      e.pixel,
      f => (window.location.href = f.getProperties()['url'])
    )
  )
  addGeolocation(map)
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
  const layer = createVectorLayer(source)
  const map = new Map({
    layers: [createBaseLayer(options.baselayer), layer],
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
  // Force style to specific Icon
  if (itemIcon) layer.setStyle(getStyleFunction({ icon: itemIcon }))

  addGeolocation(map)
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

export function setItemIcon(url) {
  itemIcon = url
}
