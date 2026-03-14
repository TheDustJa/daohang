import { createVNode, render, type VNode } from 'vue'
import ToastComponent from '../components/Toast.vue'

export type ToastType = 'success' | 'warning' | 'error' | 'info'

interface ToastOptions {
  message: string
  type?: ToastType
  duration?: number
}

let seed = 1
const instances: VNode[] = []

const showMessage = (options: ToastOptions | string) => {
  if (typeof options === 'string') {
    options = { message: options }
  }

  const id = `toast_${seed++}`
  const container = document.createElement('div')
  
  // Create props
  const props = {
    ...options,
    id,
    onClose: () => {
      closeMessage(id)
    }
  }

  const vnode = createVNode(ToastComponent, props)
  render(vnode, container)

  // Mount to body
  if (container.firstElementChild) {
    document.body.appendChild(container.firstElementChild)
  }

  instances.push(vnode)
}

const closeMessage = (id: string) => {
  const idx = instances.findIndex(vm => vm.props?.id === id)
  if (idx === -1) return

  // In a full implementation we would adjust the vertical offset of other toasts here
  instances.splice(idx, 1)
  
  // Cleanup is handled by the component's after-leave hook
}

export const Toast = {
  success(message: string) { showMessage({ message, type: 'success' }) },
  warning(message: string) { showMessage({ message, type: 'warning' }) },
  error(message: string) { showMessage({ message, type: 'error' }) },
  info(message: string) { showMessage({ message, type: 'info' }) }
}
