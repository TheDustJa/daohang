<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CalendarCheck, Flame, Star } from 'lucide-vue-next'
import { doCheckin, getCheckinStatus } from '../api/sites'
import { useFingerprint } from '../composables/useFingerprint'
import { Toast } from '../utils/toast'

const fp = useFingerprint()
const checkedIn = ref(false)
const streak = ref(0)
const totalPoints = ref(0)
const showPanel = ref(false)
const loading = ref(false)

onMounted(async () => {
  try {
    const status = await getCheckinStatus(fp)
    checkedIn.value = status.checkedInToday
    streak.value = status.streak
    totalPoints.value = status.totalPoints
  } catch { /* ignore */ }
})

const handleCheckin = async () => {
  if (checkedIn.value || loading.value) return
  loading.value = true
  try {
    const result = await doCheckin(fp)
    checkedIn.value = true
    streak.value = result.streak
    totalPoints.value = result.totalPoints
    Toast.success(`签到成功！+${result.pointsEarned} 积分${result.streak > 1 ? ` | 连续 ${result.streak} 天` : ''}`)
  } catch {
    Toast.error('签到失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="relative">
    <button
      @click="showPanel = !showPanel"
      class="w-10 h-10 flex items-center justify-center border-[3px] md:border-4 bg-white dark:bg-black transition-colors shadow-neo-sm active:translate-y-1 active:translate-x-1 active:shadow-none"
      :class="checkedIn ? 'border-neo-accent dark:border-[#33ff00] text-neo-accent dark:text-[#33ff00]' : 'border-black dark:border-term-muted hover:bg-neo-secondary dark:hover:bg-term-muted'"
      title="每日签到"
    >
      <CalendarCheck class="w-4 h-4" :stroke-width="3" />
    </button>

    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="showPanel"
        class="absolute top-12 right-0 w-56 bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-neo-md dark:shadow-term-glow z-50 p-4"
      >
        <h3 class="text-sm font-black uppercase tracking-widest mb-3 dark:text-term-primary">每日签到</h3>
        <div class="space-y-2 mb-4">
          <div class="flex items-center gap-2 text-xs font-bold">
            <Flame class="w-3.5 h-3.5 text-neo-accent" :stroke-width="2.5" />
            <span>连续签到：{{ streak }} 天</span>
          </div>
          <div class="flex items-center gap-2 text-xs font-bold">
            <Star class="w-3.5 h-3.5 text-neo-secondary" :stroke-width="2.5" />
            <span>累计积分：{{ totalPoints }}</span>
          </div>
        </div>
        <button
          @click="handleCheckin"
          :disabled="checkedIn || loading"
          class="w-full h-10 font-black uppercase text-xs tracking-widest transition-all"
          :class="checkedIn
            ? 'bg-neo-secondary/50 dark:bg-term-muted/50 border-2 border-black/20 dark:border-term-muted cursor-default opacity-70'
            : 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-2 border-black dark:border-black hover:-translate-y-0.5 shadow-neo-sm active:translate-y-0.5 active:shadow-none'"
        >
          {{ checkedIn ? '✓ 今日已签到' : loading ? '签到中...' : '立即签到' }}
        </button>
      </div>
    </transition>
  </div>
</template>
