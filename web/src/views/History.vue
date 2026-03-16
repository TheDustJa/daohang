<script setup lang="ts">
import { Clock, Trash2 } from 'lucide-vue-next'
import LayoutHeader from '../components/LayoutHeader.vue'
import { useHistory } from '../composables/useHistory'
import { useRouter } from 'vue-router'

const router = useRouter()
const { historyList, clearHistory, removeFromHistory } = useHistory()

const navigateTo = (item: { id: number; type: string }) => {
  router.push(`/content/${item.type}/${item.id}`)
}

const formatTime = (ts: number) => {
  const d = new Date(ts)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr} 小时前`
  const diffDay = Math.floor(diffHr / 24)
  if (diffDay < 30) return `${diffDay} 天前`
  return d.toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <LayoutHeader class="shrink-0 relative z-20" />
    <main class="flex-1 container mx-auto max-w-4xl py-8 md:py-12 px-4 md:px-6">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <Clock class="w-6 h-6 md:w-8 md:h-8" :stroke-width="2.5" />
          <h1 class="text-2xl md:text-4xl font-black uppercase tracking-tighter dark:text-term-primary">浏览历史</h1>
        </div>
        <button
          v-if="historyList.length > 0"
          @click="clearHistory"
          class="flex items-center gap-1.5 px-3 py-2 text-xs font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-accent hover:text-white dark:hover:bg-term-primary dark:hover:text-black transition-colors"
        >
          <Trash2 class="w-3.5 h-3.5" :stroke-width="2.5" />
          清空
        </button>
      </div>

      <div v-if="historyList.length === 0" class="flex flex-col items-center justify-center py-20 opacity-50">
        <Clock class="w-16 h-16 mb-4" :stroke-width="1.5" />
        <h2 class="text-xl font-black uppercase">暂无浏览记录</h2>
        <p class="font-bold mt-2 text-sm">浏览过的内容会显示在这里</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="item in historyList"
          :key="item.id + '-' + item.visitedAt"
          class="nav-card p-3 md:p-4 flex items-center gap-4 cursor-pointer group"
          @click="navigateTo(item)"
        >
          <div class="w-10 h-10 md:w-12 md:h-12 bg-neo-secondary dark:bg-black border-2 border-black dark:border-term-primary flex items-center justify-center shrink-0 -rotate-2 group-hover:rotate-0 transition-transform">
            <span class="font-black text-lg dark:text-term-primary">{{ item.name[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-black text-sm md:text-base uppercase tracking-tighter truncate">{{ item.name }}</h3>
              <span class="px-1.5 py-0.5 border border-black dark:border-term-muted text-[9px] font-black uppercase shrink-0">
                {{ item.type === 'article' ? 'ARTICLE' : 'SITE' }}
              </span>
            </div>
            <p class="text-[11px] md:text-xs font-bold text-black/60 dark:text-term-primary/60 truncate">{{ item.description }}</p>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <span class="text-[10px] md:text-xs font-bold opacity-50 whitespace-nowrap">{{ formatTime(item.visitedAt) }}</span>
            <button
              @click.stop="removeFromHistory(item.id)"
              class="p-1.5 opacity-0 group-hover:opacity-60 hover:!opacity-100 transition-opacity"
            >
              <Trash2 class="w-4 h-4" :stroke-width="2" />
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
