<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import {
  ArrowRight,
  Check,
  Edit2,
  Folder,
  FolderOpen,
  Home,
  PlusCircle,
  Save,
  Search,
  Trash2,
  X
} from 'lucide-vue-next'
import { Toast } from '../../utils/toast'
import {
  clearAdminUncategorizedSites,
  createAdminCategory,
  deleteAdminCategory,
  deleteAdminSite,
  fetchAdminCategoryOptions,
  fetchAdminCategoryTree,
  fetchAdminSites,
  updateAdminCategory,
  updateAdminSite,
  type AdminCategoryNode,
  type CategoryOptions,
  type Site
} from '../../api/sites'

const sites = ref<Site[]>([])
const categoryTree = ref<AdminCategoryNode[]>([])
const categoryOptions = ref<CategoryOptions>({
  level1Options: [],
  level2Options: [],
  level2ByLevel1: {}
})

const loading = ref(false)
const categorySubmitting = ref(false)
const clearingUncategorized = ref(false)
const searchQuery = ref('')
const selectedLevel1 = ref<string | null>(null)
const selectedLevel2 = ref<string | null>(null)
const expandedCategories = ref<Record<number, boolean>>({})
const dirtySiteIds = ref<number[]>([])
const savingSiteIds = ref<number[]>([])

const categoryDialog = reactive({
  open: false,
  mode: 'create' as 'create' | 'edit',
  id: null as number | null,
  parentId: null as number | null,
  name: '',
  sortOrder: 0,
  title: ''
})

const level2DeleteDialog = reactive({
  open: false,
  category: null as AdminCategoryNode | null,
  loading: false
})

const totalSites = computed(() => sites.value.length)
const totalCategories = computed(() => {
  return categoryTree.value.reduce((sum, item) => sum + 1 + item.children.length, 0)
})
const uncategorizedCount = computed(() => {
  return sites.value.filter(site => !site.level1?.trim() || !site.level2?.trim()).length
})

const filteredSites = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase()
  return sites.value
    .filter((site) => {
      if (selectedLevel1.value && site.level1 !== selectedLevel1.value) return false
      if (selectedLevel2.value && site.level2 !== selectedLevel2.value) return false
      if (!keyword) return true

      return [site.name, site.description, site.url]
        .filter(Boolean)
        .some((value) => value!.toLowerCase().includes(keyword))
    })
    .sort((a, b) => {
      if ((a.sortOrder || 0) !== (b.sortOrder || 0)) {
        return (b.sortOrder || 0) - (a.sortOrder || 0)
      }
      const aRec = a.isRecommended ? 1 : 0
      const bRec = b.isRecommended ? 1 : 0
      if (aRec !== bRec) {
        return bRec - aRec
      }
      return b.id - a.id
    })
})

const isSiteSaving = (id: number) => savingSiteIds.value.includes(id)
const isSiteDirty = (id: number) => dirtySiteIds.value.includes(id)

const markSiteDirty = (id: number) => {
  if (!dirtySiteIds.value.includes(id)) {
    dirtySiteIds.value = [...dirtySiteIds.value, id]
  }
}

const clearSiteDirty = (id: number) => {
  dirtySiteIds.value = dirtySiteIds.value.filter(item => item !== id)
}

const refreshSites = async () => {
  sites.value = await fetchAdminSites()
}

const loadCategories = async () => {
  const [tree, options] = await Promise.all([
    fetchAdminCategoryTree(),
    fetchAdminCategoryOptions()
  ])
  categoryTree.value = tree
  categoryOptions.value = options
  expandedCategories.value = tree.reduce<Record<number, boolean>>((acc, item) => {
    acc[item.id] = expandedCategories.value[item.id] ?? true
    return acc
  }, {})

  if (selectedLevel1.value && !options.level1Options.includes(selectedLevel1.value)) {
    selectedLevel1.value = null
    selectedLevel2.value = null
  }

  if (
    selectedLevel1.value &&
    selectedLevel2.value &&
    !options.level2ByLevel1[selectedLevel1.value]?.includes(selectedLevel2.value)
  ) {
    selectedLevel2.value = null
  }
}

const loadDashboard = async () => {
  loading.value = true
  try {
    await Promise.all([refreshSites(), loadCategories()])
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '管理数据加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)

const selectCategory = (level1: string | null, level2: string | null = null) => {
  selectedLevel1.value = level1
  selectedLevel2.value = level2
}

const toggleCategory = (id: number) => {
  expandedCategories.value[id] = !expandedCategories.value[id]
}

const getAvailableLevel2 = (level1: string) => {
  return categoryOptions.value.level2ByLevel1[level1] || []
}

const handleLevel1Change = (site: Site) => {
  const availableLevel2 = getAvailableLevel2(site.level1)
  if (!availableLevel2.includes(site.level2)) {
    site.level2 = availableLevel2[0] || ''
  }
  markSiteDirty(site.id)
}

const openCreateLevel1Dialog = () => {
  categoryDialog.open = true
  categoryDialog.mode = 'create'
  categoryDialog.id = null
  categoryDialog.parentId = null
  categoryDialog.name = ''
  categoryDialog.sortOrder = 0
  categoryDialog.title = '新增一级分类'
}

const openCreateLevel2Dialog = (parent: AdminCategoryNode) => {
  categoryDialog.open = true
  categoryDialog.mode = 'create'
  categoryDialog.id = null
  categoryDialog.parentId = parent.id
  categoryDialog.name = ''
  categoryDialog.sortOrder = 0
  categoryDialog.title = `新增二级分类 / ${parent.name}`
}

const openEditDialog = (category: AdminCategoryNode, parentId: number | null) => {
  categoryDialog.open = true
  categoryDialog.mode = 'edit'
  categoryDialog.id = category.id
  categoryDialog.parentId = parentId
  categoryDialog.name = category.name
  categoryDialog.sortOrder = category.sortOrder || 0
  categoryDialog.title = `编辑分类 / ${category.name}`
}

const closeDialog = () => {
  categoryDialog.open = false
}

const submitCategory = async () => {
  if (!categoryDialog.name.trim()) {
    Toast.warning('请先填写分类名称')
    return
  }

  categorySubmitting.value = true
  try {
    const payload = {
      name: categoryDialog.name.trim(),
      parentId: categoryDialog.parentId,
      sortOrder: Number(categoryDialog.sortOrder || 0)
    }

    if (categoryDialog.mode === 'create') {
      await createAdminCategory(payload)
      Toast.success('分类已创建')
    } else if (categoryDialog.id !== null) {
      await updateAdminCategory(categoryDialog.id, payload)
      Toast.success('分类已更新')
    }

    await Promise.all([refreshSites(), loadCategories()])
    closeDialog()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '分类保存失败')
  } finally {
    categorySubmitting.value = false
  }
}

const confirmDeleteLevel1 = async (category: AdminCategoryNode) => {
  const ok = window.confirm(`删除一级分类“${category.name}”后，分类关系会被清空。确定继续吗？`)
  if (!ok) return

  try {
    await deleteAdminCategory(category.id)
    await Promise.all([refreshSites(), loadCategories()])
    Toast.success('分类已删除')
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '分类删除失败')
  }
}

const openLevel2DeleteDialog = (category: AdminCategoryNode) => {
  level2DeleteDialog.open = true
  level2DeleteDialog.category = category
}

const closeLevel2DeleteDialog = () => {
  level2DeleteDialog.open = false
  level2DeleteDialog.category = null
}

const deleteLevel2Category = async (deleteRelatedContent: boolean) => {
  if (!level2DeleteDialog.category) return

  level2DeleteDialog.loading = true
  try {
    await deleteAdminCategory(level2DeleteDialog.category.id, deleteRelatedContent)
    await Promise.all([refreshSites(), loadCategories()])
    Toast.success(deleteRelatedContent ? '二级分类及对应内容已删除' : '二级分类已删除，对应内容已保留')
    closeLevel2DeleteDialog()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '二级分类删除失败')
  } finally {
    level2DeleteDialog.loading = false
  }
}

const clearUncategorizedContent = async () => {
  if (!uncategorizedCount.value) {
    Toast.warning('当前没有未分类内容')
    return
  }

  const ok = window.confirm(`确定清空 ${uncategorizedCount.value} 条未分类内容吗？该操作不可撤销。`)
  if (!ok) return

  clearingUncategorized.value = true
  try {
    await clearAdminUncategorizedSites()
    await Promise.all([refreshSites(), loadCategories()])
    Toast.success('未分类内容已清空')
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '清空未分类内容失败')
  } finally {
    clearingUncategorized.value = false
  }
}

const saveSite = async (site: Site) => {
  if (isSiteSaving(site.id)) return

  savingSiteIds.value = [...savingSiteIds.value, site.id]
  try {
    const updated = await updateAdminSite(site.id, {
      name: site.name,
      url: site.url,
      logo: site.logo,
      description: site.description,
      level1: site.level1,
      level2: site.level2,
      level3: site.level3,
      tags: site.tags || [],
      isRecommended: Boolean(site.isRecommended),
      sortOrder: Number(site.sortOrder || 0),
      type: site.type || 'site',
      content: site.content || '',
      contentFormat: site.contentFormat || 'html',
      status: site.status || 'approved'
    })

    const index = sites.value.findIndex(item => item.id === site.id)
    if (index !== -1) {
      sites.value[index] = updated
    }
    clearSiteDirty(site.id)
    await loadCategories()
    Toast.success('内容分类已更新')
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '内容保存失败')
  } finally {
    savingSiteIds.value = savingSiteIds.value.filter(id => id !== site.id)
  }
}

const deleteSiteItem = async (site: Site) => {
  if (!window.confirm(`确定删除内容“${site.name}”吗？此操作不可撤销。`)) return

  savingSiteIds.value = [...savingSiteIds.value, site.id]
  try {
    await deleteAdminSite(site.id, site.type || 'site')
    sites.value = sites.value.filter(item => !(item.id === site.id && (item.type || 'site') === (site.type || 'site')))
    clearSiteDirty(site.id)
    await loadCategories()
    Toast.success('内容已删除')
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '内容删除失败')
  } finally {
    savingSiteIds.value = savingSiteIds.value.filter(id => id !== site.id)
  }
}
</script>

<template>
  <div class="h-full flex flex-col mx-auto max-w-7xl animate-fade-in pb-10">
    <div class="mb-6 md:mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div>
        <h2 class="text-2xl md:text-3xl font-black uppercase flex items-center gap-3">内容与分类管理</h2>
        <p class="text-sm opacity-60 mt-1">管理站点内容、分类结构，以及内容所属的层级关系。</p>
      </div>

      <div class="flex items-center gap-4 bg-white dark:bg-[#111] p-2 px-4 rounded-lg border border-gray-300 dark:border-term-muted shadow-sm">
        <div class="text-center px-2">
          <div class="text-xs opacity-60 font-bold uppercase">内容总数</div>
          <div class="text-lg font-black">{{ totalSites }}</div>
        </div>
        <div class="w-px h-8 bg-gray-300 dark:bg-term-muted"></div>
        <div class="text-center px-2">
          <div class="text-xs opacity-60 font-bold uppercase">分类总数</div>
          <div class="text-lg font-black">{{ totalCategories }}</div>
        </div>
        <div class="w-px h-8 bg-gray-300 dark:bg-term-muted"></div>
        <div class="text-center px-2">
          <div class="text-xs opacity-60 font-bold uppercase">未分类</div>
          <div class="text-lg font-black">{{ uncategorizedCount }}</div>
        </div>
      </div>
    </div>

    <div class="mb-6 flex justify-end">
      <button
        class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-red-400 text-red-500 text-sm font-bold hover:bg-red-50 dark:hover:bg-red-900/10 disabled:opacity-60"
        :disabled="clearingUncategorized"
        @click="clearUncategorizedContent"
      >
        <Trash2 class="w-4 h-4" />
        {{ clearingUncategorized ? '清理中...' : '清空未分类内容' }}
      </button>
    </div>

    <div class="flex-1 flex flex-col md:flex-row gap-6 min-h-0">
      <div class="w-full md:w-80 flex shrink-0 flex-col bg-white dark:bg-[#111] border border-gray-300 dark:border-term-muted rounded-xl shadow-sm overflow-hidden h-[520px] md:h-auto md:max-h-[calc(100vh-200px)]">
        <div class="p-4 border-b border-gray-200 dark:border-term-muted bg-gray-50 dark:bg-black/50 flex justify-between items-center">
          <h3 class="font-black text-sm uppercase flex items-center gap-2">
            <Folder class="w-4 h-4" /> 分类结构
          </h3>
          <button
            class="w-8 h-8 flex items-center justify-center rounded-md hover:bg-gray-200 dark:hover:bg-term-muted/30 transition-colors text-black dark:text-term-primary"
            title="新增一级分类"
            @click="openCreateLevel1Dialog"
          >
            <PlusCircle class="w-4 h-4" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-2 scrollbar-thin">
          <button
            @click="selectCategory(null)"
            :class="[
              'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-bold transition-all mb-2',
              selectedLevel1 === null ? 'bg-neo-accent text-white dark:bg-term-primary dark:text-black shadow-md' : 'hover:bg-gray-100 dark:hover:bg-term-muted/20 opacity-80 hover:opacity-100'
            ]"
          >
            <Home class="w-4 h-4" /> 全部内容
          </button>

          <div v-if="!categoryTree.length && !loading" class="px-3 py-6 text-sm opacity-60">
            还没有分类，先创建一级分类。
          </div>

          <div v-for="level1 in categoryTree" :key="level1.id" class="mb-2">
            <div
              class="group flex items-center relative rounded-lg transition-colors overflow-hidden"
              :class="selectedLevel1 === level1.name && selectedLevel2 === null ? 'bg-blue-50 dark:bg-term-primary/10 border border-blue-200 dark:border-term-primary/30' : 'hover:bg-gray-50 dark:hover:bg-term-muted/10 border border-transparent'"
            >
              <button @click="toggleCategory(level1.id)" class="p-2 opacity-50 hover:opacity-100 transition-opacity">
                <FolderOpen v-if="expandedCategories[level1.id]" class="w-4 h-4 text-neo-accent dark:text-term-primary" />
                <Folder v-else class="w-4 h-4" />
              </button>

              <button @click="selectCategory(level1.name)" class="flex-1 text-left py-2.5 px-1 font-bold text-sm truncate flex justify-between items-center pr-2">
                {{ level1.name }}
                <span class="text-xs bg-gray-200 dark:bg-term-muted/50 px-2 py-0.5 rounded-full font-normal opacity-70">
                  {{ level1.total }}
                </span>
              </button>

              <div class="absolute right-1 opacity-0 group-hover:opacity-100 flex items-center bg-gray-50 dark:bg-[#1a1a1a] shadow-sm rounded-md border border-gray-200 dark:border-term-muted/50 transition-opacity">
                <button class="p-1.5 hover:text-neo-accent dark:hover:text-term-primary" title="新增二级分类" @click="openCreateLevel2Dialog(level1)">
                  <PlusCircle class="w-3 h-3" />
                </button>
                <button class="p-1.5 hover:text-neo-accent dark:hover:text-term-primary" title="编辑分类" @click="openEditDialog(level1, null)">
                  <Edit2 class="w-3 h-3" />
                </button>
                <button class="p-1.5 hover:text-red-500" title="删除分类" @click="confirmDeleteLevel1(level1)">
                  <Trash2 class="w-3 h-3" />
                </button>
              </div>
            </div>

            <div v-show="expandedCategories[level1.id]" class="pl-7 pr-1 py-1 space-y-0.5 relative">
              <div class="absolute left-4 top-0 bottom-2 w-px bg-gray-300 dark:bg-term-muted/50"></div>

              <div
                v-for="level2 in level1.children"
                :key="level2.id"
                class="group relative flex items-center rounded-md"
                :class="selectedLevel1 === level1.name && selectedLevel2 === level2.name ? 'bg-blue-50 dark:bg-term-primary/10 text-neo-accent dark:text-term-primary font-bold' : 'hover:bg-gray-50 dark:hover:bg-term-muted/10 text-gray-600 dark:text-gray-400 font-medium'"
              >
                <div class="absolute -left-3 top-1/2 w-3 h-px bg-gray-300 dark:bg-term-muted/50"></div>

                <button @click="selectCategory(level1.name, level2.name)" class="flex-1 text-left py-1.5 px-3 text-sm truncate flex justify-between items-center">
                  {{ level2.name }}
                  <span class="text-[10px] opacity-60">{{ level2.total }}</span>
                </button>

                <div class="opacity-0 group-hover:opacity-100 flex items-center mr-1 transition-opacity">
                  <button class="p-1.5 hover:text-neo-accent dark:hover:text-term-primary" title="编辑分类" @click="openEditDialog(level2, level1.id)">
                    <Edit2 class="w-3 h-3" />
                  </button>
                  <button class="p-1.5 hover:text-red-500" title="删除分类" @click="openLevel2DeleteDialog(level2)">
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex-1 flex flex-col bg-white dark:bg-[#111] border border-gray-300 dark:border-term-muted rounded-xl shadow-sm overflow-hidden md:max-h-[calc(100vh-200px)]">
        <div class="p-4 border-b border-gray-200 dark:border-term-muted flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-gray-50 dark:bg-black/50">
          <div>
            <h3 class="font-black text-lg">
              <span v-if="!selectedLevel1">全部内容</span>
              <span v-else class="flex items-center gap-2">
                {{ selectedLevel1 }}
                <template v-if="selectedLevel2">
                  <ArrowRight class="w-4 h-4 opacity-50" />
                  <span class="text-neo-accent dark:text-term-primary">{{ selectedLevel2 }}</span>
                </template>
              </span>
            </h3>
            <p class="text-xs opacity-60 mt-0.5">当前共找到 {{ filteredSites.length }} 条内容</p>
          </div>

          <div class="relative w-full sm:w-72 shrink-0">
            <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 opacity-50" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索名称、简介或链接"
              class="w-full h-10 pl-9 pr-4 text-sm bg-white dark:bg-black border border-gray-300 dark:border-term-muted rounded-lg outline-none focus:border-neo-accent dark:focus:border-term-primary transition-colors focus:ring-2 ring-neo-accent/20 dark:ring-term-primary/20"
            />
          </div>
        </div>

        <div v-if="loading" class="p-8 text-center text-sm opacity-60">正在加载管理数据...</div>

        <div v-else class="flex-1 overflow-x-auto overflow-y-auto w-full">
          <table class="w-full text-left border-collapse min-w-[820px]">
            <thead class="sticky top-0 bg-gray-100/95 dark:bg-[#1a1a1a]/95 backdrop-blur-sm z-10 border-b border-gray-300 dark:border-term-muted shadow-sm">
              <tr>
                <th class="p-3 pl-4 font-bold text-xs uppercase tracking-wider opacity-70 w-[30%]">内容信息</th>
                <th class="p-3 font-bold text-xs uppercase tracking-wider opacity-70 w-[16%]">一级分类</th>
                <th class="p-3 font-bold text-xs uppercase tracking-wider opacity-70 w-[16%]">二级分类</th>
                <th class="p-3 font-bold text-xs uppercase tracking-wider opacity-70 w-[12%]">排序值</th>
                <th class="p-3 font-bold text-xs uppercase tracking-wider opacity-70 w-[10%]">状态</th>
                <th class="p-3 pr-4 font-bold text-xs uppercase tracking-wider opacity-70 w-[16%] text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-term-muted/30">
              <tr v-for="site in filteredSites" :key="site.id" class="hover:bg-blue-50/50 dark:hover:bg-term-muted/10 transition-colors">
                <td class="p-3 pl-4">
                  <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-2">
                      <span class="font-bold text-sm text-black dark:text-white">{{ site.name }}</span>
                      <span class="text-[10px] px-2 py-0.5 rounded-full bg-gray-200 dark:bg-term-muted/40 uppercase">{{ site.type || 'site' }}</span>
                    </div>
                    <a :href="site.url" target="_blank" rel="noreferrer" class="text-xs text-blue-500 hover:underline truncate max-w-[260px]">{{ site.url || '无外链' }}</a>
                    <p class="text-xs opacity-70">{{ site.description || '暂无简介' }}</p>
                  </div>
                </td>

                <td class="p-3">
                  <select
                    v-model="site.level1"
                    class="appearance-none w-full bg-gray-50 dark:bg-black border border-gray-200 dark:border-term-muted text-sm rounded py-2 pl-3 pr-8 outline-none focus:border-neo-accent dark:focus:border-term-primary focus:ring-1 ring-neo-accent/20 cursor-pointer transition-colors"
                    @change="handleLevel1Change(site)"
                  >
                    <option value="">未分类</option>
                    <option v-for="level1 in categoryOptions.level1Options" :key="level1" :value="level1">{{ level1 }}</option>
                  </select>
                </td>

                <td class="p-3">
                  <select
                    v-model="site.level2"
                    class="appearance-none w-full bg-gray-50 dark:bg-black border border-gray-200 dark:border-term-muted text-sm rounded py-2 pl-3 pr-8 outline-none focus:border-neo-accent dark:focus:border-term-primary focus:ring-1 ring-neo-accent/20 cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="!site.level1 || !getAvailableLevel2(site.level1).length"
                    @change="markSiteDirty(site.id)"
                  >
                    <option value="">未分类</option>
                    <option v-for="level2 in getAvailableLevel2(site.level1)" :key="level2" :value="level2">{{ level2 }}</option>
                  </select>
                </td>

                <td class="p-3">
                  <input
                    v-model="site.sortOrder"
                    type="number"
                    class="w-full bg-gray-50 dark:bg-black border border-gray-200 dark:border-term-muted text-sm rounded py-2 px-3 outline-none focus:border-neo-accent dark:focus:border-term-primary focus:ring-1 ring-neo-accent/20 transition-colors"
                    placeholder="越大越靠前"
                    @input="markSiteDirty(site.id)"
                  />
                </td>

                <td class="p-3">
                  <div
                    class="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-bold border"
                    :class="site.status === 'approved'
                      ? 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800/50'
                      : site.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800/50'
                        : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-900/30 dark:text-gray-300 dark:border-gray-700/50'"
                  >
                    <Check v-if="site.status === 'approved'" class="w-3 h-3" />
                    {{ site.status === 'approved' ? '已发布' : site.status === 'pending' ? '待审核' : '草稿' }}
                  </div>
                </td>

                <td class="p-3 pr-4">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      class="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-bold border border-red-300 text-red-500 hover:bg-red-50 dark:border-red-500/40 dark:text-red-400 dark:hover:bg-red-900/10 transition-colors disabled:opacity-60"
                      :disabled="isSiteSaving(site.id)"
                      @click="deleteSiteItem(site)"
                    >
                      <Trash2 class="w-4 h-4" />
                      {{ isSiteSaving(site.id) ? '处理中...' : '删除' }}
                    </button>
                    <button
                      class="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-bold border transition-colors"
                      :class="isSiteDirty(site.id) ? 'border-neo-accent text-neo-accent dark:border-term-primary dark:text-term-primary hover:bg-blue-50 dark:hover:bg-term-primary/10' : 'border-gray-200 text-gray-400 dark:border-term-muted/50 dark:text-gray-500 cursor-not-allowed'"
                      :disabled="!isSiteDirty(site.id) || isSiteSaving(site.id)"
                      @click="saveSite(site)"
                    >
                      <Save class="w-4 h-4" />
                      {{ isSiteSaving(site.id) ? '保存中...' : '保存修改' }}
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="!filteredSites.length">
                <td colspan="6" class="p-12 text-center text-gray-500 dark:text-gray-400">
                  <div class="flex flex-col items-center justify-center gap-3">
                    <FolderOpen class="w-12 h-12 opacity-20" />
                    <p class="font-bold text-lg">没有找到相关内容</p>
                    <p class="text-sm opacity-70">尝试调整筛选条件或切换分类。</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="categoryDialog.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="w-full max-w-md bg-white dark:bg-[#111] border border-gray-300 dark:border-term-muted rounded-2xl shadow-xl overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200 dark:border-term-muted flex items-center justify-between">
          <div>
            <h3 class="font-black text-lg">{{ categoryDialog.title }}</h3>
            <p class="text-xs opacity-60 mt-1">分类创建和编辑会立即影响后台可选项与内容归类。</p>
          </div>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-term-muted/20" @click="closeDialog">
            <X class="w-4 h-4" />
          </button>
        </div>

        <div class="p-5 space-y-4">
          <label class="flex flex-col gap-2 text-sm font-bold">
            分类名称
            <input
              v-model="categoryDialog.name"
              type="text"
              class="h-11 px-4 rounded-lg border border-gray-300 dark:border-term-muted bg-white dark:bg-black outline-none focus:border-neo-accent dark:focus:border-term-primary"
              placeholder="输入分类名称"
            />
          </label>

          <label class="flex flex-col gap-2 text-sm font-bold">
            排序值
            <input
              v-model="categoryDialog.sortOrder"
              type="number"
              class="h-11 px-4 rounded-lg border border-gray-300 dark:border-term-muted bg-white dark:bg-black outline-none focus:border-neo-accent dark:focus:border-term-primary"
              placeholder="默认 0，数值越大越靠前"
            />
          </label>
        </div>

        <div class="px-5 py-4 border-t border-gray-200 dark:border-term-muted flex items-center justify-end gap-3 bg-gray-50 dark:bg-black/40">
          <button class="px-4 py-2 rounded-lg border border-gray-300 dark:border-term-muted text-sm font-bold hover:bg-gray-100 dark:hover:bg-term-muted/20" @click="closeDialog">
            取消
          </button>
          <button
            class="px-4 py-2 rounded-lg bg-black text-white dark:bg-term-primary dark:text-black text-sm font-bold hover:opacity-90 disabled:opacity-60"
            :disabled="categorySubmitting"
            @click="submitCategory"
          >
            {{ categorySubmitting ? '提交中...' : '保存分类' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="level2DeleteDialog.open && level2DeleteDialog.category" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="w-full max-w-lg bg-white dark:bg-[#111] border border-gray-300 dark:border-term-muted rounded-2xl shadow-xl overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200 dark:border-term-muted flex items-center justify-between">
          <div>
            <h3 class="font-black text-lg">删除二级分类</h3>
            <p class="text-xs opacity-60 mt-1">分类：{{ level2DeleteDialog.category.name }}</p>
          </div>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-term-muted/20" @click="closeLevel2DeleteDialog">
            <X class="w-4 h-4" />
          </button>
        </div>

        <div class="p-5 space-y-4 text-sm opacity-80">
          <p>请选择删除二级分类时的处理方式：</p>
          <p>仅删除分类：内容保留，但对应二级分类会被清空。</p>
          <p>删除分类并删除内容：该二级分类下的全部内容会一起删除。</p>
        </div>

        <div class="px-5 py-4 border-t border-gray-200 dark:border-term-muted flex items-center justify-end gap-3 bg-gray-50 dark:bg-black/40">
          <button class="px-4 py-2 rounded-lg border border-gray-300 dark:border-term-muted text-sm font-bold hover:bg-gray-100 dark:hover:bg-term-muted/20" @click="closeLevel2DeleteDialog">
            取消
          </button>
          <button
            class="px-4 py-2 rounded-lg border border-gray-300 dark:border-term-muted text-sm font-bold hover:bg-gray-100 dark:hover:bg-term-muted/20 disabled:opacity-60"
            :disabled="level2DeleteDialog.loading"
            @click="deleteLevel2Category(false)"
          >
            仅删除分类
          </button>
          <button
            class="px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-bold hover:opacity-90 disabled:opacity-60"
            :disabled="level2DeleteDialog.loading"
            @click="deleteLevel2Category(true)"
          >
            {{ level2DeleteDialog.loading ? '处理中...' : '分类和内容一起删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 20px;
}

.dark .scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgba(75, 85, 99, 0.5);
}
</style>
