// composables/useVolver.ts
// Reemplaza todos los botones "Volver" hardcodeados.
// Usa router.back() si hay historial, sino va al fallback.

import { useRouter, navigateTo } from '#app'

export const useVolver = (fallback = '/dashboard') => {
  const router = useRouter()

  const volver = () => {
    if (import.meta.client && window.history.length > 2) {
      router.back()
    } else {
      navigateTo(fallback)
    }
  }

  return { volver }
}
