<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Tag } from 'lucide-vue-next'
import LayoutHeader from '../components/LayoutHeader.vue'
import { fetchAllTags, type TagInfo } from '../api/sites'
import { useNavigationStore } from '../store/navigation'
import { useRouter } from 'vue-router'

const tags = ref<TagInfo[]>([])
const store = useNavigationStore()
const router = useRouter()

onMounted(async () => {
  try {
    tags.value = await fetchAllTags()
  } catch { /* ignore */ }
})

const getSize = (count: number) => {
  const max = Math.max(...tags.value.map(t => t.count), 1)
  const ratio = count / max
  if (ratio > 0.7) return 'text-2xl md:text-3xl'
  if (ratio > 0.4) return 'text-lg md:text-xl'
  if (ratio > 0.2) return 'text-base md:text-lg'
  return 'text-sm'
}

const searchByTag = (tag: string) => {
  store.$patch({ searchQuery: tag })
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <LayoutHeader class="shrink-0 relative z-20" />
    <main class="flex-1 container mx-auto max-w-4xl py-8 md:py-12 px-4 md:px-6">
      <div class="flex items-center gap-3 mb-8">
        <Tag class="w-6 h-6 md:w-8 md:h-8" :stroke-width="2.5" />
        <h1 class="text-2xl md:text-4xl font-black uppercase tracking-tighter dark:text-term-primary">标签云</h1>
        <span class="text-sm font-bold opacity-50 dark:text-term-secondary">{{ tags.length }} 个标签</span>
      </div>

      <div v-if="tags.length === 0" class="text-center py-20 opacity-50">
        <Tag class="w-16 h-16 mx-auto mb-4" :stroke-width="1.5" />
        <h2 class="text-xl font-black uppercase">暂无标签数据</h2>
      </div>

      <div v-else class="flex flex-wrap gap-3 md:gap-4 items-center justify-center py-8">
        <button
          v-for="tag in tags"
          :key="tag.name"
          @click="searchByTag(tag.name)"
          :class="getSize(tag.count)"
          class="font-black uppercase tracking-wider px-3 py-1.5 md:px-4 md:py-2 border-2 border-black dark:border-term-muted hover:bg-neo-accent hover:text-white dark:hover:bg-term-primary dark:hover:text-black transition-all cursor-pointer hover:-translate-y-0.5 hover:shadow-neo-sm dark:hover:shadow-term-glow"
        >
          {{ tag.name }}
          <sup class="text-[9px] ml-0.5 opacity-50">{{ tag.count }}</sup>
        </button>
      </div>
    </main>
  </div>
</template>
