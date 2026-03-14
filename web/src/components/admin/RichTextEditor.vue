<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Editor from '@toast-ui/editor'
import '@toast-ui/editor/dist/toastui-editor.css'

const props = withDefaults(defineProps<{
  modelValue: string
  format?: 'html' | 'markdown'
  placeholder?: string
}>(), {
  format: 'markdown',
  placeholder: 'Start writing...'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const containerRef = ref<HTMLElement | null>(null)
const editorRef = ref<Editor | null>(null)

const editorMode = computed(() => props.format === 'html' ? 'wysiwyg' : 'markdown')

const getEditorValue = () => {
  if (!editorRef.value) return ''
  return props.format === 'html' ? editorRef.value.getHTML() : editorRef.value.getMarkdown()
}

const syncFromProps = (value: string) => {
  if (!editorRef.value) return
  if (getEditorValue() === value) return
  if (props.format === 'html') {
    editorRef.value.setHTML(value || '')
    editorRef.value.changeMode('wysiwyg', true)
    return
  }
  editorRef.value.setMarkdown(value || '', false)
}

const initEditor = () => {
  if (!containerRef.value) return
  editorRef.value?.destroy()
  editorRef.value = new Editor({
    el: containerRef.value,
    height: '420px',
    initialEditType: editorMode.value,
    initialValue: props.format === 'markdown' ? (props.modelValue || '') : '',
    previewStyle: 'vertical',
    usageStatistics: false,
    hideModeSwitch: false,
    placeholder: props.placeholder,
    events: {
      change: () => emit('update:modelValue', getEditorValue())
    }
  })
  if (props.format === 'html' && props.modelValue) {
    editorRef.value.setHTML(props.modelValue)
  }
}

onMounted(() => {
  initEditor()
})

onBeforeUnmount(() => {
  editorRef.value?.destroy()
  editorRef.value = null
})

watch(() => props.modelValue, (value) => {
  syncFromProps(value)
})

watch(() => props.format, () => {
  const currentValue = getEditorValue() || props.modelValue || ''
  emit('update:modelValue', currentValue)
  initEditor()
})
</script>

<template>
  <div class="rich-editor-shell">
    <div ref="containerRef" />
  </div>
</template>

<style>
.rich-editor-shell .toastui-editor-defaultUI {
  border: 0;
  border-radius: 0;
}

.rich-editor-shell .toastui-editor-toolbar {
  border-bottom: 1px solid #d1d5db;
  background: #f8fafc;
}

.rich-editor-shell .toastui-editor-contents {
  font-family: inherit;
  font-size: 0.98rem;
}

.dark .rich-editor-shell .toastui-editor-toolbar {
  background: #050505;
  border-bottom-color: #2f2f2f;
}

.dark .rich-editor-shell .toastui-editor-defaultUI,
.dark .rich-editor-shell .toastui-editor-md-container,
.dark .rich-editor-shell .toastui-editor-ww-container,
.dark .rich-editor-shell .toastui-editor-mode-switch,
.dark .rich-editor-shell .toastui-editor-popup {
  background: #050505;
  color: #f3f4f6;
  border-color: #2f2f2f;
}

.dark .rich-editor-shell .toastui-editor-toolbar-icons {
  filter: invert(1);
}
</style>
