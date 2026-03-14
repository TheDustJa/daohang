<script setup lang="ts">
import { onMounted } from 'vue'
import { useNavigationStore } from '../store/navigation'
import LayoutHeader from '../components/LayoutHeader.vue'
import Sidebar from '../components/Sidebar.vue'
import ContentArea from '../components/ContentArea.vue'

const store = useNavigationStore()

onMounted(async () => {
  await store.loadSites()
})
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <!-- Top Level 1 Menu & Search -->
    <LayoutHeader class="shrink-0 z-20" />
    
    <div class="flex-1 flex flex-col md:flex-row overflow-hidden relative z-10">
      <!-- Left Level 2 Sidebar -->
      <Sidebar class="w-full md:w-64 md:shrink-0 border-b-4 md:border-b-0 md:border-r-4 border-black dark:border-term-muted overflow-y-hidden md:overflow-y-auto" />
      
      <!-- Right Level 3 & Content Area -->
      <ContentArea class="flex-1 overflow-y-auto bg-neo-bg/50 dark:bg-transparent relative" />
    </div>
  </div>
</template>
