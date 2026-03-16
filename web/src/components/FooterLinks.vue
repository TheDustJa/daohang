<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Link2, Rss } from 'lucide-vue-next'
import { fetchFriendLinks, fetchStats, type FriendLink } from '../api/sites'

const props = withDefaults(defineProps<{
  stats?: { totalSites: number; totalArticles: number; totalCategories: number; totalTags: number }
}>(), { stats: () => ({ totalSites: 0, totalArticles: 0, totalCategories: 0, totalTags: 0 }) })

const friendLinks = ref<FriendLink[]>([])
const apiStats = ref<{ totalSites: number; totalArticles: number; totalCategories: number; totalTags: number } | null>(null)

const displayStats = computed(() => {
  const p = props.stats
  if (p && (p.totalSites > 0 || p.totalArticles > 0)) return p
  return apiStats.value || p
})

onMounted(async () => {
  try {
    friendLinks.value = await fetchFriendLinks()
  } catch {
    friendLinks.value = []
  }
  try {
    apiStats.value = await fetchStats()
  } catch { /* ignore */ }
})
</script>

<template>
  <footer class="border-t-4 border-black dark:border-term-muted bg-neo-bg dark:bg-[#0a0a0a] py-8 px-6 mt-16 shadow-[0_-4px_0_0_rgba(0,0,0,0.1)] dark:shadow-none w-full flex-shrink-0">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
      <div class="flex flex-col items-center md:items-start gap-4 w-full md:w-auto">
        <div class="flex items-center gap-2 font-black uppercase tracking-tighter text-lg dark:text-term-primary">
          <Link2 class="w-5 h-5" :stroke-width="3" />
          友情链接
        </div>
        <div v-if="friendLinks.length" class="flex flex-wrap justify-center md:justify-start gap-3">
          <a
            v-for="item in friendLinks"
            :key="item.id"
            :href="item.siteUrl"
            target="_blank"
            rel="noreferrer"
            class="px-3 py-1 border-2 border-black dark:border-term-muted text-sm font-bold hover:bg-neo-accent hover:text-white dark:hover:bg-term-primary dark:hover:text-black transition-colors bg-white dark:bg-black"
          >
            {{ item.siteName }}
          </a>
        </div>
        <div v-else class="text-sm font-bold opacity-60">暂无已通过的友情链接</div>
      </div>

      <div class="flex flex-col items-center md:items-end gap-2 text-sm font-bold opacity-70">
        <div v-if="displayStats && (displayStats.totalSites > 0 || displayStats.totalArticles > 0)" class="flex flex-wrap gap-3 justify-center md:justify-end text-xs">
          <span>{{ displayStats.totalSites }} 工具</span>
          <span>{{ displayStats.totalArticles }} 文章</span>
          <span>{{ displayStats.totalCategories }} 分类</span>
          <span>{{ displayStats.totalTags }} 标签</span>
        </div>
        <a href="/api/v1/rss.xml" target="_blank" rel="noreferrer" class="flex items-center gap-1 hover:underline">
          <Rss class="w-3.5 h-3.5" :stroke-width="2.5" />
          RSS 订阅
        </a>
        <div>© 2026 AI Navigation Pro-Max. All rights reserved.</div>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer" class="hover:underline flex items-center gap-1">
          <span>京 ICP 备 XXXXXX 号-1</span>
        </a>
      </div>
    </div>
  </footer>
</template>
