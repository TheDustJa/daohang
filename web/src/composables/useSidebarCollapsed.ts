import { ref, watch } from 'vue'

const STORAGE_KEY = 'nav_sidebar_collapsed'
function load(): boolean {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'false')
  } catch {
    return false
  }
}

const collapsed = ref(load())
watch(collapsed, (v) => localStorage.setItem(STORAGE_KEY, JSON.stringify(v)), { immediate: true })

export function useSidebarCollapsed() {
  const toggle = () => { collapsed.value = !collapsed.value }
  return { collapsed, toggle }
}
