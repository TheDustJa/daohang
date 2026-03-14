<script setup lang="ts">
import { ref } from 'vue'
import LayoutHeader from '../components/LayoutHeader.vue'
import FooterLinks from '../components/FooterLinks.vue'
import { useRouter } from 'vue-router'
import { Toast } from '../utils/toast'
import { loginAdmin } from '../api/sites'

const router = useRouter()
const username = ref('')
const password = ref('')
const isSubmitting = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    Toast.error('请输入用户名和密码')
    return
  }

  isSubmitting.value = true
  try {
    await loginAdmin({
      username: username.value,
      password: password.value
    })
    Toast.success('登录成功，欢迎来到后台管理系统')
    router.push('/admin')
  } catch {
    Toast.error('登录失败，用户名或密码错误')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-neo dark:font-term bg-neo-bg dark:bg-transparent relative z-10">
    <LayoutHeader class="shrink-0 relative z-20" />
    <main class="flex-1 flex items-center justify-center p-6">
      <form class="w-full max-w-md bg-white dark:bg-black p-8 border-4 border-black dark:border-term-muted shadow-neo-xl rotate-1">
        <h1 class="text-4xl font-black uppercase tracking-tighter mb-8">系统登录</h1>
        <div class="flex flex-col gap-6">
          <label class="flex flex-col gap-2 font-bold uppercase">
            用户名
            <input v-model="username" type="text" class="h-14 border-4 border-black dark:border-term-muted px-4 font-bold dark:bg-black focus:bg-neo-secondary dark:focus:border-term-primary outline-none" />
          </label>
          <label class="flex flex-col gap-2 font-bold uppercase">
            密码
            <input v-model="password" type="password" class="h-14 border-4 border-black dark:border-term-muted px-4 font-bold dark:bg-black focus:bg-neo-secondary dark:focus:border-term-primary outline-none" />
          </label>
          <button :disabled="isSubmitting" type="button" @click="handleLogin" class="btn-primary w-full mt-2 disabled:opacity-60 disabled:cursor-not-allowed">
            {{ isSubmitting ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>
    </main>
    <FooterLinks />
  </div>
</template>
