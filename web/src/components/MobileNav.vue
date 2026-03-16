<script setup lang="ts">
import { Home, FileText, Tag, Heart, Info } from 'lucide-vue-next'
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/articles', icon: FileText, label: '文章' },
  { path: '/tags', icon: Tag, label: '标签' },
  { path: '/favorites', icon: Heart, label: '收藏' },
  { path: '/about', icon: Info, label: '关于' },
]

const isActive = (path: string) => route.path === path
</script>

<template>
  <nav class="md:hidden fixed bottom-0 left-0 right-0 z-[90] bg-white dark:bg-black border-t-2 border-black dark:border-term-muted safe-area-bottom">
    <div class="flex items-center justify-around h-14">
      <router-link
        v-for="item in items"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center gap-0.5 py-1.5 px-3 transition-colors"
        :class="isActive(item.path) ? 'text-neo-accent dark:text-term-primary' : 'text-black/50 dark:text-term-muted'"
      >
        <component :is="item.icon" class="w-5 h-5" :stroke-width="isActive(item.path) ? 2.5 : 2" />
        <span class="text-[9px] font-bold uppercase">{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>
