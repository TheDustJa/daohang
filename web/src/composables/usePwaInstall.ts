import { ref, onMounted } from 'vue'

const INSTALL_DISMISSED_KEY = 'nav_pwa_install_dismissed'

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
}

export function usePwaInstall() {
  const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null)
  const canInstall = ref(false)
  const showBanner = ref(false)

  onMounted(() => {
    try {
      if (sessionStorage.getItem(INSTALL_DISMISSED_KEY)) return
      if (window.matchMedia('(display-mode: standalone)').matches) return
      if ((navigator as { standalone?: boolean }).standalone) return

      const handler = (e: Event) => {
        e.preventDefault()
        deferredPrompt.value = e as unknown as BeforeInstallPromptEvent
        canInstall.value = true
        showBanner.value = true
      }
      window.addEventListener('beforeinstallprompt', handler)
      return () => window.removeEventListener('beforeinstallprompt', handler)
    } catch { /* ignore */ }
  })

  const dismiss = () => {
    showBanner.value = false
    sessionStorage.setItem(INSTALL_DISMISSED_KEY, '1')
  }

  const install = async () => {
    if (!deferredPrompt.value) return
    try {
      await deferredPrompt.value.prompt()
      deferredPrompt.value = null
      canInstall.value = false
      showBanner.value = false
    } catch { /* ignore */ }
  }

  return { showBanner, canInstall, install, dismiss }
}
