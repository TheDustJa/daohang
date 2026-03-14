<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Link2 } from 'lucide-vue-next'
import { fetchFriendLinks, type FriendLink } from '../api/sites'

const friendLinks = ref<FriendLink[]>([])

onMounted(async () => {
  try {
    friendLinks.value = await fetchFriendLinks()
  } catch {
    friendLinks.value = []
  }
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
        <div>© 2026 AI Navigation Pro-Max. All rights reserved.</div>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer" class="hover:underline flex items-center gap-1">
          <span>京 ICP 备 XXXXXX 号-1</span>
        </a>
      </div>
    </div>
  </footer>
</template>
