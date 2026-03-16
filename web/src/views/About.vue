<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Users, Globe, Zap, Heart, Code, Rss } from 'lucide-vue-next'
import LayoutHeader from '../components/LayoutHeader.vue'
import { useNavigationStore } from '../store/navigation'

const store = useNavigationStore()

onMounted(async () => {
  if (store.sites.length === 0) await store.loadSites()
})

const stats = computed(() => ({
  totalSites: store.sites.filter(s => s.type !== 'article').length,
  totalArticles: store.sites.filter(s => s.type === 'article').length,
  totalCategories: store.level1Categories.length,
  totalTags: new Set(store.sites.flatMap(s => s.tags)).size,
}))

const features = [
  { icon: Globe, title: '海量工具收录', desc: '覆盖 AI 写作、绘画、编程、数据分析等全领域工具' },
  { icon: Zap, title: '实时更新', desc: '持续跟踪 AI 行业动态，第一时间收录优质新工具' },
  { icon: Code, title: '技术文章', desc: '深度评测、教程指南、行业分析，助你深入理解 AI' },
  { icon: Heart, title: '社区驱动', desc: '支持用户投稿、评价、收藏，共建 AI 知识库' },
]
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <LayoutHeader class="shrink-0 relative z-20" />
    <main class="flex-1 container mx-auto max-w-4xl py-8 md:py-16 px-4 md:px-6">
      <div class="text-center mb-12 md:mb-16">
        <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter -rotate-1 dark:text-term-primary mb-4">关于我们</h1>
        <p class="text-base md:text-lg font-bold opacity-70 max-w-2xl mx-auto dark:text-term-secondary">
          AI 导航站致力于收录全球最优质的 AI 工具和资源，帮助每一个人高效探索人工智能世界。
        </p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-12 md:mb-16">
        <div class="nav-card p-4 md:p-6 text-center">
          <div class="text-3xl md:text-4xl font-black dark:text-term-primary">{{ stats.totalSites }}</div>
          <div class="text-xs font-bold uppercase tracking-widest opacity-50 mt-1">工具收录</div>
        </div>
        <div class="nav-card p-4 md:p-6 text-center">
          <div class="text-3xl md:text-4xl font-black dark:text-term-primary">{{ stats.totalArticles }}</div>
          <div class="text-xs font-bold uppercase tracking-widest opacity-50 mt-1">技术文章</div>
        </div>
        <div class="nav-card p-4 md:p-6 text-center">
          <div class="text-3xl md:text-4xl font-black dark:text-term-primary">{{ stats.totalCategories }}</div>
          <div class="text-xs font-bold uppercase tracking-widest opacity-50 mt-1">分类目录</div>
        </div>
        <div class="nav-card p-4 md:p-6 text-center">
          <div class="text-3xl md:text-4xl font-black dark:text-term-primary">{{ stats.totalTags }}</div>
          <div class="text-xs font-bold uppercase tracking-widest opacity-50 mt-1">标签数量</div>
        </div>
      </div>

      <!-- Features -->
      <h2 class="text-2xl md:text-3xl font-black uppercase tracking-tighter mb-6 border-b-4 border-black dark:border-term-muted pb-3">核心特色</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-12 md:mb-16">
        <div v-for="f in features" :key="f.title" class="nav-card p-5 md:p-6 flex gap-4">
          <div class="w-12 h-12 bg-neo-accent dark:bg-term-primary flex items-center justify-center shrink-0 -rotate-2 border-2 border-black dark:border-black">
            <component :is="f.icon" class="w-6 h-6 text-white dark:text-black" :stroke-width="2.5" />
          </div>
          <div>
            <h3 class="font-black uppercase text-base mb-1">{{ f.title }}</h3>
            <p class="text-sm font-bold opacity-60">{{ f.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Links -->
      <div class="nav-card p-6 md:p-8 text-center">
        <h2 class="text-xl font-black uppercase tracking-tighter mb-4">订阅与关注</h2>
        <div class="flex flex-wrap gap-3 justify-center">
          <a href="/api/v1/rss.xml" target="_blank" class="flex items-center gap-2 px-4 py-2 border-2 border-black dark:border-term-muted font-bold text-sm hover:bg-neo-accent hover:text-white dark:hover:bg-term-primary dark:hover:text-black transition-colors">
            <Rss class="w-4 h-4" :stroke-width="2.5" />
            RSS 订阅
          </a>
          <router-link to="/submit" class="flex items-center gap-2 px-4 py-2 bg-neo-accent dark:bg-term-primary text-white dark:text-black border-2 border-black dark:border-black font-bold text-sm hover:-translate-y-0.5 transition-transform">
            提交工具
          </router-link>
          <router-link to="/friend-link" class="flex items-center gap-2 px-4 py-2 border-2 border-black dark:border-term-muted font-bold text-sm hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors">
            <Users class="w-4 h-4" :stroke-width="2.5" />
            友链合作
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>
