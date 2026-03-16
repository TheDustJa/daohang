import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { fetchNavigation, type NavigationResponse, type Site } from '../api/sites'

export const useNavigationStore = defineStore('navigation', () => {
  const navigation = ref<NavigationResponse>({
    categories: [],
    sites: []
  })
  const isLoading = ref(false)
  const activeLevel1 = ref('')
  const activeLevel2 = ref('')
  const searchQuery = ref('')
  const activeTag = ref('')
  const isScrollingByClick = ref(false)
  const recommendedOnly = ref(false)
  const sortBy = ref<'default' | 'click' | 'latest' | 'name'>('default')

  const sites = computed(() => navigation.value.sites)
  const level1Categories = computed(() => navigation.value.categories)

  const filteredSites = computed(() => {
    let result: Site[]

    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      result = sites.value.filter((site) =>
        site.name.toLowerCase().includes(q) ||
        site.description.toLowerCase().includes(q) ||
        site.tags.some((tag) => tag.toLowerCase().includes(q))
      )
    } else {
      result = sites.value.filter((site) => site.level1 === activeLevel1.value)
    }

    if (recommendedOnly.value) {
      result = result.filter((site) => site.isRecommended)
    }
    if (activeTag.value) {
      const tag = activeTag.value.toLowerCase()
      result = result.filter((site) => site.tags?.some((t) => t.toLowerCase() === tag))
    }

    const sb = sortBy.value
    if (sb === 'click') {
      result = [...result].sort((a, b) => (b.clickCount ?? 0) - (a.clickCount ?? 0))
    } else if (sb === 'latest') {
      result = [...result].sort((a, b) => ((b.updatedAt || b.createdAt || '') > (a.updatedAt || a.createdAt || '') ? 1 : -1))
    } else if (sb === 'name') {
      result = [...result].sort((a, b) => (a.name || '').localeCompare(b.name || ''))
    }

    if (sb === 'default') return [...result].sort((a, b) => {
      if ((a.sortOrder ?? 0) !== (b.sortOrder ?? 0)) {
        return (b.sortOrder ?? 0) - (a.sortOrder ?? 0)
      }
      const aRec = a.isRecommended ? 1 : 0
      const bRec = b.isRecommended ? 1 : 0
      if (aRec !== bRec) {
        return bRec - aRec
      }
      return b.id - a.id
    })
    return result
  })

  const sitesGroupedByLevel2 = computed(() => {
    const grouped: Record<string, Site[]> = {}

    filteredSites.value.forEach((site) => {
      const level2 = site.level2?.trim() || site.level1?.trim() || '其他内容'
      if (!grouped[level2]) {
        grouped[level2] = []
      }
      grouped[level2].push(site)
    })

    if (searchQuery.value) {
      return grouped
    }

    const ordered: Record<string, Site[]> = {}
    level2Categories.value.forEach((level2) => {
      if (grouped[level2]) {
        ordered[level2] = grouped[level2]
      }
    })
    return ordered
  })

  const level2Categories = computed(() => {
    if (searchQuery.value) {
      return Object.keys(sitesGroupedByLevel2.value)
    }
    const currentLevel1 = level1Categories.value.find((item) => item.name === activeLevel1.value)
    return currentLevel1?.children.map((child) => child.name) || []
  })

  const syncActiveCategories = () => {
    const firstLevel1 = level1Categories.value[0]?.name || ''
    if (!activeLevel1.value || !level1Categories.value.some((item) => item.name === activeLevel1.value)) {
      activeLevel1.value = firstLevel1
    }

    if (!level2Categories.value.includes(activeLevel2.value)) {
      activeLevel2.value = level2Categories.value[0] || ''
    }
  }

  const loadSites = async () => {
    isLoading.value = true
    try {
      navigation.value = await fetchNavigation()
      syncActiveCategories()
    } finally {
      isLoading.value = false
    }
  }

  watch(level1Categories, () => {
    syncActiveCategories()
  }, { deep: true })

  watch(activeLevel1, () => {
    if (!searchQuery.value) {
      activeLevel2.value = level2Categories.value[0] || ''
    }
    activeTag.value = ''
  })
  watch(searchQuery, () => { activeTag.value = '' })

  return {
    navigation,
    sites,
    level1Categories,
    isLoading,
    activeLevel1,
    activeLevel2,
    searchQuery,
    loadSites,
    filteredSites,
    level2Categories,
    sitesGroupedByLevel2,
    isScrollingByClick,
    recommendedOnly,
    sortBy,
    activeTag
  }
})
