import { ref, watch } from 'vue'

const STORAGE_KEY = 'nav_link_new_tab'
function load(): boolean {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    return v === null ? true : JSON.parse(v) // 默认新窗口
  } catch {
    return true
  }
}

const openInNewTab = ref(load())

watch(openInNewTab, (val) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
}, { immediate: true })

export function useLinkOpenPref() {
  const toggle = () => {
    openInNewTab.value = !openInNewTab.value
  }
  return { openInNewTab, toggle }
}
