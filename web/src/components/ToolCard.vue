<script setup lang="ts">
import type { Site } from '../api/sites'
import { ArrowUpRight, FileText } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const props = defineProps<{
  site: Site
}>()

const router = useRouter()

const navigateToDetail = () => {
  router.push(`/content/${props.site.type || 'site'}/${props.site.id}`)
}

const openSite = (url: string) => {
  if (!url) return
  window.open(url, '_blank')
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
  <article
    @click="navigateToDetail"
    class="nav-card relative p-2 md:p-3 lg:p-4 flex flex-col gap-1.5 md:gap-3 cursor-pointer group hover:-rotate-1"
  >
    <div v-if="site.isRecommended"
         class="absolute -top-2.5 -right-2.5 sm:-top-3 sm:-right-3 md:-top-4 md:-right-4 rotate-[6deg] px-2 py-1 md:px-3 md:py-1.5 bg-neo-accent dark:bg-[#ff3333] text-white dark:text-black text-[10px] sm:text-xs md:text-sm font-black uppercase tracking-widest leading-none border-2 md:border-[3px] border-black shadow-[2px_2px_0px_0px_#000] md:shadow-[4px_4px_0px_0px_#000] z-20 transition-transform group-hover:rotate-[12deg] group-hover:scale-110">
      推荐
    </div>

    <div class="flex items-start justify-between gap-2">
      <div class="w-8 h-8 md:w-12 md:h-12 lg:w-14 lg:h-14 bg-neo-secondary dark:bg-black border-[1.5px] md:border-2 lg:border-[3px] border-black dark:border-term-primary flex items-center justify-center -rotate-2 group-hover:rotate-0 transition-transform overflow-hidden relative">
        <img v-if="site.type === 'site' && site.url" :src="`https://www.google.com/s2/favicons?domain=${getDomain(site.url)}&sz=128`" @error="handleImageError" class="w-5 h-5 md:w-7 md:h-7 lg:w-8 lg:h-8 object-contain block z-10" />
        <span class="font-black text-base md:text-lg lg:text-xl dark:text-term-primary absolute">{{ site.logo?.[0] || site.name[0] }}</span>
      </div>

      <div class="flex items-center gap-2">
        <span class="px-2 py-1 border border-black dark:border-term-muted text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em]">
          {{ site.type === 'article' ? 'ARTICLE' : 'SITE' }}
        </span>
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
      <h3 class="text-[13px] sm:text-sm md:text-base lg:text-xl font-black uppercase tracking-tighter mb-0.5 line-clamp-1 truncate">{{ site.name }}</h3>
      <p class="text-[10px] sm:text-[11px] md:text-xs lg:text-sm font-bold text-black/70 dark:text-term-primary/70 line-clamp-4 leading-snug">{{ site.description }}</p>
    </div>

    <div class="flex flex-wrap gap-2 mt-2">
      <span
        v-for="tag in site.tags.slice(0, 2)"
        :key="tag"
        class="px-1 py-px md:px-1.5 md:py-0.5 lg:px-2 lg:py-1 bg-neo-muted/30 dark:bg-black border md:border-2 border-black dark:border-term-muted text-[9px] md:text-[10px] lg:text-xs font-black uppercase tracking-widest whitespace-nowrap"
      >
        {{ tag }}
      </span>
    </div>
  </article>
</template>
