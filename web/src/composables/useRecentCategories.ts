import { ref, watch } from 'vue'

const STORAGE_KEY = 'nav_recent_categories'
const MAX = 5
function load(): string[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

const recent = ref<string[]>(load())
watch(recent, (v) => localStorage.setItem(STORAGE_KEY, JSON.stringify(v)), { deep: true })

export function useRecentCategories() {
  const add = (name: string) => {
    const next = recent.value.filter((x) => x !== name)
    next.unshift(name)
    recent.value = next.slice(0, MAX)
  }
  return { recentCategories: recent, addRecent: add }
}
