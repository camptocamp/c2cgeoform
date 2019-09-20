function createButton(options) {
  const { content, title, callback, className } = options
  const container = document.createElement('div')
  container.classList.add('ol-control', 'ol-unselectable', className)
  const btn = document.createElement('button')
  btn.title = title
  btn.innerHTML = content
  btn.type = 'button'
  container.appendChild(btn)
  return container
}

export function addClearButton(el, title, source) {
  const content = '&times;'
  el.querySelector('.ol-viewport').appendChild(
    createButton({
      content,
      title,
      className: 'c2cgeoform-delete',
      callback: () => {
        source.clear()
      },
    })
  )
}
