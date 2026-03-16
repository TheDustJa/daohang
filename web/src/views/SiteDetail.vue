<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import DOMPurify from 'dompurify'
import MarkdownIt from 'markdown-it'
import { Share2, Copy, Heart, Check, ThumbsUp, ThumbsDown, Flag, Maximize2, Minimize2, QrCode, Clock } from 'lucide-vue-next'
import { fetchSiteById, recordClick, voteContent, getVoteStatus, fetchRelatedSites, submitReport, type Site } from '../api/sites'
import { useFingerprint } from '../composables/useFingerprint'
import LayoutHeader from '../components/LayoutHeader.vue'
import { useHistory } from '../composables/useHistory'
import { useFavorites } from '../composables/useFavorites'
import { useSiteNote } from '../composables/useSiteNote'
import { Toast } from '../utils/toast'

const route = useRoute()
const router = useRouter()
const content = ref<Site | null>(null)
const isLoading = ref(true)
const copied = ref(false)
const articleFontSize = ref<'sm' | 'md' | 'lg'>('md')
const readingMode = ref(false)
const showReport = ref(false)
const showQr = ref(false)
const reportReason = ref('')
const fullscreenRead = ref(false)
let readTimerId: ReturnType<typeof setInterval> | null = null
const { getNote, setNote } = useSiteNote()
const likes = ref(0)
const dislikes = ref(0)
const userVote = ref<string | null>(null)
const relatedSites = ref<Site[]>([])
const fp = useFingerprint()
const { addToHistory } = useHistory()
const { isFavorite, toggleFavorite } = useFavorites()

const handleVote = async (type: 'like' | 'dislike') => {
  if (!content.value) return
  try {
    const result = await voteContent(contentType.value, contentId.value, fp, type)
    likes.value = result.likes
    dislikes.value = result.dislikes
    userVote.value = result.userVote
  } catch { /* ignore */ }
}

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  breaks: true
})

const contentType = computed(() => route.params.type === 'article' ? 'article' : 'site')
const contentId = computed(() => Number(route.params.id))

const readingTimeMin = computed(() => {
  if (content.value?.type !== 'article') return 0
  const body = content.value?.content || ''
  const len = body.replace(/\s/g, '').length
  return Math.max(1, Math.ceil(len / 300))
})

const renderedArticleHtml = computed(() => {
  if (!content.value || content.value.type !== 'article') return ''
  const body = content.value.content || ''
  if (!body.trim()) return ''

  let html: string
  if (content.value.contentFormat === 'markdown') {
    html = md.render(body)
  } else if (content.value.contentFormat === 'html') {
    html = body
  } else {
    return ''
  }
  html = DOMPurify.sanitize(html)
  return html.replace(/<a\s+/gi, '<a target="_blank" rel="noopener" ')
})

const articleIsPlainText = computed(() => content.value?.type === 'article' && content.value.contentFormat === 'text')

const shareContent = async () => {
  if (!content.value) return
  const shareData = {
    title: content.value.name,
    text: content.value.description,
    url: window.location.href
  }
  if (navigator.share) {
    try {
      await navigator.share(shareData)
    } catch { /* user cancelled */ }
  } else {
    await copyLink()
  }
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    copied.value = true
    Toast.success('链接已复制到剪贴板')
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    Toast.error('复制失败')
  }
}

const copyAsMarkdown = async () => {
  if (!content.value) return
  const link = content.value.url || window.location.href
  const text = `- [${content.value.name}](${link}) - ${content.value.description}`
  try {
    await navigator.clipboard.writeText(text)
    Toast.success('Markdown 已复制')
  } catch {
    Toast.error('复制失败')
  }
}

const copyAsMarkdownTable = async () => {
  if (!content.value) return
  const name = (content.value.name || '').replace(/\|/g, '｜')
  const url = (content.value.url || window.location.href).replace(/\|/g, '｜')
  const desc = (content.value.description || '').slice(0, 80).replace(/\|/g, '｜')
  const text = `| ${name} | ${url} | ${desc} |`
  try {
    await navigator.clipboard.writeText(text)
    Toast.success('表格行已复制')
  } catch {
    Toast.error('复制失败')
  }
}

const copyShareText = async () => {
  if (!content.value) return
  const text = `推荐一个 AI 工具：${content.value.name}\n${content.value.description}\n链接：${content.value.url || window.location.href}`
  try {
    await navigator.clipboard.writeText(text)
    Toast.success('分享文案已复制')
  } catch {
    Toast.error('复制失败')
  }
}

const toggleFullscreen = () => {
  fullscreenRead.value = !fullscreenRead.value
  if (fullscreenRead.value) {
    document.documentElement.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

const handleFullscreenChange = () => {
  if (!document.fullscreenElement) fullscreenRead.value = false
}

const shareToX = () => {
  if (!content.value) return
  const text = encodeURIComponent(`发现好工具：${content.value.name} ${content.value.url || window.location.href}`)
  window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank')
}

const submitReportAction = async () => {
  if (!content.value) return
  try {
    await submitReport(contentType.value, contentId.value, reportReason.value)
    Toast.success('举报已提交，我们会尽快处理')
    showReport.value = false
    reportReason.value = ''
  } catch {
    Toast.error('提交失败')
  }
}

onMounted(async () => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  content.value = await fetchSiteById(contentType.value, contentId.value) || null
  if (content.value?.type === 'article') {
    readTimerId = setInterval(() => {
      Toast.info('已阅读 20 分钟，记得休息一下哦 👀')
    }, 20 * 60 * 1000)
  }
  isLoading.value = false

  if (content.value) {
    addToHistory({
      id: content.value.id,
      name: content.value.name,
      type: (content.value.type || 'site') as 'site' | 'article',
      description: content.value.description,
      url: content.value.url
    })
    recordClick(contentType.value, contentId.value).catch(() => {})
    likes.value = content.value.likes ?? 0
    dislikes.value = content.value.dislikes ?? 0

    getVoteStatus(contentType.value, contentId.value, fp).then(r => {
      userVote.value = r.userVote
    }).catch(() => {})

    fetchRelatedSites(contentType.value, contentId.value, 6).then(r => {
      relatedSites.value = r
    }).catch(() => {})
  }

  if (content.value) {
    const isArticle = content.value.type === 'article'
    useHead({
      title: `${content.value.name} - AI 导航站`,
      meta: [
        { name: 'description', content: content.value.description },
        { property: 'og:title', content: `${content.value.name} - AI 导航站` },
        { property: 'og:description', content: content.value.description },
        { property: 'og:type', content: isArticle ? 'article' : 'website' }
      ],
      link: [
        { rel: 'canonical', href: window.location.href }
      ],
      script: [
        {
          type: 'application/ld+json',
          innerHTML: JSON.stringify(
            isArticle
              ? {
                  '@context': 'https://schema.org',
                  '@type': 'Article',
                  headline: content.value.name,
                  description: content.value.description,
                  datePublished: content.value.createdAt,
                  dateModified: content.value.updatedAt
                }
              : {
                  '@context': 'https://schema.org',
                  '@type': 'SoftwareApplication',
                  name: content.value.name,
                  description: content.value.description,
                  url: content.value.url,
                  applicationCategory: content.value.level1
                }
          )
        }
      ]
    })
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  if (readTimerId) clearInterval(readTimerId)
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

const qrUrl = computed(() => {
  const u = content.value?.url || window.location.href
  return `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(u)}`
})

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
      <!-- 面包屑 -->
      <nav class="mb-6 flex items-center gap-2 text-sm font-bold uppercase tracking-widest opacity-60">
        <router-link to="/" class="hover:opacity-100 transition-opacity">首页</router-link>
        <span>/</span>
        <span v-if="content">{{ content.level1 }} / {{ content.level2 }}</span>
        <span>/</span>
        <span class="opacity-100 truncate max-w-[200px]" v-if="content">{{ content.name }}</span>
      </nav>
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
            <img v-if="content.type === 'site' && content.url" :src="`https://www.google.com/s2/favicons?domain=${getDomain(content.url)}&sz=128`" :alt="`${content.name} 图标`" loading="lazy" @error="handleImageError" class="w-16 h-16 object-contain block z-10" />
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
            <div class="flex items-center gap-2 mt-3">
              <button
                @click="toggleFavorite(content!.id)"
                class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase transition-colors"
                :class="isFavorite(content!.id) ? 'bg-neo-accent dark:bg-[#ff3333] text-white border-neo-accent dark:border-[#ff3333]' : 'hover:bg-neo-secondary dark:hover:bg-term-muted'"
              >
                <Heart class="w-3.5 h-3.5" :stroke-width="2.5" :fill="isFavorite(content!.id) ? 'currentColor' : 'none'" />
                {{ isFavorite(content!.id) ? '已收藏' : '收藏' }}
              </button>
              <button
                @click="shareContent"
                class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors"
              >
                <Share2 class="w-3.5 h-3.5" :stroke-width="2.5" />
                分享
              </button>
              <button
                @click="copyLink"
                class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors"
              >
                <component :is="copied ? Check : Copy" class="w-3.5 h-3.5" :stroke-width="2.5" />
                {{ copied ? '已复制' : '复制链接' }}
              </button>
              <button
                @click="copyAsMarkdown"
                class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors"
                title="复制为 Markdown"
              >
                Markdown
              </button>
              <button @click="copyAsMarkdownTable" class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="复制为表格行">表格行</button>
              <button
                @click="copyShareText"
                class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors"
                title="复制分享文案"
              >
                分享文案
              </button>
              <button @click="shareToX" class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="分享到 X">X</button>
              <button @click="showQr = !showQr" class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors" title="二维码">
                <QrCode class="w-3.5 h-3.5" :stroke-width="2.5" />
                二维码
              </button>
              <button
                v-if="content.type === 'article'"
                @click="toggleFullscreen"
                class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors"
                title="全屏阅读"
              >
                <component :is="fullscreenRead ? Minimize2 : Maximize2" class="w-3.5 h-3.5" :stroke-width="2.5" />
              </button>
              <button
                @click="showReport = true"
                class="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black dark:border-term-muted text-xs font-bold uppercase hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors opacity-60 hover:opacity-100"
                title="举报"
              >
                <Flag class="w-3.5 h-3.5" :stroke-width="2.5" />
                举报
              </button>
            </div>
          </div>
        </header>

        <div v-if="showQr" class="p-4 bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-neo-sm inline-block">
          <img :src="qrUrl" alt="二维码" class="w-[150px] h-[150px]" />
        </div>

        <section class="p-8 bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-[8px_8px_0px_#000] dark:shadow-term-glow">
          <h2 class="text-2xl font-black uppercase mb-4 border-b-4 border-black dark:border-term-muted pb-2">概览</h2>
          <p class="font-bold text-lg leading-relaxed">{{ content.description }}</p>

          <div v-if="content" class="mt-4 p-3 border-2 border-black/10 dark:border-term-muted/30">
            <label class="text-xs font-black uppercase opacity-60 block mb-1">我的备注</label>
            <textarea
              :value="getNote(content!.id)"
              @input="(e) => setNote(content!.id, (e.target as HTMLTextAreaElement).value)"
              rows="2"
              placeholder="添加个人备注（仅保存在本地）"
              class="w-full text-sm p-2 border border-black/20 dark:border-term-muted bg-white dark:bg-black dark:text-term-primary outline-none resize-none"
            />
          </div>
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

        <section v-if="content.type === 'article'" class="p-8 bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-[8px_8px_0px_#000] dark:shadow-term-glow space-y-6" :class="{ 'reading-mode': readingMode, 'fixed inset-0 z-[80] overflow-y-auto': fullscreenRead }">
          <div class="flex items-center justify-between gap-4 border-b-4 border-black dark:border-term-muted pb-2 flex-wrap">
            <h2 class="text-2xl font-black uppercase">正文</h2>
            <span v-if="readingTimeMin > 0" class="flex items-center gap-1 text-sm font-bold opacity-60">
              <Clock class="w-4 h-4" :stroke-width="2" />
              约 {{ readingTimeMin }} 分钟
            </span>
            <div class="flex items-center gap-2">
              <span class="text-xs font-black uppercase tracking-[0.25em] opacity-60">{{ content.contentFormat }}</span>
              <button v-for="sz in (['sm', 'md', 'lg'] as const)" :key="sz" @click="articleFontSize = sz" class="p-1 border-2 text-[10px] font-bold" :class="articleFontSize === sz ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black' : ''">{{ sz === 'sm' ? '小' : sz === 'md' ? '中' : '大' }}</button>
              <button @click="readingMode = !readingMode" class="px-2 py-1 border-2 text-[10px] font-bold" title="护眼模式">护眼</button>
            </div>
          </div>

          <article v-if="articleIsPlainText" class="whitespace-pre-wrap leading-8" :class="{ 'text-sm': articleFontSize === 'sm', 'text-base': articleFontSize === 'md', 'text-lg': articleFontSize === 'lg' }">{{ content.content }}</article>
          <article v-else class="article-content" :class="{ 'article-sm': articleFontSize === 'sm', 'article-md': articleFontSize === 'md', 'article-lg': articleFontSize === 'lg' }" v-html="renderedArticleHtml" />

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

        <!-- Score Summary -->
        <div v-if="(likes + dislikes) > 0" class="text-center py-2 text-xs font-bold opacity-50">
          {{ likes }} 赞 / {{ dislikes }} 踩 · 有用率 {{ likes + dislikes > 0 ? Math.round((likes / (likes + dislikes)) * 100) : 0 }}%
        </div>

        <!-- Vote Section -->
        <div class="flex items-center justify-center gap-6 py-6 border-t-4 border-black dark:border-term-muted">
          <span class="text-sm font-bold uppercase opacity-50">觉得有用吗？</span>
          <button
            @click="handleVote('like')"
            class="flex items-center gap-1.5 px-4 py-2 border-2 font-bold text-sm transition-all"
            :class="userVote === 'like' ? 'bg-green-500 text-white border-green-600 scale-105' : 'border-black dark:border-term-muted hover:bg-green-50 dark:hover:bg-green-900/20'"
          >
            <ThumbsUp class="w-4 h-4" :stroke-width="2.5" />
            {{ likes }}
          </button>
          <button
            @click="handleVote('dislike')"
            class="flex items-center gap-1.5 px-4 py-2 border-2 font-bold text-sm transition-all"
            :class="userVote === 'dislike' ? 'bg-red-500 text-white border-red-600 scale-105' : 'border-black dark:border-term-muted hover:bg-red-50 dark:hover:bg-red-900/20'"
          >
            <ThumbsDown class="w-4 h-4" :stroke-width="2.5" />
            {{ dislikes }}
          </button>
        </div>

        <!-- Report Modal -->
        <div v-if="showReport" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60" @click.self="showReport = false">
          <div class="bg-white dark:bg-black border-4 border-black dark:border-term-muted p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-black uppercase mb-3">举报此内容</h3>
            <textarea v-model="reportReason" rows="3" placeholder="请说明举报原因（选填）" class="w-full border-2 border-black dark:border-term-muted p-2 text-sm bg-white dark:bg-black dark:text-term-primary outline-none resize-none mb-4" />
            <div class="flex gap-2">
              <button @click="submitReportAction" class="flex-1 btn-primary py-2">提交举报</button>
              <button @click="showReport = false" class="px-4 py-2 border-2 border-black dark:border-term-muted font-bold">取消</button>
            </div>
          </div>
        </div>

        <!-- Related Sites -->
        <section v-if="relatedSites.length > 0" class="mt-8">
          <h2 class="text-xl font-black uppercase tracking-tighter mb-4 border-b-4 border-black dark:border-term-muted pb-2">相关推荐</h2>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
            <router-link
              v-for="rs in relatedSites"
              :key="rs.id"
              :to="`/content/${rs.type || 'site'}/${rs.id}`"
              class="nav-card p-3 md:p-4 flex flex-col gap-2 group hover:-rotate-1"
            >
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 bg-neo-secondary dark:bg-black border-2 border-black dark:border-term-primary flex items-center justify-center -rotate-2 group-hover:rotate-0 transition-transform">
                  <span class="font-black text-sm dark:text-term-primary">{{ rs.name[0] }}</span>
                </div>
                <h3 class="text-sm font-black uppercase tracking-tighter truncate flex-1">{{ rs.name }}</h3>
              </div>
              <p class="text-[10px] md:text-xs font-bold text-black/60 dark:text-term-primary/60 line-clamp-2">{{ rs.description }}</p>
            </router-link>
          </div>
        </section>
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
  background: #1e293b;
  color: #e2e8f0;
  border: 2px solid #334155;
  border-radius: 4px;
  font-size: 0.875rem;
  line-height: 1.7;
}

.article-content :deep(code) {
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}

.article-content :deep(:not(pre) > code) {
  background: rgba(15, 23, 42, 0.08);
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 2px solid currentColor;
  padding: 0.5rem 0.75rem;
  text-align: left;
}

.article-content :deep(th) {
  font-weight: 900;
  text-transform: uppercase;
}

.article-content :deep(a) {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.article-content :deep(hr) {
  border: none;
  border-top: 3px solid currentColor;
  margin: 2rem 0;
  opacity: 0.2;
}

.article-sm :deep(p), .article-sm :deep(li) { font-size: 0.875rem; }
.article-lg :deep(p), .article-lg :deep(li) { font-size: 1.125rem; }
.reading-mode { filter: sepia(0.2) contrast(0.95); background-color: #f7f5f0 !important; }
.dark .reading-mode { background-color: #1a1a18 !important; filter: sepia(0.15) contrast(0.9); }

.article-content :deep(blockquote) {
  border-left: 4px solid currentColor;
  padding-left: 1rem;
  opacity: 0.75;
}
</style>
