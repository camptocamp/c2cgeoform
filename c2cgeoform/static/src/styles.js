import { Circle, Fill, Stroke, Style } from 'ol/style.js'

export function get_default_styles() {
  return [
    new Style({
      stroke: new Stroke({
        color: 'blue',
        width: 3,
      }),
      fill: new Fill({
        color: 'rgba(0, 0, 255, 0.1)',
      }),
      image: new Circle({
        radius: 6,
        stroke: new Stroke({
          width: 1.5,
          color: 'rgba(0, 0, 255, 1)',
        }),
        fill: new Fill({
          color: 'rgba(0, 0, 255, 0.4)',
        }),
      }),
    }),
  ]
}
