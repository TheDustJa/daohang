<script setup lang="ts">
import { ref } from 'vue'
import { MessageCircle, X, Send } from 'lucide-vue-next'
import { Toast } from '../utils/toast'
import { submitFeedback } from '../api/sites'

const isOpen = ref(false)
const feedback = ref('')
const type = ref<'bug' | 'feature' | 'other'>('feature')
const sending = ref(false)

const submit = async () => {
  if (!feedback.value.trim()) {
    Toast.error('请输入反馈内容')
    return
  }
  sending.value = true
  try {
    await submitFeedback(type.value, feedback.value)
    Toast.success('感谢反馈！我们会尽快处理')
    feedback.value = ''
    isOpen.value = false
  } catch {
    Toast.error('发送失败，请稍后再试')
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div class="fixed bottom-[4.5rem] md:bottom-4 left-4 z-50">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-90 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-90 opacity-0"
    >
      <div v-if="isOpen" class="absolute bottom-14 left-0 w-72 bg-white dark:bg-black border-4 border-black dark:border-term-muted shadow-neo-md dark:shadow-term-glow p-4 mb-2">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-black uppercase dark:text-term-primary">意见反馈</h3>
          <button @click="isOpen = false" class="opacity-50 hover:opacity-100"><X class="w-4 h-4" :stroke-width="2.5" /></button>
        </div>
        <div class="flex gap-2 mb-3">
          <button v-for="t in (['feature', 'bug', 'other'] as const)" :key="t" @click="type = t"
            class="px-2 py-1 text-[10px] font-bold uppercase border-2 transition-colors"
            :class="type === t ? 'bg-neo-accent dark:bg-term-primary text-white dark:text-black border-black dark:border-term-primary' : 'border-black/20 dark:border-term-muted/50 opacity-60 hover:opacity-100'"
          >
            {{ t === 'feature' ? '功能建议' : t === 'bug' ? 'Bug 报告' : '其他' }}
          </button>
        </div>
        <textarea v-model="feedback" rows="3" placeholder="告诉我们你的想法..." class="w-full border-2 border-black dark:border-term-muted p-2 text-sm font-bold bg-white dark:bg-black dark:text-term-primary outline-none resize-none focus:border-neo-accent dark:focus:border-term-primary transition-colors" />
        <button @click="submit" :disabled="sending" class="mt-2 w-full h-9 bg-neo-accent dark:bg-term-primary text-white dark:text-black border-2 border-black dark:border-black font-bold text-xs uppercase flex items-center justify-center gap-1.5 hover:-translate-y-0.5 transition-all disabled:opacity-50">
          <Send class="w-3.5 h-3.5" :stroke-width="2.5" />
          {{ sending ? '发送中...' : '发送反馈' }}
        </button>
      </div>
    </transition>

    <button
      @click="isOpen = !isOpen"
      class="w-10 h-10 flex items-center justify-center bg-neo-accent dark:bg-term-primary text-white dark:text-black border-2 border-black dark:border-black shadow-neo-sm hover:-translate-y-0.5 transition-all"
    >
      <component :is="isOpen ? X : MessageCircle" class="w-5 h-5" :stroke-width="2.5" />
    </button>
  </div>
</template>
