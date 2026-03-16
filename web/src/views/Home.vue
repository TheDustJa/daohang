<script setup lang="ts">
import { onMounted } from 'vue'
import { useHead } from '@unhead/vue'
import { useNavigationStore } from '../store/navigation'
import { useSidebarCollapsed } from '../composables/useSidebarCollapsed'
import LayoutHeader from '../components/LayoutHeader.vue'
import Sidebar from '../components/Sidebar.vue'
import ContentArea from '../components/ContentArea.vue'
import AnnouncementBanner from '../components/AnnouncementBanner.vue'

const store = useNavigationStore()
const { collapsed: sidebarCollapsed, toggle: toggleSidebar } = useSidebarCollapsed()

useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: 'AI 导航站',
        url: window.location.origin,
        description: '收录优质 AI 工具、平台与站内文章，一站式 AI 资源导航。',
        potentialAction: {
          '@type': 'SearchAction',
          target: `${window.location.origin}/?q={search_term_string}`,
          'query-input': 'required name=search_term_string'
        }
      })
    }
  ]
})

onMounted(async () => {
  await store.loadSites()
})
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <AnnouncementBanner />
    <!-- Top Level 1 Menu & Search -->
    <LayoutHeader class="shrink-0 z-20" />
    
    <div class="flex-1 flex flex-col md:flex-row overflow-hidden relative z-10">
      <!-- Left Level 2 Sidebar -->
      <aside v-show="!sidebarCollapsed" class="w-full md:w-64 md:shrink-0 border-b-4 md:border-b-0 md:border-r-4 border-black dark:border-term-muted overflow-y-hidden md:overflow-y-auto transition-all">
        <Sidebar @collapse="toggleSidebar" />
      </aside>
      
      <!-- Right Level 3 & Content Area -->
      <ContentArea class="flex-1 overflow-y-auto bg-neo-bg/50 dark:bg-transparent relative" :sidebar-collapsed="sidebarCollapsed" @toggle-sidebar="toggleSidebar" />
    </div>
  </div>
</template>
