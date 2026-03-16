<script setup lang="ts">
import { useNavigationStore } from '../store/navigation'
import ToolCard from './ToolCard.vue'
import FooterLinks from './FooterLinks.vue'
import { ArrowUp, Sparkles, TrendingUp, Shuffle, Tag, PanelLeft } from 'lucide-vue-next'
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { fetchRecentSites, fetchPopularSites, fetchRandomSites, fetchAllTags, type Site } from '../api/sites'
import { useRouter } from 'vue-router'
import { LayoutGrid, List, Rows3 } from 'lucide-vue-next'
import { useLayoutMode } from '../composables/useLayoutMode'
import { useCardFontSize } from '../composables/useCardFontSize'
import { useScrollProgress } from '../composables/useScrollProgress'
import { useFavorites } from '../composables/useFavorites'
import { Toast } from '../utils/toast'

withDefaults(defineProps<{ sidebarCollapsed?: boolean }>(), { sidebarCollapsed: false })
const emit = defineEmits<{ (e: 'toggle-sidebar'): void }>()

const store = useNavigationStore()
const router = useRouter()
const recentSites = ref<Site[]>([])
const popularSites = ref<Site[]>([])
const randomSites = ref<Site[]>([])
const hotTags = ref<{ name: string; count: number }[]>([])

const loadRecent = async () => {
  try {
    recentSites.value = await fetchRecentSites(8)
  } catch { /* ignore */ }
}

const loadPopular = async () => {
  try {
    popularSites.value = await fetchPopularSites(6)
  } catch { /* ignore */ }
}

const loadRandom = async () => {
  try {
    randomSites.value = await fetchRandomSites(6)
  } catch { /* ignore */ }
}

const loadHotTags = async () => {
  try {
    const tags = await fetchAllTags()
    hotTags.value = tags.slice(0, 8)
  } catch { /* ignore */ }
}

const searchByTag = (tag: string) => {
  store.$patch({ searchQuery: tag })
  router.push('/')
}

const exportCurrentResults = () => {
  const sites = store.filteredSites
  if (sites.length === 0) return
  const lines = ['| 名称 | 链接 | 描述 |', '|------|------|------|']
  sites.forEach((s) => {
    const name = (s.name || '').replace(/\|/g, '｜')
    const url = (s.url || '').replace(/\|/g, '｜')
    const desc = (s.description || '').slice(0, 80).replace(/\|/g, '｜').replace(/\n/g, ' ')
    lines.push(`| ${name} | ${url} | ${desc} |`)
  })
  const blob = new Blob([lines.join('\n')], { type: 'text/markdown' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'ai-nav-export.md'
  a.click()
  URL.revokeObjectURL(a.href)
}

const exportCurrentAsCsv = () => {
  const sites = store.filteredSites
  if (sites.length === 0) return
  const header = '名称,链接,描述,标签'
  const rows = sites.map((s) => {
    const name = (s.name || '').replace(/"/g, '""')
    const url = (s.url || '').replace(/"/g, '""')
    const desc = (s.description || '').replace(/"/g, '""').replace(/\n/g, ' ')
    const tags = (s.tags || []).join(';')
    return `"${name}","${url}","${desc}","${tags}"`
  })
  const blob = new Blob([('\ufeff' + header + '\n' + rows.join('\n'))], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'ai-nav-export.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}

const exportCurrentAsJson = () => {
  const sites = store.filteredSites
  if (sites.length === 0) return
  const data = sites.map((s) => ({ name: s.name, url: s.url, description: s.description, tags: s.tags, type: s.type }))
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'ai-nav-export.json'
  a.click()
  URL.revokeObjectURL(a.href)
}

const exportCurrentAsHtml = () => {
  const sites = store.filteredSites
  if (sites.length === 0) return
  const items = sites.map((s) => `<li><a href="${(s.url || '').replace(/"/g, '&quot;')}">${(s.name || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</a></li>`).join('\n')
  const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI 导航导出</title></head><body><ul>\n${items}\n</ul></body></html>`
  const blob = new Blob([html], { type: 'text/html' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'ai-nav-export.html'
  a.click()
  URL.revokeObjectURL(a.href)
}

const copyAllUrls = async () => {
  const sites = store.filteredSites.filter((s) => s.url)
  if (sites.length === 0) return
  const text = sites.map((s) => s.url).join('\n')
  try {
    await navigator.clipboard.writeText(text)
    Toast.success(`已复制 ${sites.length} 个链接`)
  } catch {
    Toast.error('复制失败')
  }
}

const { addFavorites } = useFavorites()
const batchFavoriteCurrent = () => {
  const sites = store.filteredSites
  if (sites.length === 0) return
  addFavorites(sites.map((s) => s.id))
  Toast.success(`已收藏当前 ${sites.length} 个站点`)
}

const goToSite = (site: Site) => {
  router.push(`/content/${site.type || 'site'}/${site.id}`)
}

const goRandomFromEmpty = async () => {
  await loadRandom()
  if (randomSites.value.length > 0) goToSite(randomSites.value[0])
}

const { layoutMode, setMode } = useLayoutMode()
const { cardFontSize } = useCardFontSize()
const setCardFontSize = (s: 'sm' | 'md' | 'lg') => { cardFontSize.value = s }
const { reportProgress } = useScrollProgress()

const gridClass = () => {
  if (layoutMode.value === 'list') return 'grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4'
  if (layoutMode.value === 'compact') return 'grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-2 md:gap-3'
  return 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3 sm:gap-5 md:gap-6'
}

const contentRef = ref<HTMLElement | null>(null)
const showBackToTop = ref(false)

const footerStats = computed(() => ({
  totalSites: store.sites.filter((s) => s.type !== 'article').length,
  totalArticles: store.sites.filter((s) => s.type === 'article').length,
  totalCategories: store.level1Categories.length,
  totalTags: new Set(store.sites.flatMap((s) => s.tags)).size
}))

let isScrolling = false
let scrollEndTimeout: ReturnType<typeof setTimeout> | null = null

const checkActiveSection = () => {
  if (store.searchQuery || store.isScrollingByClick) return
  if (!contentRef.value) return
  
  const container = contentRef.value
  const sections = Array.from(container.querySelectorAll('.scroll-section')) as HTMLElement[]
  if (sections.length === 0) return

  const containerTop = container.getBoundingClientRect().top
  const isAtBottom = Math.abs(container.scrollHeight - container.scrollTop - container.clientHeight) < 10

  let activeSection = sections[0]

  if (isAtBottom) {
    activeSection = sections[sections.length - 1]
  } else {
    for (const section of sections) {
      const rect = section.getBoundingClientRect()
      // Use a comfortable offset to trigger the active state relative to the standard header height
      if (rect.top - containerTop <= 150) {
        activeSection = section
      } else {
        break
      }
    }
  }

  const level2 = activeSection.getAttribute('data-level2')
  if (level2 && store.activeLevel2 !== level2) {
    store.activeLevel2 = level2
  }
}

const onScroll = () => {
  if (contentRef.value) {
    const el = contentRef.value
    showBackToTop.value = el.scrollTop > 300
    const h = el.scrollHeight - el.clientHeight
    reportProgress(h > 0 ? Math.min((el.scrollTop / h) * 100, 100) : 0)
  }

  // If scrolling was triggered by a click, debounce until scrolling stops
  if (store.isScrollingByClick) {
    if (scrollEndTimeout) clearTimeout(scrollEndTimeout)
    scrollEndTimeout = setTimeout(() => {
      store.isScrollingByClick = false
      checkActiveSection()
    }, 150)
    return
  }

  if (!isScrolling) {
    window.requestAnimationFrame(() => {
      checkActiveSection()
      isScrolling = false
    })
    isScrolling = true
  }
}

const scrollToTop = () => {
  if (contentRef.value) {
    contentRef.value.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Re-run setup when data changes
watch(() => store.sitesGroupedByLevel2, async () => {
  await nextTick()
  checkActiveSection()
}, { deep: true })

onMounted(() => {
  checkActiveSection()
  loadRecent()
  loadPopular()
  loadRandom()
  loadHotTags()
})
</script>

<template>
  <main ref="contentRef" data-nav-scroll class="p-4 md:p-8 pb-32 relative" @scroll="onScroll">
    <button v-if="sidebarCollapsed" @click="emit('toggle-sidebar')" class="absolute left-2 top-4 z-10 p-2 border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted md:left-4" title="展开侧边栏">
      <PanelLeft class="w-4 h-4" :stroke-width="2.5" />
    </button>
    <!-- Hot Tags 大家都在搜 -->
    <div v-if="hotTags.length > 0 && !store.searchQuery" class="mb-4 flex items-center gap-2 flex-wrap">
      <Tag class="w-3.5 h-3.5 opacity-50" :stroke-width="2.5" />
      <span class="text-[10px] font-black uppercase tracking-widest opacity-50">大家都在搜：</span>
      <button
        v-for="tag in hotTags"
        :key="tag.name"
        @click="searchByTag(tag.name)"
        class="px-2 py-0.5 text-[10px] font-bold border border-black dark:border-term-muted hover:bg-neo-accent hover:text-white dark:hover:bg-term-primary dark:hover:text-black transition-colors"
      >
        {{ tag.name }}
      </button>
    </div>

    <!-- Recent Sites Banner -->
    <div v-if="recentSites.length > 0 && !store.searchQuery" class="mb-6 md:mb-8">
      <div class="flex items-center gap-2 mb-3">
        <Sparkles class="w-4 h-4 md:w-5 md:h-5 text-neo-accent dark:text-term-secondary" :stroke-width="2.5" />
        <h3 class="text-xs md:text-sm font-black uppercase tracking-widest opacity-70 dark:text-term-secondary">最新收录</h3>
      </div>
      <div class="flex gap-3 overflow-x-auto no-scrollbar pb-2">
        <button
          v-for="site in recentSites"
          :key="'recent-' + site.id"
          @click="goToSite(site)"
          class="shrink-0 flex items-center gap-2 px-3 py-2 bg-white dark:bg-black border-2 border-black dark:border-term-muted hover:-translate-y-0.5 hover:shadow-neo-sm dark:hover:shadow-term-glow transition-all cursor-pointer"
        >
          <span class="w-6 h-6 bg-neo-secondary dark:bg-term-bg border border-black dark:border-term-primary flex items-center justify-center text-[10px] font-black -rotate-2 shrink-0">
            {{ site.name[0] }}
          </span>
          <span class="text-xs font-bold whitespace-nowrap max-w-[120px] truncate">{{ site.name }}</span>
        </button>
      </div>
    </div>

    <!-- Popular & Random -->
    <div v-if="(popularSites.length > 0 || randomSites.length > 0) && !store.searchQuery" class="mb-6 md:mb-8 flex flex-col sm:flex-row gap-6">
      <div v-if="popularSites.length > 0" class="flex-1">
        <div class="flex items-center gap-2 mb-3">
          <TrendingUp class="w-4 h-4 text-neo-accent dark:text-term-secondary" :stroke-width="2.5" />
          <h3 class="text-xs md:text-sm font-black uppercase tracking-widest opacity-70 dark:text-term-secondary">今日热门</h3>
        </div>
        <div class="flex gap-3 overflow-x-auto no-scrollbar pb-2">
          <button
            v-for="site in popularSites"
            :key="'pop-' + site.id"
            @click="goToSite(site)"
            class="shrink-0 flex items-center gap-2 px-3 py-2 bg-white dark:bg-black border-2 border-black dark:border-term-muted hover:-translate-y-0.5 transition-all cursor-pointer"
          >
            <span class="w-6 h-6 bg-neo-accent/20 dark:bg-term-primary/20 border border-black dark:border-term-primary flex items-center justify-center text-[10px] font-black shrink-0">{{ site.name[0] }}</span>
            <span class="text-xs font-bold whitespace-nowrap max-w-[100px] truncate">{{ site.name }}</span>
          </button>
        </div>
      </div>
      <div v-if="randomSites.length > 0" class="flex-1">
        <div class="flex items-center justify-between gap-2 mb-3">
          <div class="flex items-center gap-2">
            <Shuffle class="w-4 h-4 text-neo-accent dark:text-term-secondary" :stroke-width="2.5" />
            <h3 class="text-xs md:text-sm font-black uppercase tracking-widest opacity-70 dark:text-term-secondary">随机探索</h3>
          </div>
          <button @click="loadRandom" class="text-[10px] font-bold uppercase border border-black dark:border-term-muted px-2 py-0.5 hover:bg-neo-secondary dark:hover:bg-term-muted">换一批</button>
        </div>
        <div class="flex gap-3 overflow-x-auto no-scrollbar pb-2">
          <button
            v-for="site in randomSites"
            :key="'rand-' + site.id"
            @click="goToSite(site)"
            class="shrink-0 flex items-center gap-2 px-3 py-2 bg-white dark:bg-black border-2 border-black dark:border-term-muted hover:-translate-y-0.5 transition-all cursor-pointer"
          >
            <span class="w-6 h-6 bg-neo-secondary dark:bg-term-bg border border-black dark:border-term-primary flex items-center justify-center text-[10px] font-black shrink-0">{{ site.name[0] }}</span>
            <span class="text-xs font-bold whitespace-nowrap max-w-[100px] truncate">{{ site.name }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="store.isLoading" class="space-y-8">
      <div v-for="i in 2" :key="i">
        <div class="mb-4 md:mb-6 flex items-end justify-between gap-2 animate-pulse">
          <div class="h-6 md:h-10 w-40 bg-black/10 dark:bg-term-muted/30 border-2 border-black/5 dark:border-term-muted"></div>
          <div class="h-4 w-20 bg-black/5 dark:bg-term-muted/20"></div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3 sm:gap-5 md:gap-6">
          <div v-for="j in 6" :key="j" class="nav-card p-3 md:p-4 animate-pulse" :style="{ animationDelay: `${j * 0.08}s` }">
            <div class="flex items-start justify-between gap-2 mb-3">
              <div class="w-8 h-8 md:w-12 md:h-12 bg-black/10 dark:bg-term-muted/30 border-2 border-black/5 dark:border-term-muted -rotate-2"></div>
              <div class="w-14 h-6 bg-black/5 dark:bg-term-muted/20"></div>
            </div>
            <div class="space-y-2">
              <div class="h-4 md:h-5 w-3/4 bg-black/10 dark:bg-term-muted/30"></div>
              <div class="h-3 w-full bg-black/5 dark:bg-term-muted/15"></div>
              <div class="h-3 w-2/3 bg-black/5 dark:bg-term-muted/15"></div>
            </div>
            <div class="flex gap-2 mt-3">
              <div class="h-5 w-12 bg-black/5 dark:bg-term-muted/20 border border-black/5 dark:border-term-muted"></div>
              <div class="h-5 w-16 bg-black/5 dark:bg-term-muted/20 border border-black/5 dark:border-term-muted"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="Object.keys(store.sitesGroupedByLevel2).length === 0" class="flex flex-col items-center justify-center h-full pt-16 md:pt-20">
      <div class="text-center max-w-md">
        <h2 class="text-2xl md:text-4xl font-black uppercase tracking-tighter opacity-80">未找到结果</h2>
        <p class="font-bold mt-2 text-sm md:text-base opacity-60">试试这些热门搜索？</p>
        <div class="flex flex-wrap gap-2 justify-center mt-4" v-if="hotTags.length > 0">
          <button
            v-for="tag in hotTags.slice(0, 6)"
            :key="tag.name"
            @click="searchByTag(tag.name)"
            class="px-3 py-1.5 text-xs font-bold border-2 border-black dark:border-term-muted hover:bg-neo-accent hover:text-white dark:hover:bg-term-primary dark:hover:text-black transition-colors"
          >
            {{ tag.name }}
          </button>
        </div>
        <button @click="goRandomFromEmpty" class="mt-4 px-4 py-2 text-sm font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors flex items-center gap-1 mx-auto">
          <Shuffle class="w-4 h-4 inline mr-1" :stroke-width="2.5" />
          随机探索一个
        </button>
        <p class="font-bold mt-6 text-xs opacity-40">或清除搜索、关闭「只看推荐」试试</p>
      </div>
    </div>

    <!-- Grouped Sections -->
    <div v-else class="space-y-6 md:space-y-8">
      <!-- Layout Toggle & 只看推荐 & 导出 -->
      <div class="flex items-center justify-between gap-2 -mb-4 md:-mb-6 flex-wrap">
        <div class="flex gap-2">
          <button
            @click="store.recommendedOnly = !store.recommendedOnly"
          class="px-2 py-1 text-[10px] font-bold uppercase border-2 transition-colors"
          :class="store.recommendedOnly ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-black dark:border-term-primary' : 'border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100'"
          title="只看推荐"
        >
          只看推荐
        </button>
          <button @click="exportCurrentResults" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100">导出 MD</button>
          <button @click="exportCurrentAsCsv" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100">导出 CSV</button>
          <button @click="exportCurrentAsJson" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100">导出 JSON</button>
          <button @click="exportCurrentAsHtml" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100">导出 HTML</button>
          <button @click="copyAllUrls" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100">复制全部链接</button>
          <button @click="batchFavoriteCurrent" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100">收藏本页</button>
          <button v-if="store.activeTag" @click="store.activeTag = ''" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-neo-accent dark:border-term-primary bg-neo-accent/20 dark:bg-term-primary/20">取消标签筛选</button>
          <select v-model="store.sortBy" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black/20 dark:border-term-muted/50 bg-white dark:bg-black dark:text-term-primary">
            <option value="default">默认排序</option>
            <option value="click">按热度</option>
            <option value="latest">按更新</option>
            <option value="name">按名称</option>
          </select>
        </div>
        <div class="flex gap-1 items-center">
          <span class="text-[9px] font-bold uppercase opacity-50 hidden sm:inline">字号</span>
          <button v-for="s in (['sm', 'md', 'lg'] as const)" :key="s" @click="setCardFontSize(s)" class="px-1.5 py-0.5 text-[10px] font-bold border-2 transition-colors" :class="cardFontSize === s ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-black dark:border-term-primary' : 'border-black/20 dark:border-term-muted/50 opacity-40 hover:opacity-100'">{{ { sm: '小', md: '中', lg: '大' }[s] }}</button>
          <button
            v-for="mode in (['grid', 'list', 'compact'] as const)"
            :key="mode"
            @click="setMode(mode)"
            class="p-1.5 border-2 transition-colors"
            :class="layoutMode === mode ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-black dark:border-term-primary' : 'border-black/20 dark:border-term-muted/50 opacity-40 hover:opacity-100'"
            :title="mode === 'grid' ? '卡片视图' : mode === 'list' ? '列表视图' : '紧凑视图'"
          >
            <component :is="mode === 'grid' ? LayoutGrid : mode === 'list' ? List : Rows3" class="w-3.5 h-3.5" :stroke-width="2.5" />
          </button>
        </div>
      </div>

      <section 
        v-for="(sites, level2) in store.sitesGroupedByLevel2" 
        :key="level2"
        class="scroll-section"
        :id="`section-${level2}`"
        :data-level2="level2"
      >
        <div class="mb-3 md:mb-6 border-b-[3px] md:border-b-[6px] border-black dark:border-term-muted pb-1 md:pb-4 flex items-end justify-between gap-2">
          <h2 class="text-[10px] md:text-4xl font-black uppercase tracking-tighter" style="-webkit-text-stroke: 1px currentColor; color: transparent;">
            {{ level2 }}
          </h2>
          <div class="flex items-center gap-2">
            <span class="font-bold uppercase tracking-widest opacity-50 dark:text-term-secondary text-[9px] sm:text-[10px] md:text-base">
              [{{ sites.length }}]
            </span>
          </div>
        </div>

        <div :class="gridClass()">
          <ToolCard v-for="(site, idx) in sites" :key="site.id" :site="site" :index="idx" :layout="layoutMode" :highlight="store.searchQuery" />
        </div>
      </section>
    </div>

    <!-- Global Footer -->
    <FooterLinks class="mt-20 md:mt-24 mb-6 md:mb-0" :stats="footerStats" />

    <!-- 回到顶部按钮 -->
    <transition 
      enter-active-class="transition duration-300 ease-out" 
      enter-from-class="transform translate-y-8 opacity-0" 
      enter-to-class="transform translate-y-0 opacity-100" 
      leave-active-class="transition duration-200 ease-in" 
      leave-from-class="transform translate-y-0 opacity-100" 
      leave-to-class="transform translate-y-8 opacity-0"
    >
      <button 
        v-if="showBackToTop" 
        @click="scrollToTop" 
        class="fixed bottom-[4.5rem] md:bottom-20 left-4 z-50 p-2.5 md:p-3 bg-white dark:bg-black border-4 border-black dark:border-[#33ff00] text-black dark:text-[#33ff00] shadow-neo-sm transition-all hover:scale-105 active:scale-95 flex items-center justify-center"
        title="回到顶部"
      >
        <ArrowUp class="w-5 h-5" :stroke-width="3" />
      </button>
    </transition>
  </main>
</template>
