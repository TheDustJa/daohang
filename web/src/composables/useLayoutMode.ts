import { ref, watch } from 'vue'

export type LayoutMode = 'grid' | 'list' | 'compact'

const KEY = 'nav_layout_mode'

function load(): LayoutMode {
  return (localStorage.getItem(KEY) as LayoutMode) || 'grid'
}

const layoutMode = ref<LayoutMode>(load())

watch(layoutMode, (val) => {
  localStorage.setItem(KEY, val)
})

export function useLayoutMode() {
  const setMode = (mode: LayoutMode) => {
    layoutMode.value = mode
  }

  return { layoutMode, setMode }
}
