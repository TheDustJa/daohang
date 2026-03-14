<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import LayoutHeader from '../components/LayoutHeader.vue'
import FooterLinks from '../components/FooterLinks.vue'
import { Toast } from '../utils/toast'
import { fetchCategoryOptions, submitSite, type CategoryOptions } from '../api/sites'

const CUSTOM_OPTION_VALUE = '__custom__'

const formData = ref({
  name: '',
  url: '',
  level1: '',
  level2: '',
  description: ''
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

onMounted(async () => {
  try {
    categoryOptions.value = await fetchCategoryOptions()
  } catch {
    categoryOptions.value = {
      level1Options: [],
      level2Options: [],
      level2ByLevel1: {}
    }
  }
})

const handleLevel1Select = (value: string) => {
  if (value === CUSTOM_OPTION_VALUE) {
    isCustomLevel1.value = true
    isCustomLevel2.value = false
    formData.value.level1 = ''
    formData.value.level2 = ''
    return
  }

  isCustomLevel1.value = false
  isCustomLevel2.value = false
  formData.value.level1 = value
  if (!availableLevel2Options.value.includes(formData.value.level2)) {
    formData.value.level2 = ''
  }
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

const resetForm = () => {
  formData.value = {
    name: '',
    url: '',
    level1: '',
    level2: '',
    description: ''
  }
  isCustomLevel1.value = false
  isCustomLevel2.value = false
}

const submitForm = async () => {
  if (!formData.value.name.trim() || !formData.value.url.trim()) {
    Toast.error('请填写名称和网址')
    return
  }

  if (!formData.value.level1.trim() || !formData.value.level2.trim()) {
    Toast.error('一级分类和二级分类都必须填写')
    return
  }

  isSubmitting.value = true
  try {
    await submitSite({
      type: 'site',
      name: formData.value.name,
      url: formData.value.url,
      level1: formData.value.level1,
      level2: formData.value.level2,
      description: formData.value.description
    })
    Toast.success(`提交成功\n待审核站点: ${formData.value.name}`)
    resetForm()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '提交失败，请稍后再试')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10 transition-colors duration-300">
    <LayoutHeader class="shrink-0 relative z-20" />
    <main class="flex-1 container mx-auto max-w-3xl py-8 md:py-12 px-4 md:px-6">
      <div class="flex items-end justify-between mb-8">
        <h1 class="text-3xl md:text-5xl font-black uppercase tracking-tighter -rotate-1 dark:text-term-primary">提交收录</h1>
        <p class="font-bold opacity-60 text-sm hidden md:block dark:text-term-secondary">提交优质网站，后台审核通过后展示</p>
      </div>

      <p class="mb-6 text-sm md:text-base leading-7 font-medium text-black/75 dark:text-term-secondary">
        大家提交的内容优先放在“站长常用”一级分类里。导航网站千千万，真正能用的没几个，淦。本就是想整合一些优质的内容，大家一起使用，大家多多支持。
      </p>

      <form @submit.prevent="submitForm" class="bg-white dark:bg-black p-4 md:p-8 border-4 border-black dark:border-term-muted shadow-[4px_4px_0px_0px_#000] md:shadow-[8px_8px_0px_0px_#000] dark:shadow-none flex flex-col gap-4 md:gap-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
            网站名称 *
            <input v-model="formData.name" required type="text" class="h-12 md:h-14 border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary focus:bg-neo-secondary dark:focus:border-term-primary outline-none transition-colors" placeholder="输入网站名称" />
          </label>

          <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
            官方网址 *
            <input v-model="formData.url" required type="url" class="h-12 md:h-14 border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary focus:bg-neo-secondary dark:focus:border-term-primary outline-none transition-colors" placeholder="https://" />
          </label>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
            所属一级分类 *
            <div v-if="!isCustomLevel1" class="relative">
              <select
                :value="formData.level1 || ''"
                class="appearance-none h-12 md:h-14 w-full border-2 md:border-4 border-black dark:border-term-muted px-4 pr-10 font-bold bg-white dark:bg-black dark:text-term-primary outline-none focus:bg-neo-secondary dark:focus:border-term-primary rounded-none"
                @change="handleLevel1Select(($event.target as HTMLSelectElement).value)"
              >
                <option value="">请选择一级分类</option>
                <option v-for="level1 in categoryOptions.level1Options" :key="level1" :value="level1">{{ level1 }}</option>
                <option :value="CUSTOM_OPTION_VALUE">手动输入新一级分类</option>
              </select>
              <ChevronDown class="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
            <div v-else class="space-y-2">
              <input v-model="formData.level1" type="text" class="h-12 md:h-14 w-full border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary outline-none focus:bg-neo-secondary dark:focus:border-term-primary" placeholder="输入新一级分类" />
              <button type="button" class="text-left text-xs opacity-70 hover:opacity-100" @click="isCustomLevel1 = false">返回下拉选择</button>
            </div>
          </label>

          <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
            所属二级分类 *
            <div v-if="!isCustomLevel2" class="relative">
              <select
                :value="formData.level2 || ''"
                class="appearance-none h-12 md:h-14 w-full border-2 md:border-4 border-black dark:border-term-muted px-4 pr-10 font-bold bg-white dark:bg-black dark:text-term-primary outline-none focus:bg-neo-secondary dark:focus:border-term-primary rounded-none disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="!formData.level1 && !isCustomLevel1"
                @change="handleLevel2Select(($event.target as HTMLSelectElement).value)"
              >
                <option value="">请选择二级分类</option>
                <option v-for="level2 in availableLevel2Options" :key="level2" :value="level2">{{ level2 }}</option>
                <option :value="CUSTOM_OPTION_VALUE">手动输入新二级分类</option>
              </select>
              <ChevronDown class="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
            <div v-else class="space-y-2">
              <input v-model="formData.level2" type="text" class="h-12 md:h-14 w-full border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary outline-none focus:bg-neo-secondary dark:focus:border-term-primary" placeholder="输入新二级分类" />
              <button type="button" class="text-left text-xs opacity-70 hover:opacity-100" @click="isCustomLevel2 = false">返回下拉选择</button>
            </div>
          </label>
        </div>

        <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
          简要介绍
          <textarea v-model="formData.description" rows="3" class="border-2 md:border-4 border-black dark:border-term-muted p-4 font-bold bg-white dark:bg-black dark:text-term-primary focus:bg-neo-secondary dark:focus:border-term-primary outline-none resize-none transition-colors" placeholder="简单介绍这个网站的功能和特点..." />
        </label>

        <button :disabled="isSubmitting" type="submit" class="h-12 md:h-14 px-6 md:px-8 mt-4 bg-neo-accent dark:bg-term-primary border-[3px] md:border-4 border-black dark:border-black text-white dark:text-black font-black uppercase tracking-widest text-sm md:text-lg hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_#000] dark:hover:shadow-[0_0_15px_rgba(51,255,0,0.5)] active:translate-y-0.5 active:shadow-none transition-all self-start disabled:opacity-60 disabled:cursor-not-allowed">
          {{ isSubmitting ? '提交中...' : '提交审核' }}
        </button>
      </form>
    </main>
    <FooterLinks />
  </div>
</template>
