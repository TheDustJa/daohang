import { ref, watch } from 'vue'

const KEY = 'nav_card_font_size'
type Size = 'sm' | 'md' | 'lg'

function load(): Size {
  try {
    const v = localStorage.getItem(KEY)
    if (v === 'sm' || v === 'md' || v === 'lg') return v
  } catch { /* ignore */ }
  return 'md'
}

const cardFontSize = ref<Size>(load())
watch(cardFontSize, (v) => localStorage.setItem(KEY, v), { immediate: true })

export function useCardFontSize() {
  return { cardFontSize }
}
