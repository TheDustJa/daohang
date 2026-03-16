<script setup lang="ts">
import { useNavigationStore } from '../store/navigation'
import { useRecentCategories } from '../composables/useRecentCategories'
import { useHistory } from '../composables/useHistory'
import { ChevronRight, PanelLeftClose, Clock } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { ref, watch, nextTick, computed } from 'vue'
import DailyQuote from './DailyQuote.vue'

const emit = defineEmits<{ (e: 'collapse'): void }>()
const router = useRouter()
const store = useNavigationStore()
const { recentCategories, addRecent } = useRecentCategories()
const { historyList } = useHistory()
const recentHistory = computed(() => historyList.value.slice(0, 5))
const navRef = ref<HTMLElement | null>(null)

const goToLevel1 = (name: string) => {
  store.$patch({ activeLevel1: name, searchQuery: '' })
  addRecent(name)
}

// Simple scroll-to function to tie sidebar with content area
const scrollToSection = (level2: string) => {
  store.activeLevel2 = level2
  store.isScrollingByClick = true // Disable auto-spy momentarily
  
  const el = document.getElementById(`section-${level2}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    // Fallback safety in case no scroll event fires
    setTimeout(() => {
      store.isScrollingByClick = false
    }, 1000)
  } else {
    store.isScrollingByClick = false
  }
}

// Watch activeLevel2 to ensure the active sidebar item is visible
watch(() => store.activeLevel2, async (newVal) => {
  if (!newVal) return
  await nextTick()
  if (!navRef.value) return
  
  // Use attribute selector to find the active button inside the nav
  const activeBtn = navRef.value.querySelector(`button[data-cat="${newVal}"]`) as HTMLElement | null
  if (activeBtn) {
    // Scroll the active button into view within the nav container
    activeBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }
})
</script>

<template>
  <aside class="bg-white dark:bg-black w-full md:h-full flex flex-col pt-4 md:pt-6 font-neo dark:font-term shadow-neo-sm md:shadow-neo-sm dark:shadow-none z-10 relative">
    <div class="px-4 md:px-6 mb-1 sm:mb-2 md:mb-4 shrink-0 flex items-center justify-between gap-2">
      <h2 class="text-[9px] sm:text-xs md:text-sm font-black text-black/50 dark:text-term-muted uppercase tracking-widest">{{ store.activeLevel1 }} | 分类</h2>
      <div v-if="recentCategories.length > 0" class="flex gap-1 flex-wrap justify-end">
        <button v-for="r in recentCategories.filter((x) => x !== store.activeLevel1)" :key="r" @click="goToLevel1(r)" class="px-1.5 py-0.5 text-[9px] font-bold border border-black/20 dark:border-term-muted/50 hover:bg-neo-secondary dark:hover:bg-term-muted">{{ r }}</button>
      </div>
      <button @click="emit('collapse')" class="hidden md:flex p-1 border-2 border-black/20 dark:border-term-muted/50 hover:bg-neo-secondary dark:hover:bg-term-muted" title="收起侧边栏">
        <PanelLeftClose class="w-4 h-4" :stroke-width="2.5" />
      </button>
    </div>
    
    <div v-if="recentHistory.length > 0" class="px-4 mb-3 pb-3 border-b-2 border-black/10 dark:border-term-muted/30 shrink-0">
      <div class="flex items-center gap-1 mb-2">
        <Clock class="w-3 h-3 opacity-50" :stroke-width="2.5" />
        <span class="text-[9px] font-black uppercase tracking-widest opacity-50">最近访问</span>
      </div>
      <div class="flex flex-col gap-1">
        <button
          v-for="h in recentHistory"
          :key="`${h.type}-${h.id}`"
          @click="router.push(`/content/${h.type}/${h.id}`)"
          class="text-left px-2 py-1 text-[10px] font-bold truncate hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors border-l-2 border-transparent hover:border-neo-accent dark:hover:border-term-primary"
        >
          {{ h.name }}
        </button>
      </div>
    </div>
    <nav ref="navRef" class="flex-1 overflow-x-auto md:overflow-y-auto overflow-y-hidden px-4 md:space-y-2 pb-2 md:pb-6 flex md:flex-col gap-2 md:gap-0 no-scrollbar items-center md:items-stretch">
      <button
        v-for="cat in store.level2Categories"
        :key="cat"
        :data-cat="cat"
        @click="scrollToSection(cat)"
        :class="[
          'shrink-0 md:w-full flex items-center justify-between px-2.5 sm:px-4 py-1 sm:py-2 md:py-3 text-[10px] sm:text-sm md:text-base text-left font-bold transition-all duration-100 uppercase',
          store.activeLevel2 === cat 
            ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-[3px] md:border-4 border-black dark:border-term-primary shadow-[2px_2px_0px_0px_#000] md:shadow-[4px_4px_0px_0px_#000] -translate-y-0.5 md:-translate-y-1' 
            : 'bg-transparent text-black dark:text-term-primary border-[3px] md:border-4 border-transparent hover:border-black dark:hover:border-term-primary opacity-70 hover:opacity-100'
        ]"
      >
        <span class="whitespace-nowrap">{{ cat }}</span>
        <ChevronRight v-if="store.activeLevel2 === cat" class="hidden md:block w-5 h-5 ml-2" :stroke-width="3" />
      </button>

      <div v-if="store.level2Categories.length === 0" class="text-center opacity-50 p-4">
        未找到分类
      </div>
    </nav>
    <DailyQuote class="hidden md:block border-t-2 border-black/10 dark:border-term-muted/30 mt-auto" />
  </aside>
</template>
