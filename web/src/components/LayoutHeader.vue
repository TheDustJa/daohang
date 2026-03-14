<script setup lang="ts">
import { computed } from 'vue'
import { Search, User, Compass, Newspaper, Cpu, BookOpen } from 'lucide-vue-next'
import { useNavigationStore } from '../store/navigation'
import { useRouter } from 'vue-router'

const store = useNavigationStore()
const router = useRouter()

const iconMap: Record<string, typeof Compass> = {
  'AI 工具': Compass,
  'AI工具': Compass,
  'AI 资讯': Newspaper,
  'AI资讯': Newspaper,
  '提示词': Cpu,
  '我的文章': BookOpen
}

const level1Items = computed(() =>
  store.level1Categories.map((item) => ({
    name: item.name,
    icon: iconMap[item.name] || Compass
  }))
)

const handleLevel1Click = (name: string) => {
  store.$patch({ activeLevel1: name, searchQuery: '' })
  router.push('/')
}

const resetHomeCategory = () => {
  store.activeLevel1 = store.level1Categories[0]?.name || ''
  store.searchQuery = ''
}

const handleSearch = (e: Event) => {
  const target = e.target as HTMLInputElement
  store.$patch({ searchQuery: target.value })
}
</script>

<template>
  <header class="min-h-[4rem] flex flex-col xl:flex-row xl:items-center justify-between px-4 md:px-6 bg-white dark:bg-black border-b-4 border-black dark:border-term-muted shadow-neo-sm py-2 md:py-3 gap-3 xl:gap-4">
    <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 w-full xl:w-auto shrink-0">
      <div class="flex items-center justify-between w-full md:w-auto shrink-0">
        <router-link to="/" @click="resetHomeCategory" class="flex items-center gap-1.5 md:gap-2 group cursor-pointer shrink-0">
          <div class="w-7 h-7 md:w-10 md:h-10 bg-neo-accent dark:bg-term-primary border-2 md:border-4 border-black dark:border-black flex items-center justify-center -rotate-2 group-hover:rotate-0 transition-transform">
            <span class="font-black text-[10px] md:text-sm text-white dark:text-black">导航</span>
          </div>
          <h1 class="text-lg md:text-2xl font-black uppercase tracking-tighter dark:text-term-primary">AI 导航</h1>
        </router-link>

        <div class="flex items-center gap-1.5 shrink-0 md:hidden">
          <router-link to="/login" class="w-8 h-8 flex items-center justify-center border-2 border-black dark:border-term-muted bg-white dark:bg-black hover:bg-neo-muted dark:hover:bg-term-muted transition-colors shadow-[2px_2px_0px_0px_#000] dark:shadow-none active:translate-y-0.5 active:translate-x-0.5 active:shadow-none rounded-sm">
            <User class="w-3.5 h-3.5 dark:text-term-primary" :stroke-width="3" />
          </router-link>
        </div>
      </div>

      <nav class="flex items-center gap-1.5 md:gap-4 overflow-x-auto no-scrollbar md:pr-4 pb-1 md:pb-0 w-full md:w-max whitespace-nowrap">
        <button
          v-for="item in level1Items"
          :key="item.name"
          @click="handleLevel1Click(item.name)"
          :class="[
            'flex items-center gap-1 px-2 py-1 md:px-4 md:py-2 text-[11px] md:text-base font-bold uppercase transition-transform shrink-0',
            store.activeLevel1 === item.name
              ? 'bg-neo-secondary dark:bg-term-primary dark:text-black border-2 md:border-4 border-black dark:border-term-primary shadow-[2px_2px_0px_0px_#000] md:shadow-[4px_4px_0px_0px_#000] -translate-y-0.5 md:-translate-y-1'
              : 'border-2 md:border-[4px] border-transparent hover:border-black dark:hover:border-term-primary opacity-70 hover:opacity-100'
          ]"
        >
          <component :is="item.icon" class="w-3.5 h-3.5 md:w-5 md:h-5" :stroke-width="store.activeLevel1 === item.name ? 3 : 2" />
          {{ item.name }}
        </button>
      </nav>
    </div>

    <div class="hidden md:flex flex-row items-center justify-between xl:justify-end gap-4 w-full xl:w-auto shrink-0 mt-2 xl:mt-0">
      <div class="relative w-full max-w-sm xl:max-w-xs group shadow-neo-sm xl:shadow-none">
        <input
          type="text"
          placeholder="搜索..."
          :value="store.searchQuery"
          @input="handleSearch"
          class="w-full h-10 md:h-10 pl-10 pr-4 text-sm md:text-base font-bold uppercase bg-white dark:bg-black border-[3px] md:border-4 border-black dark:border-term-muted focus:bg-neo-secondary dark:focus:border-term-primary dark:focus:ring-1 dark:focus:ring-term-primary focus:shadow-neo-sm focus:outline-none transition-colors"
        />
        <Search class="absolute left-3 top-2.5 w-5 h-5 text-black dark:text-term-muted group-focus-within:text-black dark:group-focus-within:text-term-primary" :stroke-width="3" />
      </div>

      <div class="flex items-center gap-2 md:gap-4 shrink-0">
        <router-link to="/friend-link" class="flex text-sm h-10 items-center font-bold hover:underline opacity-80 cursor-pointer">
          友链申请
        </router-link>
        <router-link to="/submit" class="flex btn-primary text-sm h-10 items-center">
          提交网站
        </router-link>
        <router-link to="/login" class="w-10 h-10 flex items-center justify-center border-[3px] md:border-4 bg-white dark:bg-black hover:bg-neo-muted dark:hover:bg-term-muted transition-colors shadow-neo-sm active:translate-y-1 active:translate-x-1 active:shadow-none">
          <User class="w-5 h-5 dark:text-term-primary" :stroke-width="3" />
        </router-link>
      </div>
    </div>
  </header>
</template>
