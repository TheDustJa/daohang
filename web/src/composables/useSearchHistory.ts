import { ref, watch } from 'vue'

const STORAGE_KEY = 'nav_search_history'
const MAX_ITEMS = 10

function load(): string[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

const searchHistory = ref<string[]>(load())

watch(searchHistory, (val) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
}, { deep: true })

export function useSearchHistory() {
  const addSearch = (query: string) => {
    const q = query.trim()
    if (!q) return
    searchHistory.value = searchHistory.value.filter(s => s !== q)
    searchHistory.value.unshift(q)
    if (searchHistory.value.length > MAX_ITEMS) {
      searchHistory.value = searchHistory.value.slice(0, MAX_ITEMS)
    }
  }

  const removeSearch = (query: string) => {
    searchHistory.value = searchHistory.value.filter(s => s !== query)
  }

  const clearSearchHistory = () => {
    searchHistory.value = []
  }

  return { searchHistory, addSearch, removeSearch, clearSearchHistory }
}
