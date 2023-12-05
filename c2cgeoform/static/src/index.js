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
import { createLayer, createVectorLayer } from './layers.js'
import { getStyleFunction } from './styles'
import { defaults as controlDefaults } from 'ol/control'

const format = new GeoJSONFormat()
const widgets = {}
let itemIcon

export function initMap(target, options) {
  const source = new VectorSource()
  let vectorLayer = createVectorLayer(source)
  const context = { feature: null }
  vectorLayer.setStyle(getStyleFunction({ context }))

  let map = new Map({
    layers: options.baseLayers.map((def) => createLayer(def)).concat([vectorLayer]),
    target,
    view: new View(options.view || {}),
    controls: controlDefaults({
      zoomOptions: options,
    }),
  })
  if (options.view.initialExtent) {
    map.getView().fit(options.view.initialExtent)
  }

  if (options.url)
    fetch(options.url)
      .then((resp) => resp.json())
      .then((json) => format.readFeatures(json))
      .then((features) => {
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
  map.on('pointermove', (e) => {
    if (e.dragging) return
    let feature
    map.forEachFeatureAtPixel(e.pixel, (f) => (feature = f), {
      hitTolerance: 3,
    })
    map.getTargetElement().classList.toggle('hovering', !!feature)
    context.feature = feature
    vectorLayer.changed()
  })

  addGeolocation(map, options)
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
    layers: options.baseLayers.map((def) => createLayer(def)).concat([layer]),
    target,
    view: new View(options.view || {}),
    interactions: defaults({ onFocusOnly: options.onFocusOnly }),
    controls: controlDefaults({
      zoomOptions: options,
    }),
  })
  //Store map for oid
  widgets[oid] = map

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
    const interactions = addInteractions({
      map,
      source,
      type,
      input,
      multi,
      mobile: options.mobile,
    })
    addControls(
      Object.assign(options, {
        target,
        interactions,
        drawTooltip: options[`draw${type}Tooltip`],
        source,
        type,
      })
    )
  }
  // Force style to specific Icon
  if (itemIcon) layer.setStyle(getStyleFunction({ icon: itemIcon }))

  addGeolocation(map, options)
}

export function addLayer(oid, config) {
  const layer = createLayer(config)
  getObjectMap(oid).addLayer(layer)
  return layer
}

export function checkInitialized(oid) {
  return oid in widgets
}

export function getObjectMap(oid) {
  return widgets[oid]
}

export function setReadOnly(oid) {
  const map = getObjectMap(oid)
  map.getControls().clear()
  map.getInteractions().clear()
  map.getTargetElement().classList.add('c2cgeoform-readonly')
  map.updateSize()
}

export function registerProjection(epsg, def) {
  proj4.defs(epsg, def)
  register(proj4)
}

export function setItemIcon(url) {
  itemIcon = url
}
