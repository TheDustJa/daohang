<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, X } from 'lucide-vue-next'
import { useNavigationStore } from './store/navigation'
import { useRouter } from 'vue-router'

// 'fluent' | 'light' | 'dark'
const currentTheme = ref('fluent')
const isSearchOpen = ref(false)
const localSearchQuery = ref('')

const store = useNavigationStore()
const router = useRouter()

const toggleTheme = () => {
  if (currentTheme.value === 'fluent') {
    currentTheme.value = 'light'
  } else if (currentTheme.value === 'light') {
    currentTheme.value = 'dark'
  } else {
    currentTheme.value = 'fluent'
  }
}

const themeName = computed(() => {
  if (currentTheme.value === 'fluent') return '系统原生 (Fluent)'
  if (currentTheme.value === 'light') return '新锐模式(Neo)'
  return '赛博指令(Dark)'
})

const executeSearch = () => {
  store.$patch({ searchQuery: localSearchQuery.value })
  isSearchOpen.value = false
  router.push('/')
}

const closeSearch = () => {
  isSearchOpen.value = false
}

// Watch theme changes and update HTML class
watch(currentTheme, (theme) => {
  const html = document.documentElement
  html.classList.remove('fluent', 'light', 'dark')
  html.classList.add(theme)
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
    // #020b14 is the new blue theme bg color
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

import { onMounted, onBeforeUnmount, computed } from 'vue'

onMounted(() => {
  if (currentTheme.value !== 'fluent') {
     initMatrix()
  }
  window.addEventListener('resize', handleResize)
})

watch(currentTheme, (theme) => {
  if (theme === 'fluent') {
    if (animationId) cancelAnimationFrame(animationId)
    const canvas = canvasRef.value
    if (canvas) {
      const ctx = canvas.getContext('2d')
      // Clear matrix for fluent
      if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
  } else {
    if (animationId) cancelAnimationFrame(animationId)
    initMatrix()
  }
})

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="min-h-screen transition-colors duration-300 relative">
    <canvas ref="canvasRef" class="fixed inset-0 z-0 pointer-events-none opacity-40" v-show="currentTheme !== 'fluent'"></canvas>
    <div class="relative z-10 h-full flex flex-col">
      <button @click="toggleTheme" class="fixed bottom-4 right-4 z-50 p-3 rounded bg-white dark:bg-black border-4 border-black dark:border-[#33ff00] text-black dark:text-[#33ff00] font-bold shadow-neo-sm hover:-translate-y-1 transition-transform">
        {{ themeName }}
      </button>

      <!-- Mobile Floating Search Button -->
      <button @click="isSearchOpen = true" class="md:hidden fixed bottom-20 right-4 z-50 p-2 sm:p-3 rounded bg-neo-accent dark:bg-term-primary border-2 sm:border-4 border-black dark:border-black text-white dark:text-black font-bold shadow-neo-sm hover:-translate-y-1 transition-transform">
        <Search class="w-5 h-5 sm:w-6 sm:h-6" :stroke-width="3" />
      </button>

      <!-- Global Search Modal (Mobile & PC overlay) -->
      <div v-if="isSearchOpen" class="fixed inset-0 z-[100] flex items-start justify-center pt-24 px-2 sm:px-4 bg-black/60 backdrop-blur-sm" @click.self="closeSearch">
        <div class="bg-white dark:bg-[#0a0a0a] border-4 border-black dark:border-term-primary shadow-[4px_4px_0px_0px_#000] sm:shadow-[8px_8px_0px_0px_#000] w-full max-w-xl p-2 sm:p-4 flex gap-1.5 sm:gap-2">
          <input 
            type="text" 
            placeholder="搜索..." 
            v-model="localSearchQuery"
            @keyup.enter="executeSearch"
            class="flex-1 min-w-0 h-10 md:h-12 pl-2 md:pl-4 pr-2 md:pr-4 text-sm md:text-lg font-bold uppercase bg-white dark:bg-black border-[3px] border-black dark:border-term-muted focus:bg-neo-secondary dark:focus:border-term-primary focus:outline-none transition-colors"
            autofocus
          />
          <button @click="executeSearch" class="h-10 md:h-12 px-2 sm:px-3 md:px-6 shrink-0 bg-neo-accent dark:bg-term-primary border-[3px] border-black dark:border-black text-white dark:text-black font-black uppercase tracking-widest text-[11px] sm:text-sm md:text-base hover:opacity-90 active:translate-y-0.5 active:translate-x-0.5 transition-all whitespace-nowrap">
            搜索
          </button>
          <button @click="closeSearch" class="h-10 w-10 md:h-12 md:w-12 shrink-0 flex items-center justify-center border-[3px] border-black dark:border-term-muted hover:bg-black/5 dark:hover:bg-term-muted transition-colors">
            <X class="w-5 h-5 md:w-6 md:h-6 dark:text-term-primary" :stroke-width="3" />
          </button>
        </div>
      </div>

      <router-view />
    </div>
  </div>
</template>
