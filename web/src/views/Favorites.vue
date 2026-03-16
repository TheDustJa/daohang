<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Heart, Download, Upload } from 'lucide-vue-next'
import LayoutHeader from '../components/LayoutHeader.vue'
import ToolCard from '../components/ToolCard.vue'
import { useNavigationStore } from '../store/navigation'
import { useFavorites } from '../composables/useFavorites'
import { Toast } from '../utils/toast'

const store = useNavigationStore()
const { getFavoriteSites, favoriteIds, addFavorites } = useFavorites()

onMounted(async () => {
  if (store.sites.length === 0) {
    await store.loadSites()
  }
})

const favoriteSites = computed(() => getFavoriteSites(store.sites, true))

const exportAs = (format: 'json' | 'markdown' | 'html' | 'html-list' | 'notion' | 'csv') => {
  const sites = favoriteSites.value
  if (sites.length === 0) return

  let content: string
  let filename: string
  let mime: string

  if (format === 'html') {
    const lines = ['<!DOCTYPE NETSCAPE Bookmark file>', '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">', '<TITLE>AI 导航收藏</TITLE>', '<H1>AI 导航收藏</H1>', '<DL>']
    sites.forEach((s) => {
      const url = s.url || '#'
      const title = s.name.replace(/</g, '&lt;').replace(/>/g, '&gt;')
      lines.push(`<DT><A HREF="${url}">${title}</A>`)
    })
    lines.push('</DL>')
    content = lines.join('\n')
    filename = 'ai-nav-favorites.html'
    mime = 'text/html'
  } else if (format === 'csv') {
    const header = '名称,链接,描述,标签'
    const rows = sites.map((s) => {
      const name = (s.name || '').replace(/"/g, '""')
      const url = (s.url || '').replace(/"/g, '""')
      const desc = (s.description || '').replace(/"/g, '""').replace(/\n/g, ' ')
      const tags = (s.tags || []).join(';')
      return `"${name}","${url}","${desc}","${tags}"`
    })
    content = [header, ...rows].join('\n')
    filename = 'ai-nav-favorites.csv'
    mime = 'text/csv'
  } else if (format === 'notion') {
    const lines = sites.map((s) => `- [${s.name}](${s.url || '#'}) - ${(s.description || '').slice(0, 100)}`)
    content = lines.join('\n')
    filename = 'ai-nav-favorites-notion.txt'
    mime = 'text/plain'
  } else if (format === 'html-list') {
    const items = sites.map((s) => `<li><a href="${(s.url || '#').replace(/"/g, '&quot;')}">${(s.name || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</a></li>`).join('\n')
    content = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI 导航收藏</title></head><body><ul>\n${items}\n</ul></body></html>`
    filename = 'ai-nav-favorites.html'
    mime = 'text/html'
  } else if (format === 'json') {
    content = JSON.stringify(sites.map(s => ({
      name: s.name,
      url: s.url,
      description: s.description,
      tags: s.tags,
      type: s.type
    })), null, 2)
    filename = 'ai-nav-favorites.json'
    mime = 'application/json'
  } else {
    const lines = ['# 我的 AI 工具收藏\n']
    sites.forEach(s => {
      lines.push(`## ${s.name}`)
      if (s.url) lines.push(`- 链接：[${s.url}](${s.url})`)
      if (s.description) lines.push(`- 简介：${s.description}`)
      if (s.tags.length) lines.push(`- 标签：${s.tags.join(', ')}`)
      lines.push('')
    })
    content = lines.join('\n')
    filename = 'ai-nav-favorites.md'
    mime = 'text/markdown'
  }

  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
  Toast.success(`已导出 ${sites.length} 个收藏`)
}

function normalizeUrl(url: string): string {
  try {
    const u = new URL(url)
    return u.hostname.replace(/^www\./, '') + u.pathname.replace(/\/$/, '') || u.hostname
  } catch {
    return url.toLowerCase()
  }
}

const importBookmarks = (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  input.value = ''
  const reader = new FileReader()
  reader.onload = () => {
    const html = String(reader.result || '')
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const links = Array.from(doc.querySelectorAll('a[href]'))
    const bookmarks: { url: string; title: string }[] = []
    links.forEach((a) => {
      const href = (a as HTMLAnchorElement).href
      if (href && !href.startsWith('place:') && !href.startsWith('data:')) {
        bookmarks.push({ url: href, title: (a as HTMLAnchorElement).textContent?.trim() || href })
      }
    })
    const allSites = store.sites
    const urlToSite = new Map<string, { id: number }>()
    allSites.forEach((s) => {
      if (s.url) {
        const key = normalizeUrl(s.url)
        if (!urlToSite.has(key)) urlToSite.set(key, { id: s.id })
      }
    })
    const matchedIds: number[] = []
    const notFound: { url: string; title: string }[] = []
    bookmarks.forEach((b) => {
      const key = normalizeUrl(b.url)
      const site = urlToSite.get(key)
      if (site) {
        matchedIds.push(site.id)
      } else {
        notFound.push(b)
      }
    })
    addFavorites(matchedIds)
    Toast.success(`导入完成：${matchedIds.length} 个已加入收藏，${notFound.length} 个未匹配`)
  }
  reader.readAsText(file, 'UTF-8')
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <LayoutHeader class="shrink-0 relative z-20" />
    <main class="flex-1 container mx-auto max-w-6xl py-8 md:py-12 px-4 md:px-6">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <Heart class="w-6 h-6 md:w-8 md:h-8 text-neo-accent dark:text-[#ff3333]" :stroke-width="2.5" fill="currentColor" />
          <h1 class="text-2xl md:text-4xl font-black uppercase tracking-tighter dark:text-term-primary">我的收藏</h1>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <label class="cursor-pointer px-2 py-1 text-[10px] font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors flex items-center gap-1">
            <Upload class="w-3 h-3" :stroke-width="2.5" />
            导入书签
            <input type="file" accept=".html,.htm" class="hidden" @change="importBookmarks" />
          </label>
          <span class="text-sm font-bold opacity-60 dark:text-term-secondary">{{ favoriteIds.length }} 个项目</span>
          <div v-if="favoriteSites.length > 0" class="flex gap-1">
            <button @click="exportAs('json')" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="导出 JSON">
              <Download class="w-3 h-3 inline" :stroke-width="2.5" /> JSON
            </button>
            <button @click="exportAs('markdown')" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="导出 Markdown">
              <Download class="w-3 h-3 inline" :stroke-width="2.5" /> MD
            </button>
            <button @click="exportAs('html')" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="导出 HTML 书签">书签</button>
            <button @click="exportAs('html-list')" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="导出 HTML 列表">HTML</button>
            <button @click="exportAs('notion')" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="导出 Notion">
              <Download class="w-3 h-3 inline" :stroke-width="2.5" /> Notion
            </button>
            <button @click="exportAs('csv')" class="px-2 py-1 text-[10px] font-bold uppercase border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="导出 CSV">
              <Download class="w-3 h-3 inline" :stroke-width="2.5" /> CSV
            </button>
          </div>
        </div>
      </div>

      <div v-if="favoriteSites.length === 0" class="flex flex-col items-center justify-center py-20">
        <Heart class="w-16 h-16 mb-4 opacity-50" :stroke-width="1.5" />
        <h2 class="text-xl font-black uppercase opacity-70">暂无收藏</h2>
        <p class="font-bold mt-2 text-sm opacity-60">点击工具卡片上的爱心按钮即可收藏</p>
        <p class="font-bold mt-4 text-xs opacity-50">或到首页浏览「今日热门」「随机探索」发现好工具</p>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-5 md:gap-6">
        <ToolCard v-for="(site, idx) in favoriteSites" :key="site.id" :site="site" :index="idx" />
      </div>
    </main>
  </div>
</template>
