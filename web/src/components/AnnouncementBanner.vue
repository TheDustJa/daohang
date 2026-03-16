<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Megaphone, X } from 'lucide-vue-next'
import { fetchAnnouncements, type Announcement } from '../api/sites'

const announcements = ref<Announcement[]>([])
const dismissed = ref<Set<number>>(new Set())

onMounted(async () => {
  try {
    const stored = localStorage.getItem('nav_dismissed_ann')
    if (stored) dismissed.value = new Set(JSON.parse(stored))
    announcements.value = await fetchAnnouncements()
  } catch { /* ignore */ }
})

const visibleAnnouncements = () =>
  announcements.value.filter(a => !dismissed.value.has(a.id))

const dismiss = (id: number) => {
  dismissed.value.add(id)
  localStorage.setItem('nav_dismissed_ann', JSON.stringify([...dismissed.value]))
}

const typeStyles: Record<string, string> = {
  info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-800 text-blue-800 dark:text-blue-300',
  warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-800 text-yellow-800 dark:text-yellow-300',
  success: 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-800 text-green-800 dark:text-green-300',
}
</script>

<template>
  <div v-for="ann in visibleAnnouncements()" :key="ann.id" class="border-2 px-4 py-2.5 flex items-center gap-3 text-sm font-bold" :class="typeStyles[ann.type] || typeStyles.info">
    <Megaphone class="w-4 h-4 shrink-0" :stroke-width="2.5" />
    <span class="flex-1">{{ ann.title }}<template v-if="ann.content"> — {{ ann.content }}</template></span>
    <button @click="dismiss(ann.id)" class="shrink-0 opacity-50 hover:opacity-100 transition-opacity">
      <X class="w-4 h-4" :stroke-width="2.5" />
    </button>
  </div>
</template>
