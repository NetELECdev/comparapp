// composables/useDragScroll.ts
// Permite arrastrar con el mouse (click + mover) para scrollear
// contenedores horizontales en desktop, sin afectar touch/mobile.

import { ref, onMounted, onUnmounted, type Ref } from 'vue'

export function useDragScroll(elRef: Ref<HTMLElement | null>) {
  const isDragging = ref(false)
  let startX = 0
  let scrollLeft = 0
  let moved = false

  function onMouseDown(e: MouseEvent) {
    const el = elRef.value
    if (!el) return
    isDragging.value = true
    moved = false
    startX = e.pageX - el.offsetLeft
    scrollLeft = el.scrollLeft
    el.classList.add('is-dragging')
  }

  function onMouseMove(e: MouseEvent) {
    const el = elRef.value
    if (!isDragging.value || !el) return
    e.preventDefault()
    const x = e.pageX - el.offsetLeft
    const walk = x - startX
    if (Math.abs(walk) > 5) moved = true
    el.scrollLeft = scrollLeft - walk
  }

  function onMouseUp() {
    const el = elRef.value
    isDragging.value = false
    el?.classList.remove('is-dragging')
  }

  // Evita que un arrastre se interprete como click en los hijos (botones/links)
  function onClickCapture(e: MouseEvent) {
    if (moved) {
      e.preventDefault()
      e.stopPropagation()
    }
  }

  onMounted(() => {
    const el = elRef.value
    if (!el) return
    el.addEventListener('mousedown', onMouseDown)
    el.addEventListener('mousemove', onMouseMove)
    el.addEventListener('mouseup', onMouseUp)
    el.addEventListener('mouseleave', onMouseUp)
    el.addEventListener('click', onClickCapture, true)
  })

  onUnmounted(() => {
    const el = elRef.value
    if (!el) return
    el.removeEventListener('mousedown', onMouseDown)
    el.removeEventListener('mousemove', onMouseMove)
    el.removeEventListener('mouseup', onMouseUp)
    el.removeEventListener('mouseleave', onMouseUp)
    el.removeEventListener('click', onClickCapture, true)
  })

  return { isDragging }
}