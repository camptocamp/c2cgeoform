import Feature from 'ol/Feature'
import GeoJSONFormat from 'ol/format/GeoJSON'
import Map from 'ol/Map'
import VectorSource from 'ol/source/Vector'
import View from 'ol/View'
import { defaults } from 'ol/interaction'
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
  let vectorLayer = createVectorLayer(source)
  const context = { feature: null }
  vectorLayer.setStyle(getStyleFunction({ opacity: 0.5, context }))

  let map = new Map({
    layers: options.baseLayers
      .map(def => createBaseLayer(def))
      .concat([vectorLayer]),
    target,
    view: new View(options.view || {}),
  })
  if (options.view.initialExtent) {
    map.getView().fit(options.view.initialExtent)
  }

  if (options.url)
    fetch(options.url)
      .then(resp => resp.json())
      .then(json => format.readFeatures(json))
      .then(features => {
        source.addFeatures(features)
        if (options.fitSource) {
          map.getView().fit(source.getExtent(), {
            maxZoom: options.fitMaxZoom || 18,
          })
        }
        if (options.onFeaturesLoaded) {
          options.onFeaturesLoaded(features)
        }
      })

  // Change feature style on Hover
  map.on('pointermove', e => {
    if (e.dragging) return
    if (context.feature) {
      context.feature.__over = false
    }
    let feature
    map.forEachFeatureAtPixel(e.pixel, f => (feature = f), { hitTolerance: 3 })
    map.getTargetElement().classList.toggle('hovering', !!feature)
    context.feature = feature
    if (context.feature) {
      context.feature.__over = true
    }
    vectorLayer.changed()
  })

  addGeolocation(map)
  return map
}

export function initMapWidget(oid, options) {
  if (checkInitialized(oid)) return
  const geometry = options.geojson ? format.readGeometry(options.geojson) : null
  const target = document.querySelector(`#map_${oid}`)
  const input = document.querySelector(`#${oid}`)
  const type = options.point ? 'Point' : options.line ? 'Line' : 'Polygon'
  const multi = options.isMultiGeometry

  const source = new VectorSource()
  const layer = createVectorLayer(source)
  const map = new Map({
    layers: options.baseLayers.map(def => createBaseLayer(def)).concat([layer]),
    target,
    view: new View(options.view || {}),
    interactions: defaults({ onFocusOnly: options.onFocusOnly }),
  })

  if (options.onFocusOnly) map.getTargetElement().setAttribute('tabindex', '0')

  // Existing geometry
  if (geometry) {
    source.addFeature(new Feature({ geometry }))
    map.getView().fit(geometry, {
      maxZoom: options.fitMaxZoom || 18,
      padding: [20, 20, 20, 20],
    })
  } else if (options.view.initialExtent) {
    map.getView().fit(options.view.initialExtent)
  }
  if (!options.readonly) {
    const interactions = addInteractions({ map, source, type, input, multi })
    addControls({
      target,
      interactions,
      i18n: {
        draw: options[`draw${type}Tooltip`],
        edit: options.modifyTooltip,
        clear: options.clearTooltip,
      },
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
