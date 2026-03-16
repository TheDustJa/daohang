import { ref, watch } from 'vue'

const STORAGE_KEY = 'nav_no_image'
function load(): boolean {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'false')
  } catch {
    return false
  }
}

const noImageMode = ref(load())

watch(noImageMode, (val) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
}, { immediate: true })

export function useNoImage() {
  const toggleNoImage = () => {
    noImageMode.value = !noImageMode.value
  }
  return { noImageMode, toggleNoImage }
}
