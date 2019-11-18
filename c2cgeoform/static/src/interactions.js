import Draw from 'ol/interaction/Draw'
import Modify from 'ol/interaction/Modify'
import GeoJSON from 'ol/format/GeoJSON'
import MultiPoint from 'ol/geom/MultiPoint'
import MultiLineString from 'ol/geom/MultiLineString'
import MultiPolygon from 'ol/geom/MultiPolygon'

const format = new GeoJSON()

export function addInteractions(options) {
  const { input, multi, ...interactionOptions } = options
  const draw = addDrawInteraction(interactionOptions)
  const modify = addModifyInteraction(interactionOptions)
  modify.setActive(false)
  options.source.on(
    'change',
    e =>
      (input.value =
        options.source.getFeatures().length > 0
          ? getGeometryJSON(
              options.source.getFeatures()[0].getGeometry(),
              multi
            )
          : '')
  )
  return { draw, modify }
}

export function addDrawInteraction(options) {
  const { map, source, type } = options
  const draw = new Draw({ type })
  map.addInteraction(draw)
  draw.on('drawstart', e => source.clear())
  draw.on('drawend', e => source.addFeature(e.feature))
  return draw
}

export function addModifyInteraction(options) {
  const { map, source } = options
  const modify = new Modify({ source })
  map.addInteraction(modify)
  return modify
}

function getGeometryJSON(geometry, multi) {
  const classes = {
    Point: MultiPoint,
    LineString: MultiLineString,
    Polygon: MultiPolygon,
  }
  if (multi && geometry.getType() in classes) {
    geometry = new classes[(geometry.getType())]([geometry.getCoordinates()])
  }
  return format.writeGeometry(geometry)
}
