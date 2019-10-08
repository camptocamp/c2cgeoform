function createButton(options) {
  const { content, title, callback, className } = options
  const container = document.createElement('div')
  container.classList.add('ol-control', 'ol-unselectable', className)
  const btn = document.createElement('button')
  btn.title = title
  btn.innerHTML = content
  btn.type = 'button'
  btn.addEventListener('click', e => {
    e.stopPropagation()
    callback()
  })
  container.appendChild(btn)
  return container
}

export function addClearButton(el, title, source) {
  const content = '&times;'
  el.appendChild(
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
