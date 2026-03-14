<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import DOMPurify from 'dompurify'
import MarkdownIt from 'markdown-it'
import { fetchSiteById, type Site } from '../api/sites'
import LayoutHeader from '../components/LayoutHeader.vue'

const route = useRoute()
const router = useRouter()
const content = ref<Site | null>(null)
const isLoading = ref(true)

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  breaks: true
})

const contentType = computed(() => route.params.type === 'article' ? 'article' : 'site')
const contentId = computed(() => Number(route.params.id))

const renderedArticleHtml = computed(() => {
  if (!content.value || content.value.type !== 'article') return ''
  const body = content.value.content || ''
  if (!body.trim()) return ''

  if (content.value.contentFormat === 'markdown') {
    return DOMPurify.sanitize(md.render(body))
  }

  if (content.value.contentFormat === 'html') {
    return DOMPurify.sanitize(body)
  }

  return ''
})

const articleIsPlainText = computed(() => content.value?.type === 'article' && content.value.contentFormat === 'text')

onMounted(async () => {
  content.value = await fetchSiteById(contentType.value, contentId.value) || null
  isLoading.value = false

  if (content.value) {
    useHead({
      title: `${content.value.name} - AI Navigation Directory`,
      meta: [
        { name: 'description', content: content.value.description }
      ]
    })
  }
})

const goBack = () => router.push('/')
const goWebsite = () => {
  if (content.value?.url) window.open(content.value.url, '_blank')
}

const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement
  target.style.display = 'none'
  if (target.nextElementSibling) {
    ;(target.nextElementSibling as HTMLElement).style.display = 'block'
  }
}

const getDomain = (url: string) => {
  try {
    return new URL(url).hostname
  } catch {
    return ''
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <LayoutHeader class="shrink-0 relative z-20" />

    <main class="flex-1 container mx-auto max-w-4xl py-12 px-6">
      <button @click="goBack" class="mb-8 font-bold uppercase tracking-widest opacity-50 hover:opacity-100 transition-opacity">
        ← 返回导航
      </button>

      <div v-if="isLoading" class="animate-pulse flex flex-col gap-6">
        <div class="h-12 w-1/3 bg-black/10 dark:bg-term-muted border-4 border-black dark:border-term-primary"></div>
        <div class="h-64 bg-black/10 dark:bg-term-muted border-4 border-black dark:border-term-primary"></div>
      </div>

      <div v-else-if="!content" class="text-center py-20">
        <h1 class="text-6xl font-black uppercase tracking-tighter">404 未找到内容</h1>
      </div>

      <div v-else class="space-y-8">
        <header class="flex items-center gap-6">
          <div class="w-24 h-24 bg-neo-secondary dark:bg-black border-4 border-black dark:border-term-primary flex items-center justify-center -rotate-3 overflow-hidden relative shrink-0">
            <img v-if="content.type === 'site' && content.url" :src="`https://www.google.com/s2/favicons?domain=${getDomain(content.url)}&sz=128`" @error="handleImageError" class="w-16 h-16 object-contain block z-10" />
            <span class="font-black text-4xl dark:text-term-primary absolute">{{ content.logo?.[0] || content.name[0] }}</span>
          </div>
          <div>
            <div class="flex flex-wrap items-center gap-3 mb-2">
              <span class="px-3 py-1 border-2 border-black dark:border-term-muted text-xs font-black tracking-[0.25em] uppercase">
                {{ content.type === 'article' ? 'Article' : 'Site' }}
              </span>
              <span class="text-sm opacity-60">{{ content.level1 }} / {{ content.level2 }}<template v-if="content.level3"> / {{ content.level3 }}</template></span>
            </div>
            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter">{{ content.name }}</h1>
          </div>
        </header>

        <section class="p-8 bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-[8px_8px_0px_#000] dark:shadow-term-glow">
          <h2 class="text-2xl font-black uppercase mb-4 border-b-4 border-black dark:border-term-muted pb-2">概览</h2>
          <p class="font-bold text-lg leading-relaxed">{{ content.description }}</p>

          <div class="flex flex-wrap gap-3 mt-6">
            <span
              v-for="tag in content.tags"
              :key="tag"
              class="px-3 py-1 bg-neo-muted dark:bg-black border-2 border-black dark:border-term-muted font-black tracking-widest uppercase text-sm"
            >
              {{ tag }}
            </span>
          </div>
        </section>

        <section v-if="content.type === 'article'" class="p-8 bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-[8px_8px_0px_#000] dark:shadow-term-glow space-y-6">
          <div class="flex items-center justify-between gap-4 border-b-4 border-black dark:border-term-muted pb-2">
            <h2 class="text-2xl font-black uppercase">正文</h2>
            <span class="text-xs font-black uppercase tracking-[0.25em] opacity-60">{{ content.contentFormat }}</span>
          </div>

          <article v-if="articleIsPlainText" class="whitespace-pre-wrap leading-8 text-base">{{ content.content }}</article>
          <article v-else class="article-content" v-html="renderedArticleHtml" />

          <div v-if="content.url" class="pt-4 border-t border-black dark:border-term-muted">
            <button @click="goWebsite" class="btn-primary text-lg h-14 px-10 rotate-1 hover:-translate-y-1 transition-all">
              查看文章来源 →
            </button>
          </div>
        </section>

        <div v-else class="flex flex-col sm:flex-row gap-4 mt-12 justify-center pt-8">
          <button @click="goWebsite" class="btn-primary text-xl h-16 px-12 rotate-1 hover:-translate-y-2 hover:shadow-[12px_12px_0px_0px_#000] active:translate-y-0 active:shadow-none transition-all">
            打开 {{ content.name }} 官网 →
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  font-weight: 900;
  margin: 1.2rem 0 0.75rem;
}

.article-content :deep(p),
.article-content :deep(li),
.article-content :deep(blockquote) {
  line-height: 1.9;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  padding-left: 1.5rem;
}

.article-content :deep(pre) {
  overflow-x: auto;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.08);
  border: 2px solid #111827;
}

.article-content :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.article-content :deep(blockquote) {
  border-left: 4px solid currentColor;
  padding-left: 1rem;
  opacity: 0.75;
}
</style>
