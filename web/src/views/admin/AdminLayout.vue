<script setup lang="ts">
import { onMounted } from 'vue'
import { Settings, PlusCircle, Database, LogOut } from 'lucide-vue-next'
import FooterLinks from '../../components/FooterLinks.vue'
import { useRouter } from 'vue-router'
import { clearAdminToken, isAdminLoggedIn } from '../../api/sites'

const router = useRouter()

onMounted(() => {
  if (!isAdminLoggedIn()) {
    router.replace('/login')
  }
})

const logout = () => {
  clearAdminToken()
  router.push('/')
}
</script>

<template>
  <div class="h-screen flex flex-col md:flex-row font-neo dark:font-term bg-gray-100 dark:bg-[#0a0a0a] text-black dark:text-term-primary relative z-20 overflow-hidden">
    <aside class="w-full md:w-64 shrink-0 bg-white dark:bg-[#111] border-b md:border-r border-gray-300 dark:border-term-muted shadow flex flex-col pt-safe">
      <div class="p-4 md:p-6 border-b border-gray-300 dark:border-term-muted flex justify-between items-center md:block">
        <div>
          <h1 class="text-xl md:text-2xl font-black uppercase tracking-tighter">ADMIN PANEL</h1>
          <p class="text-[10px] md:text-xs opacity-50 mt-1 hidden md:block">Navigation System V1.0</p>
        </div>
        <button @click="logout" class="md:hidden flex items-center gap-1 p-2 bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 rounded transition-colors text-sm font-bold">
          <LogOut class="w-4 h-4" /> 注销
        </button>
      </div>

      <nav class="flex-none p-2 md:p-4 flex md:flex-col gap-2 overflow-x-auto scroolbar-hide md:overflow-visible flex-nowrap md:flex-wrap">
        <router-link to="/admin" class="shrink-0 flex items-center gap-2 md:gap-3 px-3 md:px-4 py-2 md:py-3 rounded hover:bg-gray-100 dark:hover:bg-term-muted transition-colors font-bold text-sm md:text-base" exact-active-class="bg-neo-accent text-white dark:bg-term-primary dark:text-black">
          <Database class="w-4 h-4 md:w-5 md:h-5" /> 内容管理
        </router-link>
        <router-link to="/admin/create" class="shrink-0 flex items-center gap-2 md:gap-3 px-3 md:px-4 py-2 md:py-3 rounded hover:bg-gray-100 dark:hover:bg-term-muted transition-colors font-bold text-sm md:text-base" active-class="bg-neo-accent text-white dark:bg-term-primary dark:text-black">
          <PlusCircle class="w-4 h-4 md:w-5 md:h-5" /> 发布新内容
        </router-link>
        <router-link to="/admin/settings" class="shrink-0 flex items-center gap-2 md:gap-3 px-3 md:px-4 py-2 md:py-3 rounded hover:bg-gray-100 dark:hover:bg-term-muted transition-colors font-bold text-sm md:text-base" active-class="bg-neo-accent text-white dark:bg-term-primary dark:text-black">
          <Settings class="w-4 h-4 md:w-5 md:h-5" /> 系统设置
        </router-link>
      </nav>

      <div class="hidden md:block p-4 border-t border-gray-300 dark:border-term-muted mt-auto">
        <button @click="logout" class="w-full flex items-center justify-center gap-2 py-3 border border-red-500 text-red-500 hover:bg-red-500 hover:text-white dark:border-term-error dark:text-term-error dark:hover:bg-term-error dark:hover:text-black font-bold transition-colors rounded">
          <LogOut class="w-4 h-4" /> 退出登录
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col overflow-y-auto p-4 md:p-8 relative z-20 bg-white/90 dark:bg-black/90">
      <router-view class="flex-1" />
      <FooterLinks />
    </main>
  </div>
</template>
