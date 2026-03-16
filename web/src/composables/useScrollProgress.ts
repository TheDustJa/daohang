import { ref } from 'vue'

export const globalScrollProgress = ref(0)

export function useScrollProgress() {
  const reportProgress = (percent: number) => {
    globalScrollProgress.value = percent
  }
  return { globalScrollProgress, reportProgress }
}
