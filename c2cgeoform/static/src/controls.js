import { fromLonLat } from 'ol/proj'

function createButton(container, options) {
  const { content, title, callback } = options
  const btn = document.createElement('button')
  btn.title = title
  btn.innerHTML = content
  btn.type = 'button'
  btn.addEventListener('click', e => {
    e.stopPropagation()
    callback()
  })
  container.appendChild(btn)
  return btn
}

export function addControls(options) {
  const { target, i18n, interactions, source } = options
  const { draw, modify } = interactions
  const container = document.createElement('div')
  container.classList.add(
    'ol-control',
    'ol-unselectable',
    'c2cgeoform-controls'
  )

  createButton(container, {
    content: '<i class="glyphicon glyphicon-pencil"></i>',
    title: i18n.draw,
    callback: () => draw.setActive(true) && modify.setActive(false),
  })
  createButton(container, {
    content: '<i class="glyphicon glyphicon-move"></i>',
    title: i18n.edit,
    callback: () => modify.setActive(true) && draw.setActive(false),
  })
  createButton(container, {
    content: '<i class="glyphicon glyphicon-remove"></i>',
    title: i18n.clear,
    callback: () => source.clear(),
  })
  target.appendChild(container)
}

export function addGeolocation(map) {
  // getCurrentPosition is only available with HTTPS
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    console.warn('Geolocation is only available with HTTPS protocol')
    return
  }
  let container = document.createElement('div')
  container.classList.add('ol-control', 'c2cgeoform-locate-me-btn')
  createButton(container, {
    content: '<i class="glyphicon glyphicon-record"></i>',
    callback: () =>
      navigator.geolocation.getCurrentPosition(
        position => {
          const { latitude, longitude } = position.coords
          map.getView().animate({
            center: fromLonLat([longitude, latitude]),
            duration: 1500,
            zoom: 18,
          })
        },
        err => console.warn(`ERROR(${err.code}): ${err.message}`),
        {
          enableHighAccuracy: true,
        }
      ),
  })

  $(map.getTargetElement()).append(container)
}
