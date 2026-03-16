<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigationStore } from '../store/navigation'
import { Keyboard, X } from 'lucide-vue-next'
import { useNoImage } from '../composables/useNoImage'
import { useLinkOpenPref } from '../composables/useLinkOpenPref'
import { useAutoDark } from '../composables/useAutoDark'
import { fetchRandomSites } from '../api/sites'

const show = ref(false)
const router = useRouter()
const store = useNavigationStore()
const { noImageMode, toggleNoImage } = useNoImage()
const { openInNewTab, toggle } = useLinkOpenPref()
const { autoDark, autoDarkMode, check } = useAutoDark()

const shortcuts = [
  { keys: ['/', 'Ctrl+K'], desc: '打开搜索' },
  { keys: ['Esc'], desc: '关闭弹窗' },
  { keys: ['?'], desc: '打开快捷键帮助' },
  { keys: ['B'], desc: '打开收藏' },
  { keys: ['H'], desc: '打开历史' },
  { keys: ['G'], desc: '回到顶部（内容区）' },
  { keys: ['R'], desc: '随机跳转一个工具' },
  { keys: ['1-9'], desc: '切换一级分类' },
]

const handleKey = (e: KeyboardEvent) => {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
  if (e.key === '?' && !e.ctrlKey) {
    show.value = !show.value
  }
  if (e.key === 'Escape') {
    show.value = false
  }
  if (e.key === 'g' || e.key === 'G') {
    const el = document.querySelector('[data-nav-scroll]')
    if (el) (el as HTMLElement).scrollTo({ top: 0, behavior: 'smooth' })
  }
  if (e.key === 'r' || e.key === 'R') {
    fetchRandomSites(1).then((sites) => {
      if (sites.length > 0) {
        const s = sites[0]
        router.push(`/content/${s.type || 'site'}/${s.id}`)
      }
    }).catch(() => {})
  }
  if (e.key === 'b' || e.key === 'B') { e.preventDefault(); router.push('/favorites') }
  if (e.key === 'h' || e.key === 'H') { e.preventDefault(); router.push('/history') }
  const num = parseInt(e.key, 10)
    if (num >= 1 && num <= 9 && store.level1Categories.length >= num) {
    store.activeLevel1 = store.level1Categories[num - 1].name
    router.push('/')
  }
}

defineExpose({ show })

import { onMounted, onBeforeUnmount } from 'vue'
onMounted(() => window.addEventListener('keydown', handleKey))
onBeforeUnmount(() => window.removeEventListener('keydown', handleKey))
</script>

<template>
  <transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="show" class="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="show = false">
      <div class="bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-neo-lg dark:shadow-term-glow w-full max-w-md mx-4 p-6">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-2">
            <Keyboard class="w-5 h-5" :stroke-width="2.5" />
            <h2 class="text-lg font-black uppercase tracking-tighter dark:text-term-primary">键盘快捷键</h2>
          </div>
          <button @click="show = false" class="p-1 hover:opacity-60 transition-opacity">
            <X class="w-5 h-5" :stroke-width="2.5" />
          </button>
        </div>
        <div class="space-y-3">
          <div v-for="s in shortcuts" :key="s.desc" class="flex items-center justify-between py-2 border-b border-black/10 dark:border-term-muted/30">
            <span class="font-bold text-sm opacity-70">{{ s.desc }}</span>
            <div class="flex gap-1.5">
              <kbd v-for="key in s.keys" :key="key" class="px-2 py-1 bg-neo-secondary/50 dark:bg-term-muted border-2 border-black/20 dark:border-term-muted text-xs font-black uppercase">
                {{ key }}
              </kbd>
            </div>
          </div>
          <div class="pt-2 border-t-2 border-black/10 dark:border-term-muted/30 space-y-2">
            <label class="flex items-center justify-between gap-3 cursor-pointer">
              <span class="font-bold text-sm opacity-70">无图模式（仅首字母）</span>
              <button @click="toggleNoImage" :class="noImageMode ? 'bg-neo-accent dark:bg-term-primary' : 'bg-black/10 dark:bg-term-muted'" class="w-10 h-5 rounded-full relative transition-colors">
                <span class="absolute top-0.5 w-4 h-4 bg-white dark:bg-black border-2 border-black dark:border-term-primary rounded-full transition-all" :class="noImageMode ? 'left-5' : 'left-0.5'"></span>
              </button>
            </label>
            <label class="flex items-center justify-between gap-3 cursor-pointer">
              <span class="font-bold text-sm opacity-70">夜间自动暗色</span>
              <button @click="() => { autoDark = !autoDark; check() }" :class="autoDark ? 'bg-neo-accent dark:bg-term-primary' : 'bg-black/10 dark:bg-term-muted'" class="w-10 h-5 rounded-full relative transition-colors">
                <span class="absolute top-0.5 w-4 h-4 bg-white dark:bg-black border-2 border-black dark:border-term-primary rounded-full transition-all" :class="autoDark ? 'left-5' : 'left-0.5'"></span>
              </button>
            </label>
            <div v-if="autoDark" class="flex gap-1 text-[10px] font-bold">
              <button @click="autoDarkMode = 'schedule'; check()" :class="autoDarkMode === 'schedule' ? 'underline' : 'opacity-50'">22:00-6:00</button>
              <span class="opacity-30">|</span>
              <button @click="autoDarkMode = 'system'; check()" :class="autoDarkMode === 'system' ? 'underline' : 'opacity-50'">跟随系统</button>
            </div>
            <label class="flex items-center justify-between gap-3 cursor-pointer">
              <span class="font-bold text-sm opacity-70">新窗口打开链接</span>
              <button @click="toggle" :class="openInNewTab ? 'bg-neo-accent dark:bg-term-primary' : 'bg-black/10 dark:bg-term-muted'" class="w-10 h-5 rounded-full relative transition-colors">
                <span class="absolute top-0.5 w-4 h-4 bg-white dark:bg-black border-2 border-black dark:border-term-primary rounded-full transition-all" :class="openInNewTab ? 'left-5' : 'left-0.5'"></span>
              </button>
            </label>
          </div>
        </div>
        <p class="text-[10px] font-bold opacity-40 mt-4 text-center uppercase">按 ? 或 Esc 关闭此面板</p>
      </div>
    </div>
  </transition>
</template>
