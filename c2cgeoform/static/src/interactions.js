import Draw from 'ol/interaction/Draw'
import GeoJSON from 'ol/format/GeoJSON'

const format = new GeoJSON()

export function addDrawInteraction(map, source, type, input) {
  const draw = new Draw({
    type,
  })
  map.addInteraction(draw)
  draw.on('drawend', e => {
    source.clear()
    source.addFeature(e.feature)
  })
  source.on(
    'addfeature',
    e => (input.value = format.writeGeometry(e.feature.getGeometry()))
  )
}
