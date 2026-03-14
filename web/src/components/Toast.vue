<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CheckCircle2, AlertCircle, XCircle, Info, X } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  id: string
  message: string
  type?: 'success' | 'warning' | 'error' | 'info'
  duration?: number
}>(), {
  type: 'info',
  duration: 3000
})

const emit = defineEmits(['close'])
const visible = ref(false)
const elRef = ref<HTMLElement | null>(null)



const startTimer = () => {
  if (props.duration > 0) {
    window.setTimeout(() => {
      close()
    }, props.duration)
  }
}

const close = () => {
  visible.value = false
  // allow animation to finish before destroying DOM
  setTimeout(() => {
    if (elRef.value && elRef.value.parentNode) {
      elRef.value.parentNode.removeChild(elRef.value)
    }
    emit('close')
  }, 300) 
}

onMounted(() => {
  // trick to trigger enter animation
  setTimeout(() => {
    visible.value = true
    startTimer()
  }, 10)
})

const getIcon = () => {
  switch (props.type) {
    case 'success': return CheckCircle2
    case 'error': return XCircle
    case 'warning': return AlertCircle
    default: return Info
  }
}

const getTypeClasses = () => {
  switch (props.type) {
    case 'success': return 'bg-white text-green-600 border-green-600 dark:bg-black dark:text-green-400 dark:border-green-400'
    case 'error': return 'bg-white text-red-600 border-red-600 dark:bg-black dark:text-red-400 dark:border-red-400'
    case 'warning': return 'bg-white text-yellow-600 border-yellow-600 dark:bg-black dark:text-yellow-400 dark:border-yellow-400'
    default: return 'bg-white text-black border-black dark:bg-black dark:text-term-primary dark:border-term-primary'
  }
}

defineExpose({
  close
})
</script>

<template>
  <div 
    ref="elRef"
    :class="[
      'fixed z-[9999] top-6 right-6 flex items-start gap-3 p-4 border-4 shadow-neo-sm transition-all duration-300 transform font-neo dark:font-term',
      getTypeClasses(),
      visible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
    ]"
    style="min-width: 300px; max-width: 400px;"
  >
    <component :is="getIcon()" class="w-6 h-6 shrink-0 mt-0.5" stroke-width="3" />
    <div class="flex-1">
      <p class="font-bold text-sm sm:text-base leading-snug">{{ message }}</p>
    </div>
    <button @click="close" class="shrink-0 opacity-50 hover:opacity-100 transition-opacity">
      <X class="w-5 h-5" stroke-width="3" />
    </button>
  </div>
</template>
