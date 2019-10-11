import Draw from 'ol/interaction/Draw'
import GeoJSON from 'ol/format/GeoJSON'
import MultiPoint from 'ol/geom/MultiPoint'
import MultiLineString from 'ol/geom/MultiLineString'
import MultiPolygon from 'ol/geom/MultiPolygon'

const format = new GeoJSON()

export function addDrawInteraction(options) {
  const { map, source, type, input, multi } = options
  const draw = new Draw({
    type,
  })
  map.addInteraction(draw)
  draw.on('drawstart', e => {
    source.clear()
  })
  draw.on('drawend', e => {
    source.addFeature(e.feature)
  })
  source.on(
    'addfeature',
    e => (input.value = getGeometryJSON(e.feature.getGeometry(), multi))
  )
}

function getGeometryJSON(geometry, multi) {
  const classes = {
    Point: MultiPoint,
    LineString: MultiLineString,
    Polygon: MultiPolygon,
  }
  if (multi) {
    geometry = new classes[(geometry.getType())]([geometry.getCoordinates()])
  }
  return format.writeGeometry(geometry)
}
