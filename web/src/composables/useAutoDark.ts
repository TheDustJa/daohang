import { ref, watch } from 'vue'

const STORAGE_KEY = 'nav_auto_dark'
const MODE_KEY = 'nav_auto_dark_mode'

export type AutoDarkMode = 'schedule' | 'system'

function load(): boolean {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'false')
  } catch {
    return false
  }
}

function loadMode(): AutoDarkMode {
  try {
    const m = localStorage.getItem(MODE_KEY)
    if (m === 'schedule' || m === 'system') return m
  } catch { /* ignore */ }
  return 'schedule'
}

const autoDark = ref(load())
const autoDarkMode = ref<AutoDarkMode>(loadMode())

watch(autoDark, (v) => localStorage.setItem(STORAGE_KEY, JSON.stringify(v)), { immediate: true })
watch(autoDarkMode, (v) => localStorage.setItem(MODE_KEY, v), { immediate: true })

function isNightTime(): boolean {
  const h = new Date().getHours()
  return h >= 22 || h < 6
}

function prefersDark(): boolean {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)')?.matches === true
}

export function useAutoDark() {
  const shouldBeDark = ref(false)
  const check = () => {
    if (!autoDark.value) {
      shouldBeDark.value = false
      return
    }
    if (autoDarkMode.value === 'system') {
      shouldBeDark.value = prefersDark()
    } else {
      shouldBeDark.value = isNightTime()
    }
  }
  return { autoDark, autoDarkMode, shouldBeDark, check, isNightTime, prefersDark }
}
