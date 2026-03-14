<script setup lang="ts">
import { ref } from 'vue'
import LayoutHeader from '../components/LayoutHeader.vue'
import FooterLinks from '../components/FooterLinks.vue'
import { Toast } from '../utils/toast'
import { submitFriendLink } from '../api/sites'

const form = ref({
  siteName: '',
  siteUrl: '',
  siteDesc: '',
  contactEmail: ''
})

const isSubmitting = ref(false)

const submitFriendLinkForm = async () => {
  if (!form.value.siteName || !form.value.siteUrl || !form.value.contactEmail) {
    Toast.error('请填写必填项')
    return
  }

  isSubmitting.value = true
  try {
    await submitFriendLink(form.value)
    Toast.success(`友链申请已提交\n站点：${form.value.siteName}\n我们会尽快审核`)
    form.value = {
      siteName: '',
      siteUrl: '',
      siteDesc: '',
      contactEmail: ''
    }
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '申请提交失败，请稍后再试')
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
        <h1 class="text-3xl md:text-5xl font-black uppercase tracking-tighter -rotate-1 dark:text-term-primary">友链申请</h1>
        <p class="font-bold opacity-60 text-sm hidden md:block dark:text-term-secondary">互换友情链接，共同成长</p>
      </div>

      <div class="bg-white dark:bg-[#111] p-4 md:p-8 mb-6 border-4 border-black dark:border-term-muted shadow-[4px_4px_0px_0px_#000] md:shadow-[8px_8px_0px_0px_#000] dark:shadow-none">
        <h2 class="text-lg md:text-xl font-black uppercase mb-4 dark:text-term-primary">申请须知</h2>
        <ul class="list-disc pl-5 space-y-2 font-bold opacity-80 text-sm md:text-base dark:text-term-secondary">
          <li>优先交换 AI、科技、设计、开发相关的优质网站。</li>
          <li>请先在贵站添加本站链接，再提交申请。</li>
          <li>提交后会进入后台审核，通过后会展示在前台页脚友情链接区域。</li>
        </ul>
      </div>

      <form @submit.prevent="submitFriendLinkForm" class="bg-white dark:bg-black p-4 md:p-8 border-4 border-black dark:border-term-muted shadow-[4px_4px_0px_0px_#000] md:shadow-[8px_8px_0px_0px_#000] dark:shadow-none flex flex-col gap-4 md:gap-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
            网站名称 *
            <input v-model="form.siteName" required type="text" class="h-12 md:h-14 border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary focus:bg-neo-secondary dark:focus:border-term-primary outline-none transition-colors" placeholder="请输入网站名称" />
          </label>

          <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
            网站链接 *
            <input v-model="form.siteUrl" required type="url" class="h-12 md:h-14 border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary focus:bg-neo-secondary dark:focus:border-term-primary outline-none transition-colors" placeholder="https://" />
          </label>
        </div>

        <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
          网站描述
          <input v-model="form.siteDesc" type="text" class="h-12 md:h-14 border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary focus:bg-neo-secondary dark:focus:border-term-primary outline-none transition-colors" placeholder="一句话介绍你的网站" />
        </label>

        <label class="flex flex-col gap-2 font-bold uppercase text-sm md:text-base dark:text-term-primary">
          联系邮箱 *
          <input v-model="form.contactEmail" required type="email" class="h-12 md:h-14 border-2 md:border-4 border-black dark:border-term-muted px-4 font-bold bg-white dark:bg-black dark:text-term-primary focus:bg-neo-secondary dark:focus:border-term-primary outline-none transition-colors" placeholder="用于接收审核结果" />
        </label>

        <button :disabled="isSubmitting" type="submit" class="h-12 md:h-14 px-6 md:px-8 mt-4 bg-neo-accent dark:bg-term-primary border-[3px] md:border-4 border-black dark:border-black text-white dark:text-black font-black uppercase tracking-widest text-sm md:text-lg hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_#000] dark:hover:shadow-[0_0_15px_rgba(51,255,0,0.5)] active:translate-y-0.5 active:shadow-none transition-all self-start disabled:opacity-60 disabled:cursor-not-allowed">
          {{ isSubmitting ? '提交中...' : '提交申请' }}
        </button>
      </form>
    </main>

    <FooterLinks />
  </div>
</template>
