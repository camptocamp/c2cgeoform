import { fromLonLat } from 'ol/proj'

function createButton(container, options) {
  const { content, title, callback } = options
  const btn = document.createElement('button')
  btn.title = title
  btn.innerHTML = content
  btn.type = 'button'
  btn.addEventListener('click', (e) => {
    e.stopPropagation()
    callback()
  })
  container.appendChild(btn)
  return btn
}

export function addControls(options) {
  const { target, type, interactions, source } = options
  const { draw, modify } = interactions
  const container = document.createElement('div')
  container.classList.add('ol-control', 'ol-unselectable', 'c2cgeoform-controls')

  if (type !== 'Point') {
    createButton(container, {
      content: '<i class="glyphicon glyphicon-pencil"></i>',
      title: options.drawTooltip,
      callback: () => draw.setActive(true) && modify.setActive(false),
    })
    createButton(container, {
      content: '<i class="glyphicon glyphicon-move"></i>',
      title: options.modifyTooltip,
      callback: () => modify.setActive(true) && draw.setActive(false),
    })
  }
  createButton(container, {
    content: '<i class="glyphicon glyphicon-remove"></i>',
    title: options.clearTooltip,
    callback: () => source.clear(),
  })
  target.appendChild(container)
}

export function addGeolocation(map, options) {
  // getCurrentPosition is only available with HTTPS
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    return console.warn('Geolocation is only available with HTTPS protocol')
  }
  let container = document.createElement('div')
  container.classList.add('ol-control', 'c2cgeoform-locate-me-btn')
  createButton(container, {
    content: '<i class="glyphicon glyphicon-record"></i>',
    title: options.geolocationTooltip,
    callback: () =>
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          map.getView().animate({
            center: fromLonLat([longitude, latitude], map.getView().getProjection()),
            duration: 1500,
            zoom: 18,
          })
        },
        console.warn,
        {
          enableHighAccuracy: true,
        }
      ),
  })

  $(map.getViewport()).append(container)
}
