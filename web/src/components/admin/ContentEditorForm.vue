<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import { Toast } from '../../utils/toast'
import RichTextEditor from './RichTextEditor.vue'
import { createAdminSite, fetchAdminCategoryOptions, type CategoryOptions, type ContentFormat, type ContentType } from '../../api/sites'

const props = withDefaults(defineProps<{
  title?: string
  description?: string
  submitLabel?: string
  cardClass?: string
}>(), {
  title: '发布内容',
  description: '新增导航站点或文章内容，并设置分类、推荐位与排序。',
  submitLabel: '保存并发布',
  cardClass: ''
})

const CUSTOM_OPTION_VALUE = '__custom__'

type EditorForm = {
  type: ContentType
  name: string
  url: string
  level1: string
  level2: string
  level3: string
  description: string
  content: string
  contentFormat: ContentFormat
  isRecommended: boolean
  sortOrder: number
}

const formData = ref<EditorForm>({
  type: 'site',
  name: '',
  url: '',
  level1: '',
  level2: '',
  level3: '',
  description: '',
  content: '',
  contentFormat: 'markdown',
  isRecommended: false,
  sortOrder: 0
})

const isSubmitting = ref(false)
const isCustomLevel1 = ref(false)
const isCustomLevel2 = ref(false)
const categoryOptions = ref<CategoryOptions>({
  level1Options: [],
  level2Options: [],
  level2ByLevel1: {}
})

const availableLevel2Options = computed(() => {
  return categoryOptions.value.level2ByLevel1[formData.value.level1 || ''] || []
})

const richEditorFormat = computed<'html' | 'markdown'>(() => (
  formData.value.contentFormat === 'html' ? 'html' : 'markdown'
))

watch(() => formData.value.type, (type) => {
  if (type === 'article' && !formData.value.contentFormat) {
    formData.value.contentFormat = 'markdown'
  }
})

onMounted(async () => {
  try {
    categoryOptions.value = await fetchAdminCategoryOptions()
    if (!formData.value.level1) {
      formData.value.level1 = categoryOptions.value.level1Options[0] || ''
    }
  } catch {
    // manual category input still works
  }
})

const resetForm = () => {
  formData.value = {
    type: formData.value.type || 'site',
    name: '',
    url: '',
    level1: categoryOptions.value.level1Options[0] || '',
    level2: '',
    level3: '',
    description: '',
    content: '',
    contentFormat: 'markdown',
    isRecommended: false,
    sortOrder: 0
  }
  isCustomLevel1.value = false
  isCustomLevel2.value = false
}

const handleLevel1Select = (value: string) => {
  if (value === CUSTOM_OPTION_VALUE) {
    isCustomLevel1.value = true
    formData.value.level1 = ''
    formData.value.level2 = ''
    isCustomLevel2.value = false
    return
  }

  isCustomLevel1.value = false
  formData.value.level1 = value
  if (!availableLevel2Options.value.includes(formData.value.level2 || '')) {
    formData.value.level2 = ''
  }
  isCustomLevel2.value = false
}

const handleLevel2Select = (value: string) => {
  if (value === CUSTOM_OPTION_VALUE) {
    isCustomLevel2.value = true
    formData.value.level2 = ''
    return
  }

  isCustomLevel2.value = false
  formData.value.level2 = value
}

const validateForm = () => {
  if (!formData.value.name?.trim()) {
    Toast.error('请先填写标题或名称')
    return false
  }

  if (!formData.value.level1?.trim() || !formData.value.level2?.trim()) {
    Toast.error('一级分类和二级分类都必须填写')
    return false
  }

  if (formData.value.type === 'site' && !formData.value.url?.trim()) {
    Toast.error('导航站点必须填写 URL')
    return false
  }

  if (formData.value.type === 'article' && !formData.value.content?.trim()) {
    Toast.error('文章正文不能为空')
    return false
  }

  return true
}

const submitForm = async () => {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    await createAdminSite({
      type: formData.value.type,
      name: formData.value.name || '',
      url: formData.value.url || '',
      level1: formData.value.level1 || '',
      level2: formData.value.level2 || '',
      level3: formData.value.level3 || '',
      description: formData.value.description || '',
      content: formData.value.content || '',
      contentFormat: formData.value.contentFormat,
      isRecommended: Boolean(formData.value.isRecommended),
      sortOrder: Number(formData.value.sortOrder || 0),
      status: 'approved'
    })

    Toast.success(`保存成功\n类型: ${formData.value.type === 'site' ? '导航站点' : '文章'}\n标题: ${formData.value.name}`)
    resetForm()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '保存失败，请检查登录状态或后端服务')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto pb-20">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 md:mb-8 gap-4">
      <div>
        <h2 class="text-2xl md:text-3xl font-black uppercase">{{ title }}</h2>
        <p class="text-sm opacity-60 mt-1">{{ description }}</p>
      </div>

      <div class="flex bg-gray-200 dark:bg-black rounded-lg p-1 border border-gray-300 dark:border-term-muted w-full sm:w-auto">
        <button
          @click="formData.type = 'site'"
          :class="['flex-1 sm:flex-none px-4 md:px-6 py-2 rounded-md font-bold transition-all text-sm text-center', formData.type === 'site' ? 'bg-white dark:bg-term-primary dark:text-black shadow-sm' : 'opacity-70']"
        >导航站点</button>
        <button
          @click="formData.type = 'article'"
          :class="['flex-1 sm:flex-none px-4 md:px-6 py-2 rounded-md font-bold transition-all text-sm text-center', formData.type === 'article' ? 'bg-white dark:bg-term-primary dark:text-black shadow-sm' : 'opacity-70']"
        >文章内容</button>
      </div>
    </div>

    <form @submit.prevent="submitForm" :class="['space-y-6 bg-white dark:bg-[#111] p-4 md:p-8 border border-gray-300 dark:border-term-muted rounded shadow-sm', cardClass]">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <label class="flex flex-col gap-2 font-bold select-none">
          名称 / 标题
          <input v-model="formData.name" required type="text" class="h-12 border border-gray-400 dark:border-term-muted px-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded" placeholder="例如：Cursor 或 一篇产品文章" />
        </label>

        <label class="flex flex-col gap-2 font-bold select-none">
          {{ formData.type === 'site' ? '官方网站 URL' : '文章来源 URL（可选）' }}
          <input v-model="formData.url" :required="formData.type === 'site'" type="url" class="h-12 border border-gray-400 dark:border-term-muted px-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded" placeholder="https://" />
        </label>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <label class="flex flex-col gap-2 font-bold select-none">
          一级分类
          <div v-if="!isCustomLevel1" class="relative">
            <select
              :value="formData.level1 || ''"
              class="appearance-none h-12 w-full border border-gray-400 dark:border-term-muted px-4 pr-10 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded"
              @change="handleLevel1Select(($event.target as HTMLSelectElement).value)"
            >
              <option value="">请选择一级分类</option>
              <option v-for="level1 in categoryOptions.level1Options" :key="level1" :value="level1">{{ level1 }}</option>
              <option :value="CUSTOM_OPTION_VALUE">手动输入新一级分类</option>
            </select>
            <ChevronDown class="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none opacity-60" />
          </div>
          <div v-else class="space-y-2">
            <input v-model="formData.level1" type="text" class="h-12 w-full border border-gray-400 dark:border-term-muted px-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded" placeholder="输入新一级分类" />
            <button type="button" class="text-xs opacity-70 hover:opacity-100 text-left" @click="isCustomLevel1 = false">返回下拉选择</button>
          </div>
        </label>

        <label class="flex flex-col gap-2 font-bold select-none">
          二级分类
          <div v-if="!isCustomLevel2" class="relative">
            <select
              :value="formData.level2 || ''"
              class="appearance-none h-12 w-full border border-gray-400 dark:border-term-muted px-4 pr-10 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!formData.level1 && !isCustomLevel1"
              @change="handleLevel2Select(($event.target as HTMLSelectElement).value)"
            >
              <option value="">请选择二级分类</option>
              <option v-for="level2 in availableLevel2Options" :key="level2" :value="level2">{{ level2 }}</option>
              <option :value="CUSTOM_OPTION_VALUE">手动输入新二级分类</option>
            </select>
            <ChevronDown class="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none opacity-60" />
          </div>
          <div v-else class="space-y-2">
            <input v-model="formData.level2" type="text" class="h-12 w-full border border-gray-400 dark:border-term-muted px-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded" placeholder="输入新二级分类" />
            <button type="button" class="text-xs opacity-70 hover:opacity-100 text-left" @click="isCustomLevel2 = false">返回下拉选择</button>
          </div>
        </label>

        <label class="flex flex-col gap-2 font-bold select-none">
          三级分类
          <input v-model="formData.level3" type="text" class="h-12 border border-gray-400 dark:border-term-muted px-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded" placeholder="可选" />
        </label>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <label class="flex items-center gap-2 font-bold select-none cursor-pointer h-12">
          <input v-model="formData.isRecommended" type="checkbox" class="w-5 h-5 border-[3px] border-black dark:border-term-primary accent-black dark:accent-black outline-none" />
          设为推荐内容
        </label>

        <label class="flex flex-col gap-2 font-bold select-none">
          排序值
          <input v-model="formData.sortOrder" type="number" class="h-12 border border-gray-400 dark:border-term-muted px-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded" placeholder="默认 0，越大越靠前" />
        </label>
      </div>

      <label class="flex flex-col gap-2 font-bold select-none">
        摘要描述
        <textarea v-model="formData.description" rows="3" class="border border-gray-400 dark:border-term-muted p-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded resize-none" placeholder="一句话介绍内容..." />
      </label>

      <div v-if="formData.type === 'article'" class="space-y-4">
        <label class="flex flex-col gap-2 font-bold select-none max-w-xs">
          正文格式
          <select v-model="formData.contentFormat" class="h-12 border border-gray-400 dark:border-term-muted px-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded">
            <option value="markdown">Markdown</option>
            <option value="html">富文本 HTML</option>
            <option value="text">纯文本</option>
          </select>
        </label>

        <label v-if="formData.contentFormat === 'text'" class="flex flex-col gap-2 font-bold select-none">
          文章正文
          <textarea v-model="formData.content" rows="16" class="border border-gray-400 dark:border-term-muted p-4 bg-transparent outline-none focus:border-neo-accent dark:focus:border-term-primary rounded resize-y" placeholder="输入纯文本内容..." />
        </label>

        <div v-else class="flex flex-col gap-2">
          <span class="font-bold select-none">文章正文</span>
          <div class="border border-gray-400 dark:border-term-muted rounded bg-white dark:bg-black overflow-hidden">
            <RichTextEditor
              v-model="formData.content"
              :format="richEditorFormat"
              placeholder="在这里输入正文内容..."
            />
          </div>
        </div>
      </div>

      <div class="pt-6 border-t border-gray-200 dark:border-term-muted">
        <button :disabled="isSubmitting" type="submit" class="h-12 px-8 bg-black text-white dark:bg-term-primary dark:text-black font-black uppercase text-lg rounded hover:opacity-80 transition-opacity disabled:opacity-60 disabled:cursor-not-allowed">
          {{ isSubmitting ? '保存中...' : submitLabel }}
        </button>
      </div>
    </form>
  </div>
</template>
