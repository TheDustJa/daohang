import { ref, watch } from 'vue'
import type { Site } from '../api/sites'

const STORAGE_KEY = 'nav_favorites'
const TS_KEY = 'nav_favorites_ts'

function loadIds(): number[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

function loadTs(): Record<number, number> {
  try {
    const raw = localStorage.getItem(TS_KEY)
    if (!raw) return {}
    const obj = JSON.parse(raw)
    const out: Record<number, number> = {}
    for (const k of Object.keys(obj)) out[Number(k)] = obj[k]
    return out
  } catch {
    return {}
  }
}

const favoriteIds = ref<number[]>(loadIds())
const favoriteTs = ref<Record<number, number>>(loadTs())

watch(favoriteIds, (val) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
}, { deep: true })

watch(favoriteTs, (val) => {
  localStorage.setItem(TS_KEY, JSON.stringify(val))
}, { deep: true })

export function useFavorites() {
  const isFavorite = (id: number) => favoriteIds.value.includes(id)

  const toggleFavorite = (id: number) => {
    const idx = favoriteIds.value.indexOf(id)
    if (idx === -1) {
      favoriteIds.value.push(id)
      favoriteTs.value = { ...favoriteTs.value, [id]: Date.now() }
    } else {
      favoriteIds.value.splice(idx, 1)
      const next = { ...favoriteTs.value }
      delete next[id]
      favoriteTs.value = next
    }
  }

  const getFavoriteSites = (allSites: Site[], sortByTime = true): Site[] => {
    const ids = favoriteIds.value
    const sites = allSites.filter(s => ids.includes(s.id))
    if (sortByTime && Object.keys(favoriteTs.value).length > 0) {
      return [...sites].sort((a, b) => (favoriteTs.value[b.id] ?? 0) - (favoriteTs.value[a.id] ?? 0))
    }
    return sites
  }

  const favoriteCount = () => favoriteIds.value.length

  const addFavorites = (ids: number[]) => {
    const now = Date.now()
    const set = new Set(favoriteIds.value)
    const ts = { ...favoriteTs.value }
    ids.forEach(id => {
      set.add(id)
      ts[id] = now
    })
    favoriteIds.value = Array.from(set)
    favoriteTs.value = ts
  }

  return { favoriteIds, isFavorite, toggleFavorite, getFavoriteSites, favoriteCount, addFavorites }
}
