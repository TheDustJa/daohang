<script setup lang="ts">
import type { Site } from '../api/sites'
import { ArrowUpRight, FileText, Heart, Copy, Check, MousePointerClick } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'
import { useFavorites } from '../composables/useFavorites'
import { useNoImage } from '../composables/useNoImage'
import { useLinkOpenPref } from '../composables/useLinkOpenPref'
import { useNavigationStore } from '../store/navigation'
import { useCardFontSize } from '../composables/useCardFontSize'
import { Toast } from '../utils/toast'

const props = withDefaults(defineProps<{
  site: Site
  index?: number
  layout?: 'grid' | 'list' | 'compact'
  highlight?: string
}>(), { highlight: '' })

const router = useRouter()
const imgLoaded = ref(false)
const imgFailed = ref(false)
const copied = ref(false)
const descExpanded = ref(false)
const store = useNavigationStore()
const { cardFontSize } = useCardFontSize()
const { isFavorite, toggleFavorite } = useFavorites()
const { noImageMode } = useNoImage()
const { openInNewTab } = useLinkOpenPref()

const isFav = computed(() => isFavorite(props.site.id))

const handleFavorite = () => {
  toggleFavorite(props.site.id)
}

const navigateToDetail = () => {
  router.push(`/content/${props.site.type || 'site'}/${props.site.id}`)
}

const openSite = (url: string) => {
  if (!url) return
  if (openInNewTab.value) {
    window.open(url, '_blank')
  } else {
    window.location.href = url
  }
}

const copyUrl = async (e: Event) => {
  e.stopPropagation()
  if (!props.site.url) return
  try {
    await navigator.clipboard.writeText(props.site.url)
    copied.value = true
    Toast.success('链接已复制')
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    Toast.error('复制失败')
  }
}

const copyDesc = async (e: Event) => {
  e.stopPropagation()
  const text = props.site.description || props.site.name
  try {
    await navigator.clipboard.writeText(text)
    Toast.success('描述已复制')
  } catch {
    Toast.error('复制失败')
  }
}

const handleImageError = () => {
  imgFailed.value = true
}

const handleImageLoad = () => {
  imgLoaded.value = true
}

const getDomain = (url: string) => {
  try {
    return new URL(url).hostname
  } catch {
    return ''
  }
}

const animDelay = `${(props.index ?? 0) % 12 * 0.04}s`
const showImg = computed(() => !noImageMode.value && !imgFailed.value)

const isNew = computed(() => {
  const d = props.site.updatedAt || props.site.createdAt || ''
  if (!d) return false
  const diff = Date.now() - new Date(d).getTime()
  return diff < 7 * 24 * 60 * 60 * 1000
})
const isHot = computed(() => (props.site.clickCount ?? 0) >= 100)
const descLong = computed(() => (props.site.description || '').length > 60)

const highlightText = (text: string) => {
  const q = (props.highlight || '').trim()
  if (!q || !text) return text
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(re, '<mark class="bg-yellow-200 dark:bg-yellow-900/50">$1</mark>')
}
</script>

<template>
  <!-- Compact Layout -->
  <article
    v-if="layout === 'compact'"
    @click="navigateToDetail"
    class="nav-card card-animate-in p-2 flex flex-col items-center gap-1 cursor-pointer group hover:-translate-y-0.5 text-center"
    :style="{ animationDelay: animDelay }"
  >
    <div class="w-8 h-8 bg-neo-secondary dark:bg-black border-[1.5px] border-black dark:border-term-primary flex items-center justify-center overflow-hidden relative">
      <img v-if="site.type === 'site' && site.url && showImg" :src="`https://www.google.com/s2/favicons?domain=${getDomain(site.url)}&sz=64`" :alt="site.name" loading="lazy" @error="handleImageError" @load="handleImageLoad" class="w-5 h-5 object-contain z-10" :class="imgLoaded ? 'opacity-100' : 'opacity-0'" />
      <span class="font-black text-xs dark:text-term-primary absolute">{{ site.name[0] }}</span>
    </div>
    <span class="text-[9px] font-bold truncate w-full leading-tight">{{ site.name }}</span>
  </article>

  <!-- Default/List Layout -->
  <article
    v-else
    @click="navigateToDetail"
    class="nav-card card-animate-in relative cursor-pointer group"
    :class="layout === 'list' ? 'p-3 md:p-4 flex flex-row items-center gap-3 md:gap-4 hover:-translate-y-0.5' : 'p-2 md:p-3 lg:p-4 flex flex-col gap-1.5 md:gap-3 hover:-rotate-1'"
    :style="{ animationDelay: animDelay }"
  >
    <div v-if="site.isRecommended"
         class="absolute -top-2.5 -right-2.5 sm:-top-3 sm:-right-3 md:-top-4 md:-right-4 rotate-[6deg] px-2 py-1 md:px-3 md:py-1.5 bg-neo-accent dark:bg-[#ff3333] text-white dark:text-black text-[10px] sm:text-xs md:text-sm font-black uppercase tracking-widest leading-none border-2 md:border-[3px] border-black shadow-[2px_2px_0px_0px_#000] md:shadow-[4px_4px_0px_0px_#000] z-20 transition-transform group-hover:rotate-[12deg] group-hover:scale-110">
      推荐
    </div>
    <span v-if="isNew" class="absolute -top-1 -left-1 px-1.5 py-0.5 bg-green-500 text-white text-[9px] font-black border border-black z-20">NEW</span>
    <span v-if="isHot && !site.isRecommended" class="absolute -top-1 -right-1 px-1.5 py-0.5 bg-orange-500 text-white text-[9px] font-black border border-black z-20">HOT</span>

    <div class="flex items-start justify-between gap-2">
      <div class="w-8 h-8 md:w-12 md:h-12 lg:w-14 lg:h-14 bg-neo-secondary dark:bg-black border-[1.5px] md:border-2 lg:border-[3px] border-black dark:border-term-primary flex items-center justify-center -rotate-2 group-hover:rotate-0 transition-transform overflow-hidden relative">
        <img
          v-if="site.type === 'site' && site.url && showImg"
          :src="`https://www.google.com/s2/favicons?domain=${getDomain(site.url)}&sz=128`"
          :alt="`${site.name} 图标`"
          loading="lazy"
          decoding="async"
          @error="handleImageError"
          @load="handleImageLoad"
          class="w-5 h-5 md:w-7 md:h-7 lg:w-8 lg:h-8 object-contain z-10 transition-opacity duration-300"
          :class="imgLoaded ? 'opacity-100' : 'opacity-0'"
        />
        <span class="font-black text-base md:text-lg lg:text-xl dark:text-term-primary absolute">{{ site.logo?.[0] || site.name[0] }}</span>
      </div>

      <div class="flex items-center gap-1">
        <span class="px-2 py-1 border border-black dark:border-term-muted text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em]">
          {{ site.type === 'article' ? 'ARTICLE' : 'SITE' }}
        </span>
        <button
          v-if="site.url"
          @click.stop="copyUrl"
          class="opacity-0 group-hover:opacity-100 transition-opacity p-1 md:p-2 h-8 w-8 md:h-10 md:w-10 flex items-center justify-center border-2 border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted hidden sm:flex"
          title="复制链接"
        >
          <component :is="copied ? Check : Copy" class="w-4 h-4 dark:text-term-primary" :stroke-width="2.5" />
        </button>
        <button
          v-if="site.type === 'site' && site.url"
          @click.stop="openSite(site.url)"
          class="opacity-0 group-hover:opacity-100 transition-opacity btn-primary p-1 md:p-2 h-8 w-8 md:h-10 md:w-10 flex items-center justify-center hidden sm:flex"
        >
          <ArrowUpRight class="w-4 h-4 md:w-5 md:h-5 dark:text-black" :stroke-width="3" />
        </button>
        <div v-else class="hidden sm:flex h-8 w-8 md:h-10 md:w-10 items-center justify-center border-2 border-black dark:border-term-muted bg-white dark:bg-black">
          <FileText class="w-4 h-4 md:w-5 md:h-5" :stroke-width="2.5" />
        </div>
      </div>
    </div>

    <div class="flex-1">
      <h3
        class="font-black uppercase tracking-tighter mb-0.5 line-clamp-1 truncate"
        :class="cardFontSize === 'sm' ? 'text-[11px] sm:text-xs md:text-sm' : cardFontSize === 'lg' ? 'text-base sm:text-lg md:text-xl lg:text-2xl' : 'text-[13px] sm:text-sm md:text-base lg:text-xl'"
        v-html="highlight ? highlightText(site.name) : site.name"
      ></h3>
      <p
        class="font-bold text-black/70 dark:text-term-primary/70 leading-snug"
        :class="[descExpanded ? '' : 'line-clamp-4', cardFontSize === 'sm' ? 'text-[9px] sm:text-[10px] md:text-xs' : cardFontSize === 'lg' ? 'text-xs sm:text-sm md:text-base lg:text-lg' : 'text-[10px] sm:text-[11px] md:text-xs lg:text-sm']"
        v-html="highlight ? highlightText(site.description) : site.description"
      ></p>
      <button v-if="descLong && !descExpanded" @click.stop="descExpanded = true" class="text-[9px] font-bold uppercase opacity-50 hover:opacity-100 self-start mt-0.5">展开</button>
    </div>

    <div class="flex items-center justify-between mt-2">
      <div class="flex flex-wrap gap-2 items-center">
        <span v-if="(site.clickCount ?? 0) > 0" class="flex items-center gap-0.5 text-[9px] opacity-50" title="点击量">
          <MousePointerClick class="w-3 h-3" :stroke-width="2" />
          {{ site.clickCount }}
        </span>
        <span
          v-for="tag in site.tags.slice(0, 2)"
          :key="tag"
          @click.stop="store.activeTag = store.activeTag === tag ? '' : tag"
          class="px-1 py-px md:px-1.5 md:py-0.5 lg:px-2 lg:py-1 bg-neo-muted/30 dark:bg-black border md:border-2 border-black dark:border-term-muted text-[9px] md:text-[10px] lg:text-xs font-black uppercase tracking-widest whitespace-nowrap cursor-pointer hover:bg-neo-secondary dark:hover:bg-term-muted transition-colors"
          :class="{ 'ring-2 ring-neo-accent dark:ring-term-primary': store.activeTag === tag }"
        >
          {{ tag }}
        </span>
      </div>
      <button
        @click.stop="copyDesc"
        class="opacity-0 group-hover:opacity-100 p-1 transition-opacity shrink-0"
        title="复制描述"
      >
        <Copy class="w-3 h-3" :stroke-width="2.5" />
      </button>
      <button
        @click.stop="handleFavorite"
        class="p-1 transition-all duration-200 hover:scale-110 shrink-0"
        :title="isFav ? '取消收藏' : '收藏'"
      >
        <Heart
          class="w-3.5 h-3.5 md:w-4 md:h-4"
          :stroke-width="2.5"
          :class="isFav ? 'text-neo-accent dark:text-[#ff3333] fill-current' : 'text-black/30 dark:text-term-muted'"
        />
      </button>
    </div>
  </article>
</template>
