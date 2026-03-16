<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { Search, X, Palette } from 'lucide-vue-next'
import { useNavigationStore } from './store/navigation'
import { useRouter, useRoute } from 'vue-router'
import MobileNav from './components/MobileNav.vue'
import KeyboardShortcuts from './components/KeyboardShortcuts.vue'
import FeedbackWidget from './components/FeedbackWidget.vue'
import { useScrollProgress } from './composables/useScrollProgress'
import { useAutoDark } from './composables/useAutoDark'
import { usePwaInstall } from './composables/usePwaInstall'

const THEME_KEY = 'nav_theme'
const savedTheme = localStorage.getItem(THEME_KEY) as 'fluent' | 'light' | 'dark' | null

function getAutoTheme(): 'fluent' | 'light' | 'dark' {
  if (savedTheme) return savedTheme
  if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) return 'dark'
  return 'fluent'
}

const currentTheme = ref<'fluent' | 'light' | 'dark'>(getAutoTheme())
const isSearchOpen = ref(false)
const localSearchQuery = ref('')

const store = useNavigationStore()
const router = useRouter()
const route = useRoute()
const { globalScrollProgress } = useScrollProgress()
const scrollProgress = ref(0)
const showProgress = computed(() => route.name === 'SiteDetail' || route.name === 'Home')

const updateProgress = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight
  scrollProgress.value = scrollHeight > 0 ? Math.min((scrollTop / scrollHeight) * 100, 100) : 0
}

watch(showProgress, (val) => {
  if (val && route.name === 'SiteDetail') {
    window.addEventListener('scroll', updateProgress, { passive: true })
  } else {
    window.removeEventListener('scroll', updateProgress)
    scrollProgress.value = 0
  }
})

const themeOrder: Array<'fluent' | 'light' | 'dark'> = ['fluent', 'light', 'dark']

const toggleTheme = () => {
  const idx = themeOrder.indexOf(currentTheme.value)
  currentTheme.value = themeOrder[(idx + 1) % themeOrder.length]
}

const themeName = computed(() => {
  const map = { fluent: '系统原生 (Fluent)', light: '新锐模式 (Neo)', dark: '赛博指令 (Dark)' }
  return map[currentTheme.value]
})

const executeSearch = () => {
  store.$patch({ searchQuery: localSearchQuery.value })
  isSearchOpen.value = false
  router.push('/')
}

const closeSearch = () => {
  isSearchOpen.value = false
}

const handleSearchKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') closeSearch()
}

const { autoDark, shouldBeDark, check } = useAutoDark()
const { showBanner, install, dismiss } = usePwaInstall()

watch(currentTheme, (theme) => {
  const html = document.documentElement
  html.classList.remove('fluent', 'light', 'dark')
  html.classList.add(theme)
  localStorage.setItem(THEME_KEY, theme)
}, { immediate: true })

watch(shouldBeDark, (v) => {
  if (v) {
    if (currentTheme.value !== 'dark') currentTheme.value = 'dark'
  } else {
    const saved = localStorage.getItem(THEME_KEY) as 'fluent' | 'light' | 'dark' | null
    if (saved && currentTheme.value === 'dark') currentTheme.value = saved
  }
}, { immediate: true })

let autoDarkCheckId: ReturnType<typeof setInterval> | null = null
watch(autoDark, (v) => {
  check()
  if (v) {
    if (!autoDarkCheckId) autoDarkCheckId = setInterval(check, 60 * 1000)
  } else {
    if (autoDarkCheckId) { clearInterval(autoDarkCheckId); autoDarkCheckId = null }
  }
}, { immediate: true })

// Matrix rain effect
const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId: number

const initMatrix = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$+-*/=%""\'#&_(),.;:?!\\|{}<>[]^~'.split('')
  const fontSize = 16
  const columns = canvas.width / fontSize
  const drops: number[] = []

  for (let x = 0; x < columns; x++) {
    drops[x] = 1
  }

  const draw = () => {
    const isDark = currentTheme.value === 'dark'
    ctx.fillStyle = isDark ? 'rgba(2, 11, 20, 0.1)' : 'rgba(255, 253, 245, 0.1)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.fillStyle = isDark ? '#33ff00' : '#FFD93D'
    ctx.font = `${fontSize}px monospace`

    for (let i = 0; i < drops.length; i++) {
      const text = characters[Math.floor(Math.random() * characters.length)]
      ctx.fillText(text, i * fontSize, drops[i] * fontSize)

      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
        drops[i] = 0
      }
      drops[i]++
    }
    animationId = requestAnimationFrame(draw)
  }
  
  let lastTime = 0
  const loop = (time: number) => {
    if (time - lastTime > 50) {
      draw()
      lastTime = time
    } else {
      animationId = requestAnimationFrame(loop)
    }
  }
  animationId = requestAnimationFrame(loop)
}

const handleResize = () => {
  if (animationId) cancelAnimationFrame(animationId)
  const canvas = canvasRef.value
  if (canvas) {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  if (currentTheme.value !== 'fluent') {
    initMatrix()
  }
}

const handleGlobalKeydown = (e: KeyboardEvent) => {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
  if ((e.key === '/' || (e.key === 'k' && e.ctrlKey)) && !isSearchOpen.value) {
    e.preventDefault()
    isSearchOpen.value = true
  }
  if (e.key === 'b' || e.key === 'B') {
    e.preventDefault()
    router.push('/favorites')
  }
  if (e.key === 'h' || e.key === 'H') {
    e.preventDefault()
    router.push('/history')
  }
}

onMounted(() => {
  if (currentTheme.value !== 'fluent') {
    initMatrix()
  }
  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleGlobalKeydown)
})

watch(currentTheme, (theme) => {
  if (theme === 'fluent') {
    if (animationId) cancelAnimationFrame(animationId)
    const canvas = canvasRef.value
    if (canvas) {
      const ctx = canvas.getContext('2d')
      if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
  } else {
    if (animationId) cancelAnimationFrame(animationId)
    initMatrix()
  }
})

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (autoDarkCheckId) clearInterval(autoDarkCheckId)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', updateProgress)
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <div class="min-h-screen transition-colors duration-300 relative">
    <!-- Reading Progress Bar -->
    <div
      v-if="showProgress"
      class="fixed top-0 left-0 h-[3px] z-[200] transition-[width] duration-100"
      :class="{
        'bg-blue-500': currentTheme === 'fluent',
        'bg-neo-accent': currentTheme === 'light',
        'bg-[#33ff00]': currentTheme === 'dark'
      }"
      :style="{ width: (route.name === 'Home' ? globalScrollProgress : scrollProgress) + '%' }"
    />

    <canvas ref="canvasRef" class="fixed inset-0 z-0 pointer-events-none opacity-40" v-show="currentTheme !== 'fluent'"></canvas>
    <div class="relative z-10 h-full flex flex-col">
      <!-- Theme Toggle - 三套风格兼容 -->
      <button
        @click="toggleTheme"
        class="theme-toggle-btn fixed bottom-[4.5rem] md:bottom-4 right-4 z-50 flex items-center gap-2 px-3 py-2.5 md:px-4 md:py-3 font-bold text-xs md:text-sm transition-all duration-200"
        :class="{
          'bg-white/80 backdrop-blur-md border border-black/10 text-gray-700 shadow-md hover:shadow-lg hover:-translate-y-0.5 rounded-lg': currentTheme === 'fluent',
          'bg-white border-4 border-black text-black shadow-neo-sm hover:-translate-y-1 active:translate-y-0.5 active:shadow-none': currentTheme === 'light',
          'bg-black border-2 border-[#33ff00] text-[#33ff00] shadow-term-glow hover:-translate-y-1': currentTheme === 'dark'
        }"
      >
        <Palette class="w-4 h-4" :stroke-width="2.5" />
        <span class="hidden sm:inline">{{ themeName }}</span>
      </button>

      <!-- PWA 安装提示 -->
      <transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-y-full opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-full opacity-0"
      >
        <div
          v-if="showBanner"
          class="fixed bottom-0 left-0 right-0 z-[90] p-4 flex items-center justify-between gap-4"
          :class="{
            'bg-white/95 backdrop-blur border-t border-black/10': currentTheme === 'fluent',
            'bg-white border-t-4 border-black shadow-neo-sm': currentTheme === 'light',
            'bg-[#0a0a0a] border-t-2 border-[#33ff00] shadow-term-glow': currentTheme === 'dark'
          }"
        >
          <span class="text-sm font-bold">将 AI 导航站添加到主屏幕，离线也能用</span>
          <div class="flex gap-2 shrink-0">
            <button @click="install" class="px-3 py-1.5 text-xs font-bold uppercase bg-neo-accent dark:bg-term-primary text-white dark:text-black border-2 border-black">安装</button>
            <button @click="dismiss" class="px-3 py-1.5 text-xs font-bold uppercase border-2 border-black/30 dark:border-term-muted opacity-70 hover:opacity-100">稍后</button>
          </div>
        </div>
      </transition>

      <!-- Mobile Floating Search Button -->
      <button
        @click="isSearchOpen = true"
        class="md:hidden fixed bottom-[7.5rem] right-4 z-50 p-2.5 transition-all duration-200"
        :class="{
          'bg-blue-500 text-white rounded-lg shadow-md hover:shadow-lg border border-blue-400/50': currentTheme === 'fluent',
          'bg-neo-accent border-4 border-black text-white shadow-neo-sm hover:-translate-y-1': currentTheme === 'light',
          'bg-black border-2 border-[#33ff00] text-[#33ff00] shadow-term-glow hover:-translate-y-1': currentTheme === 'dark'
        }"
      >
        <Search class="w-5 h-5" :stroke-width="3" />
      </button>

      <!-- Global Search Modal -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="isSearchOpen"
          class="fixed inset-0 z-[100] flex items-start justify-center pt-20 md:pt-24 px-3 sm:px-4 bg-black/60 backdrop-blur-sm"
          @click.self="closeSearch"
          @keydown="handleSearchKeydown"
        >
          <transition
            enter-active-class="transition duration-250 ease-out"
            enter-from-class="transform -translate-y-4 opacity-0 scale-95"
            enter-to-class="transform translate-y-0 opacity-100 scale-100"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="transform translate-y-0 opacity-100 scale-100"
            leave-to-class="transform -translate-y-4 opacity-0 scale-95"
          >
            <div
              v-if="isSearchOpen"
              class="w-full max-w-xl p-3 sm:p-4 flex gap-2"
              :class="{
                'bg-white/90 backdrop-blur-xl rounded-xl border border-black/10 shadow-2xl': currentTheme === 'fluent',
                'bg-white border-4 border-black shadow-[8px_8px_0px_0px_#000]': currentTheme === 'light',
                'bg-[#0a0a0a] border-2 border-[#33ff00] shadow-term-glow': currentTheme === 'dark'
              }"
            >
              <input
                type="text"
                placeholder="搜索 AI 工具、文章..."
                v-model="localSearchQuery"
                @keyup.enter="executeSearch"
                class="flex-1 min-w-0 h-11 md:h-12 pl-3 md:pl-4 pr-3 md:pr-4 text-sm md:text-base font-bold bg-white dark:bg-black border-[3px] border-black dark:border-term-muted focus:bg-neo-secondary dark:focus:border-term-primary focus:outline-none transition-colors"
                autofocus
              />
              <button @click="executeSearch" class="h-11 md:h-12 px-3 md:px-6 shrink-0 bg-neo-accent dark:bg-term-primary border-[3px] border-black dark:border-black text-white dark:text-black font-black uppercase tracking-widest text-xs md:text-sm hover:opacity-90 active:translate-y-0.5 active:translate-x-0.5 transition-all whitespace-nowrap">
                搜索
              </button>
              <button @click="closeSearch" class="h-11 w-11 md:h-12 md:w-12 shrink-0 flex items-center justify-center border-[3px] border-black dark:border-term-muted hover:bg-black/5 dark:hover:bg-term-muted transition-colors">
                <X class="w-5 h-5 md:w-6 md:h-6 dark:text-term-primary" :stroke-width="3" />
              </button>
            </div>
          </transition>
        </div>
      </transition>

      <!-- Route Transition -->
      <router-view v-slot="{ Component }">
        <transition
          enter-active-class="transition-opacity duration-200 ease-out"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-100 ease-in"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
          mode="out-in"
        >
          <component :is="Component" />
        </transition>
      </router-view>

      <MobileNav />
      <KeyboardShortcuts />
      <FeedbackWidget />
    </div>
  </div>
</template>
