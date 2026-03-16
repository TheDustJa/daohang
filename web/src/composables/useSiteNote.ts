import { ref, watch } from 'vue'

const STORAGE_KEY = 'nav_site_notes'
function load(): Record<number, string> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

const notes = ref<Record<number, string>>(load())

watch(notes, (val) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
}, { deep: true })

export function useSiteNote() {
  const getNote = (id: number) => notes.value[id] || ''
  const setNote = (id: number, text: string) => {
    if (text.trim()) {
      notes.value = { ...notes.value, [id]: text }
    } else {
      const next = { ...notes.value }
      delete next[id]
      notes.value = next
    }
  }
  const hasNote = (id: number) => Boolean((notes.value[id] || '').trim())
  return { notes, getNote, setNote, hasNote }
}
