import { ref, watch } from 'vue'

export interface HistoryItem {
  id: number
  name: string
  type: 'site' | 'article'
  description: string
  url: string
  visitedAt: number
}

const STORAGE_KEY = 'nav_history'
const MAX_ITEMS = 50

function load(): HistoryItem[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

const historyList = ref<HistoryItem[]>(load())

watch(historyList, (val) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
}, { deep: true })

export function useHistory() {
  const addToHistory = (item: Omit<HistoryItem, 'visitedAt'>) => {
    historyList.value = historyList.value.filter(h => h.id !== item.id)
    historyList.value.unshift({ ...item, visitedAt: Date.now() })
    if (historyList.value.length > MAX_ITEMS) {
      historyList.value = historyList.value.slice(0, MAX_ITEMS)
    }
  }

  const clearHistory = () => {
    historyList.value = []
  }

  const removeFromHistory = (id: number) => {
    historyList.value = historyList.value.filter(h => h.id !== id)
  }

  return { historyList, addToHistory, clearHistory, removeFromHistory }
}
