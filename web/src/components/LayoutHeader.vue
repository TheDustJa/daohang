<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Search, User, Compass, Newspaper, Cpu, BookOpen, Heart, Clock, Shuffle } from 'lucide-vue-next'
import { useNavigationStore } from '../store/navigation'
import { useRouter } from 'vue-router'
import { fetchRandomSites, fetchSearchSuggest } from '../api/sites'
import { useFavorites } from '../composables/useFavorites'
import { useSearchHistory } from '../composables/useSearchHistory'
import { useHistory } from '../composables/useHistory'
import { useRecentCategories } from '../composables/useRecentCategories'
import CheckinButton from './CheckinButton.vue'

const store = useNavigationStore()
const router = useRouter()

const iconMap: Record<string, typeof Compass> = {
  'AI 工具': Compass,
  'AI工具': Compass,
  'AI 资讯': Newspaper,
  'AI资讯': Newspaper,
  '提示词': Cpu,
  '我的文章': BookOpen
}

const level1Items = computed(() =>
  store.level1Categories.map((item) => ({
    name: item.name,
    icon: iconMap[item.name] || Compass
  }))
)

const { addRecent } = useRecentCategories()

const handleLevel1Click = (name: string) => {
  store.$patch({ activeLevel1: name, searchQuery: '' })
  addRecent(name)
  router.push('/')
}

const resetHomeCategory = () => {
  store.activeLevel1 = store.level1Categories[0]?.name || ''
  store.searchQuery = ''
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null
const localSearch = ref(store.searchQuery)
const showSearchDropdown = ref(false)
const { favoriteCount } = useFavorites()
const { searchHistory, addSearch, removeSearch, clearSearchHistory } = useSearchHistory()
const { historyList } = useHistory()
const historyCount = computed(() => historyList.value.length)

const handleSearch = (e: Event) => {
  const target = e.target as HTMLInputElement
  localSearch.value = target.value
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    store.$patch({ searchQuery: localSearch.value })
    if (localSearch.value.trim()) {
      addSearch(localSearch.value.trim())
    }
  }, 250)
}

const applyHistorySearch = (query: string) => {
  localSearch.value = query
  store.$patch({ searchQuery: query })
  showSearchDropdown.value = false
  router.push('/')
}

const suggestSites = ref<{ id: number; name: string; type: string }[]>([])
const suggestTags = ref<string[]>([])
let suggestTimer: ReturnType<typeof setTimeout> | null = null

const loadSuggest = async () => {
  const q = localSearch.value.trim()
  if (q.length < 1) {
    suggestSites.value = []
    suggestTags.value = []
    return
  }
  try {
    const r = await fetchSearchSuggest(q, 6)
    suggestSites.value = r.sites.map((s) => ({ id: s.id, name: s.name, type: s.type || 'site' }))
    suggestTags.value = r.tags || []
  } catch {
    suggestSites.value = []
    suggestTags.value = []
  }
}

const handleSearchFocus = () => {
  if (searchHistory.value.length > 0 || localSearch.value.trim()) {
    showSearchDropdown.value = true
    loadSuggest()
  }
}

const handleSearchBlur = () => {
  setTimeout(() => { showSearchDropdown.value = false }, 200)
}

watch(localSearch, () => {
  if (suggestTimer) clearTimeout(suggestTimer)
  suggestTimer = setTimeout(() => {
    loadSuggest()
    if (localSearch.value.trim()) showSearchDropdown.value = true
  }, 300)
})

const goRandom = async () => {
  try {
    const sites = await fetchRandomSites(1)
    if (sites.length > 0) {
      const s = sites[0]
      router.push(`/content/${s.type || 'site'}/${s.id}`)
    }
  } catch { /* ignore */ }
}
</script>

<template>
  <header class="min-h-[4rem] flex flex-col xl:flex-row xl:items-center justify-between px-4 md:px-6 bg-white dark:bg-black border-b-4 border-black dark:border-term-muted shadow-neo-sm py-2 md:py-3 gap-3 xl:gap-4">
    <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 w-full xl:w-auto shrink-0">
      <div class="flex items-center justify-between w-full md:w-auto shrink-0">
        <router-link to="/" @click="resetHomeCategory" class="flex items-center gap-1.5 md:gap-2 group cursor-pointer shrink-0">
          <div class="w-7 h-7 md:w-10 md:h-10 bg-neo-accent dark:bg-term-primary border-2 md:border-4 border-black dark:border-black flex items-center justify-center -rotate-2 group-hover:rotate-0 transition-transform">
            <span class="font-black text-[10px] md:text-sm text-white dark:text-black">导航</span>
          </div>
          <h1 class="text-lg md:text-2xl font-black uppercase tracking-tighter dark:text-term-primary">AI 导航</h1>
        </router-link>

        <div class="flex items-center gap-1.5 shrink-0 md:hidden">
          <router-link to="/login" class="w-8 h-8 flex items-center justify-center border-2 border-black dark:border-term-muted bg-white dark:bg-black hover:bg-neo-muted dark:hover:bg-term-muted transition-colors shadow-[2px_2px_0px_0px_#000] dark:shadow-none active:translate-y-0.5 active:translate-x-0.5 active:shadow-none rounded-sm">
            <User class="w-3.5 h-3.5 dark:text-term-primary" :stroke-width="3" />
          </router-link>
        </div>
      </div>

      <nav class="flex items-center gap-1.5 md:gap-4 overflow-x-auto no-scrollbar md:pr-4 pb-1 md:pb-0 w-full md:w-max whitespace-nowrap">
        <button
          v-for="item in level1Items"
          :key="item.name"
          @click="handleLevel1Click(item.name)"
          :class="[
            'flex items-center gap-1 px-2 py-1 md:px-4 md:py-2 text-[11px] md:text-base font-bold uppercase transition-transform shrink-0',
            store.activeLevel1 === item.name
              ? 'bg-neo-secondary dark:bg-term-primary dark:text-black border-2 md:border-4 border-black dark:border-term-primary shadow-[2px_2px_0px_0px_#000] md:shadow-[4px_4px_0px_0px_#000] -translate-y-0.5 md:-translate-y-1'
              : 'border-2 md:border-[4px] border-transparent hover:border-black dark:hover:border-term-primary opacity-70 hover:opacity-100'
          ]"
        >
          <component :is="item.icon" class="w-3.5 h-3.5 md:w-5 md:h-5" :stroke-width="store.activeLevel1 === item.name ? 3 : 2" />
          {{ item.name }}
        </button>
      </nav>
    </div>

    <div class="hidden md:flex flex-row items-center justify-between xl:justify-end gap-4 w-full xl:w-auto shrink-0 mt-2 xl:mt-0">
      <div class="relative w-full max-w-sm xl:max-w-xs group shadow-neo-sm xl:shadow-none">
        <input
          type="text"
          placeholder="搜索 AI 工具、文章..."
          :value="localSearch"
          @input="handleSearch"
          @focus="handleSearchFocus"
          @blur="handleSearchBlur"
          class="w-full h-10 md:h-10 pl-10 pr-4 text-sm md:text-base font-bold uppercase bg-white dark:bg-black border-[3px] md:border-4 border-black dark:border-term-muted focus:bg-neo-secondary dark:focus:border-term-primary dark:focus:ring-1 dark:focus:ring-term-primary focus:shadow-neo-sm focus:outline-none transition-colors"
        />
        <Search class="absolute left-3 top-2.5 w-5 h-5 text-black dark:text-term-muted group-focus-within:text-black dark:group-focus-within:text-term-primary" :stroke-width="3" />
        <!-- Search Suggest & History Dropdown -->
        <div v-if="showSearchDropdown && (searchHistory.length > 0 || suggestSites.length > 0 || suggestTags.length > 0)" class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-black border-[3px] border-black dark:border-term-muted shadow-neo-sm dark:shadow-term-glow z-50 max-h-64 overflow-y-auto">
          <template v-if="localSearch.trim() && (suggestSites.length > 0 || suggestTags.length > 0)">
            <div v-if="suggestTags.length > 0" class="px-3 py-2 border-b-2 border-black/10 dark:border-term-muted/50">
              <span class="text-[10px] font-black uppercase tracking-widest opacity-50">相关标签</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <button v-for="tag in suggestTags" :key="tag" @mousedown.prevent="applyHistorySearch(tag)" class="px-2 py-0.5 text-[10px] font-bold border border-black dark:border-term-muted hover:bg-neo-accent dark:hover:bg-term-primary hover:text-white dark:hover:text-black">{{ tag }}</button>
              </div>
            </div>
            <div v-if="suggestSites.length > 0">
              <span class="block px-3 py-1 text-[10px] font-black uppercase opacity-50">相关工具</span>
              <button v-for="s in suggestSites" :key="s.id" @mousedown.prevent="router.push(`/content/${s.type}/${s.id}`)" class="w-full text-left px-3 py-2 text-sm font-bold hover:bg-neo-secondary dark:hover:bg-term-muted flex items-center gap-2">
                <span class="truncate">{{ s.name }}</span>
              </button>
            </div>
          </template>
          <template v-else>
            <div class="flex items-center justify-between px-3 py-2 border-b-2 border-black/10 dark:border-term-muted/50">
              <span class="text-[10px] font-black uppercase tracking-widest opacity-50">搜索历史</span>
              <button @mousedown.prevent="clearSearchHistory" class="text-[10px] font-bold uppercase opacity-50 hover:opacity-100">清空</button>
            </div>
            <button v-for="q in searchHistory" :key="q" @mousedown.prevent="applyHistorySearch(q)" class="w-full text-left px-3 py-2 text-sm font-bold hover:bg-neo-secondary dark:hover:bg-term-muted flex items-center justify-between group/item">
              <span class="truncate">{{ q }}</span>
              <span @mousedown.prevent.stop="removeSearch(q)" class="text-[10px] opacity-0 group-hover/item:opacity-50 hover:!opacity-100">✕</span>
            </button>
          </template>
        </div>
      </div>

      <div class="flex items-center gap-1.5 md:gap-3 shrink-0">
        <CheckinButton />
        <button
          @click="goRandom"
          class="w-10 h-10 flex items-center justify-center border-[3px] md:border-4 bg-white dark:bg-black hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors shadow-neo-sm active:translate-y-1 active:translate-x-1 active:shadow-none"
          title="随机发现"
        >
          <Shuffle class="w-4 h-4 dark:text-term-primary" :stroke-width="3" />
        </button>
        <router-link to="/favorites" class="relative w-10 h-10 flex items-center justify-center border-[3px] md:border-4 bg-white dark:bg-black hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors shadow-neo-sm active:translate-y-1 active:translate-x-1 active:shadow-none" title="我的收藏">
          <Heart class="w-4 h-4 dark:text-term-primary" :stroke-width="3" />
          <span v-if="favoriteCount() > 0" class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-neo-accent dark:bg-[#ff3333] text-white text-[9px] font-black flex items-center justify-center border border-black">
            {{ favoriteCount() > 9 ? '9+' : favoriteCount() }}
          </span>
        </router-link>
        <router-link to="/history" class="relative w-10 h-10 flex items-center justify-center border-[3px] md:border-4 bg-white dark:bg-black hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors shadow-neo-sm active:translate-y-1 active:translate-x-1 active:shadow-none" title="浏览历史">
          <Clock class="w-4 h-4 dark:text-term-primary" :stroke-width="3" />
          <span v-if="historyCount > 0" class="absolute -top-1 -right-1 min-w-[14px] h-[14px] px-0.5 flex items-center justify-center bg-neo-accent dark:bg-term-primary text-white text-[9px] font-black rounded-full border border-black">{{ historyCount > 99 ? '99+' : historyCount }}</span>
        </router-link>
        <router-link to="/friend-link" class="hidden lg:flex text-sm h-10 items-center font-bold hover:underline opacity-80 cursor-pointer">
          友链申请
        </router-link>
        <router-link to="/submit" class="flex btn-primary text-sm h-10 items-center">
          提交网站
        </router-link>
        <router-link to="/login" class="w-10 h-10 flex items-center justify-center border-[3px] md:border-4 bg-white dark:bg-black hover:bg-neo-muted dark:hover:bg-term-muted transition-colors shadow-neo-sm active:translate-y-1 active:translate-x-1 active:shadow-none">
          <User class="w-5 h-5 dark:text-term-primary" :stroke-width="3" />
        </router-link>
      </div>
    </div>
  </header>
</template>
