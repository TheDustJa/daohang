<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { FileText, TrendingUp, Clock, Eye } from 'lucide-vue-next'
import LayoutHeader from '../components/LayoutHeader.vue'
import { useNavigationStore } from '../store/navigation'
import { useRouter } from 'vue-router'
import type { Site } from '../api/sites'

const store = useNavigationStore()
const router = useRouter()
const sortBy = ref<'latest' | 'popular'>('latest')

onMounted(async () => {
  if (store.sites.length === 0) await store.loadSites()
})

const articles = computed(() => {
  const list = store.sites.filter(s => s.type === 'article')
  if (sortBy.value === 'popular') {
    return [...list].sort((a, b) => (b.clickCount ?? 0) - (a.clickCount ?? 0))
  }
  return [...list].sort((a, b) => (b.createdAt ?? '').localeCompare(a.createdAt ?? ''))
})

const goToArticle = (article: Site) => {
  router.push(`/content/article/${article.id}`)
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <LayoutHeader class="shrink-0 relative z-20" />
    <main class="flex-1 container mx-auto max-w-4xl py-8 md:py-12 px-4 md:px-6">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <FileText class="w-6 h-6 md:w-8 md:h-8" :stroke-width="2.5" />
          <h1 class="text-2xl md:text-4xl font-black uppercase tracking-tighter dark:text-term-primary">文章专区</h1>
        </div>
        <div class="flex gap-2">
          <button
            @click="sortBy = 'latest'"
            class="flex items-center gap-1 px-3 py-1.5 text-xs font-bold uppercase border-2 transition-colors"
            :class="sortBy === 'latest' ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-black dark:border-term-primary' : 'border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted'"
          >
            <Clock class="w-3 h-3" :stroke-width="2.5" />
            最新
          </button>
          <button
            @click="sortBy = 'popular'"
            class="flex items-center gap-1 px-3 py-1.5 text-xs font-bold uppercase border-2 transition-colors"
            :class="sortBy === 'popular' ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-black dark:border-term-primary' : 'border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted'"
          >
            <TrendingUp class="w-3 h-3" :stroke-width="2.5" />
            热门
          </button>
        </div>
      </div>

      <div v-if="articles.length === 0" class="text-center py-20 opacity-50">
        <FileText class="w-16 h-16 mx-auto mb-4" :stroke-width="1.5" />
        <h2 class="text-xl font-black uppercase">暂无文章</h2>
      </div>

      <div v-else class="space-y-4">
        <article
          v-for="(article, idx) in articles"
          :key="article.id"
          @click="goToArticle(article)"
          class="nav-card card-animate-in p-4 md:p-6 cursor-pointer group flex gap-4 md:gap-6 items-start"
          :style="{ animationDelay: `${idx * 0.05}s` }"
        >
          <div class="hidden md:flex w-10 h-10 bg-neo-accent dark:bg-term-primary text-white dark:text-black items-center justify-center font-black text-lg shrink-0 -rotate-2 group-hover:rotate-0 transition-transform">
            {{ idx + 1 }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-2">
              <span v-if="article.isRecommended" class="px-2 py-0.5 bg-neo-accent dark:bg-[#ff3333] text-white text-[9px] font-black uppercase border border-black">推荐</span>
              <span v-for="tag in article.tags.slice(0, 3)" :key="tag" class="px-1.5 py-0.5 border border-black dark:border-term-muted text-[9px] font-black uppercase tracking-widest">{{ tag }}</span>
            </div>
            <h3 class="text-base md:text-xl font-black uppercase tracking-tighter mb-1 group-hover:text-neo-accent dark:group-hover:text-term-secondary transition-colors">{{ article.name }}</h3>
            <p class="text-xs md:text-sm font-bold text-black/60 dark:text-term-primary/60 line-clamp-2">{{ article.description }}</p>
            <div class="flex items-center gap-4 mt-3 text-[10px] md:text-xs font-bold opacity-50">
              <span class="flex items-center gap-1"><Eye class="w-3 h-3" :stroke-width="2" /> {{ article.clickCount ?? 0 }}</span>
              <span>{{ article.level2 }}</span>
            </div>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>
