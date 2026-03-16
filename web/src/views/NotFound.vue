<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AlertTriangle, Home, ArrowLeft, Shuffle } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { fetchRandomSites, fetchPopularSites, type Site } from '../api/sites'

const router = useRouter()
const recommendSites = ref<Site[]>([])

onMounted(async () => {
  try {
    recommendSites.value = await fetchPopularSites(6)
  } catch {
    try {
      recommendSites.value = await fetchRandomSites(6)
    } catch { /* ignore */ }
  }
})

const goRandom = async () => {
  try {
    const sites = await fetchRandomSites(1)
    if (sites.length > 0) {
      const s = sites[0]
      router.push(`/content/${s.type || 'site'}/${s.id}`)
    }
  } catch {
    router.push('/')
  }
}

const goTo = (s: Site) => router.push(`/content/${s.type || 'site'}/${s.id}`)
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-6 font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <div class="text-center max-w-lg">
      <div class="relative inline-block mb-8">
        <div class="text-[120px] md:text-[180px] font-black uppercase tracking-tighter leading-none -rotate-3 select-none" style="-webkit-text-stroke: 4px currentColor; color: transparent;">
          404
        </div>
        <AlertTriangle class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 md:w-16 md:h-16 text-neo-accent dark:text-[#ff3333]" :stroke-width="2" />
      </div>

      <h1 class="text-2xl md:text-4xl font-black uppercase tracking-tighter mb-4 dark:text-term-primary">页面走丢了</h1>
      <p class="font-bold opacity-60 mb-8 dark:text-term-secondary">你访问的页面不存在，可能已被移除或链接有误。</p>

      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <router-link to="/" class="btn-primary h-12 px-8 flex items-center justify-center gap-2">
          <Home class="w-4 h-4" :stroke-width="2.5" />
          返回首页
        </router-link>
        <button @click="router.back()" class="btn-secondary h-12 px-8 flex items-center justify-center gap-2">
          <ArrowLeft class="w-4 h-4" :stroke-width="2.5" />
          返回上页
        </button>
        <button @click="goRandom" class="h-12 px-8 flex items-center justify-center gap-2 border-4 border-black dark:border-term-muted font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors">
          <Shuffle class="w-4 h-4" :stroke-width="2.5" />
          随机探索
        </button>
      </div>
      <div v-if="recommendSites.length > 0" class="mt-12 pt-8 border-t-2 border-black/10 dark:border-term-muted/30">
        <p class="text-sm font-bold opacity-60 mb-3 dark:text-term-secondary">热门推荐</p>
        <div class="flex flex-wrap gap-2 justify-center">
          <button v-for="s in recommendSites" :key="s.id" @click="goTo(s)" class="px-3 py-2 border-2 border-black dark:border-term-muted text-sm font-bold hover:bg-neo-accent dark:hover:bg-term-primary hover:text-white dark:hover:text-black transition-colors">
            {{ s.name }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
