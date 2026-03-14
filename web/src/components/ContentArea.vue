<script setup lang="ts">
import { useNavigationStore } from '../store/navigation'
import ToolCard from './ToolCard.vue'
import FooterLinks from './FooterLinks.vue'
import { ArrowUp } from 'lucide-vue-next'
import { ref, onMounted, nextTick, watch } from 'vue'

const store = useNavigationStore()

const contentRef = ref<HTMLElement | null>(null)
const showBackToTop = ref(false)

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
    showBackToTop.value = contentRef.value.scrollTop > 300
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
})
</script>

<template>
  <main ref="contentRef" class="p-8 pb-32" @scroll="onScroll">
    <!-- Empty State -->
    <div v-if="store.isLoading" class="flex flex-col gap-8 animate-pulse">
      <div v-for="i in 3" :key="i" class="h-64 bg-black/10 dark:bg-term-muted/20 border-4 border-black/10 dark:border-term-muted"></div>
    </div>
    
    <div v-else-if="Object.keys(store.sitesGroupedByLevel2).length === 0" class="flex flex-col items-center justify-center h-full opacity-50 pt-20">
      <h2 class="text-4xl font-black uppercase tracking-tighter">未找到结果</h2>
      <p class="font-bold mt-2 uppercase">请尝试调整您的搜索条件</p>
    </div>

    <!-- Grouped Sections (All Level 2 categories inline) -->
    <div class="space-y-6 md:space-y-8">
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
          <span class="font-bold uppercase tracking-widest opacity-50 dark:text-term-secondary text-[9px] sm:text-[10px] md:text-base">
            [{{ sites.length }} 个项目]
          </span>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3 sm:gap-5 md:gap-6">
          <ToolCard v-for="site in sites" :key="site.id" :site="site" />
        </div>
      </section>
    </div>

    <!-- Global Footer -->
    <FooterLinks class="mt-20 md:mt-24 mb-6 md:mb-0" />

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
        class="fixed bottom-36 md:bottom-20 right-4 z-50 p-3 rounded bg-white dark:bg-black border-4 border-black dark:border-[#33ff00] text-black dark:text-[#33ff00] shadow-neo-sm transition-all hover:scale-105 active:scale-95 flex items-center justify-center"
        title="回到顶部"
      >
        <ArrowUp class="w-5 h-5 sm:w-6 sm:h-6" :stroke-width="3" />
      </button>
    </transition>
  </main>
</template>
