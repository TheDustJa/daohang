<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Check, Link2, Settings, Trash2, X } from 'lucide-vue-next'
import { Toast } from '../../utils/toast'
import {
  deleteAdminFriendLink,
  deleteAdminSite,
  fetchAdminFriendLinks,
  fetchAdminSites,
  updateAdminFriendLink,
  updateAdminSite,
  updateAdminPassword,
  type FriendLink,
  type Site
} from '../../api/sites'

const siteSubmissions = ref<Site[]>([])
const friendLinks = ref<FriendLink[]>([])
const loading = ref(false)
const busyKey = ref('')

const pwdForm = ref({
  oldPass: '',
  newPass: ''
})

const pendingSiteSubmissions = computed(() => siteSubmissions.value.filter(item => item.status === 'pending'))
const pendingFriendLinks = computed(() => friendLinks.value.filter(item => item.status === 'pending'))

const loadData = async () => {
  loading.value = true
  try {
    const [sites, links] = await Promise.all([
      fetchAdminSites('pending'),
      fetchAdminFriendLinks()
    ])
    siteSubmissions.value = sites
    friendLinks.value = links
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '审核数据加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

const approveSite = async (site: Site) => {
  busyKey.value = `site-approve-${site.id}`
  try {
    await updateAdminSite(site.id, {
      type: site.type || 'site',
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
      content: site.content || '',
      contentFormat: site.contentFormat || 'html',
      status: 'approved'
    })
    Toast.success(`已通过站点：${site.name}`)
    await loadData()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '网站审核失败')
  } finally {
    busyKey.value = ''
  }
}

const deleteSiteSubmission = async (site: Site) => {
  if (!window.confirm(`确定删除提交的网站“${site.name}”吗？`)) return

  busyKey.value = `site-delete-${site.id}`
  try {
    await deleteAdminSite(site.id, site.type || 'site')
    Toast.success('网站提交已删除')
    await loadData()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '删除网站提交失败')
  } finally {
    busyKey.value = ''
  }
}

const approveFriendLink = async (item: FriendLink) => {
  busyKey.value = `friend-approve-${item.id}`
  try {
    await updateAdminFriendLink(item.id, 'approved')
    Toast.success(`已通过友链：${item.siteName}`)
    await loadData()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '友链审核失败')
  } finally {
    busyKey.value = ''
  }
}

const rejectFriendLink = async (item: FriendLink) => {
  busyKey.value = `friend-reject-${item.id}`
  try {
    await updateAdminFriendLink(item.id, 'rejected')
    Toast.success('友链申请已标记为拒绝')
    await loadData()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '友链申请处理失败')
  } finally {
    busyKey.value = ''
  }
}

const deleteFriendLinkItem = async (item: FriendLink) => {
  if (!window.confirm(`确定删除友链申请“${item.siteName}”吗？`)) return

  busyKey.value = `friend-delete-${item.id}`
  try {
    await deleteAdminFriendLink(item.id)
    Toast.success('友链申请已删除')
    await loadData()
  } catch (error: any) {
    Toast.error(error?.response?.data?.detail || '删除友链申请失败')
  } finally {
    busyKey.value = ''
  }
}

const handleUpdatePassword = async () => {
  if (!pwdForm.value.oldPass.trim() || !pwdForm.value.newPass.trim()) {
    Toast.error('请输入旧密码和新密码')
    return
  }
  busyKey.value = 'password-update'
  try {
    await updateAdminPassword(pwdForm.value.oldPass, pwdForm.value.newPass)
    Toast.success('密码修改成功，请重新登录')
    pwdForm.value.oldPass = ''
    pwdForm.value.newPass = ''
    // Optionally log out after a moment 
    // setTimeout(() => router.push('/login'), 1500)
  } catch (error: any) {
     Toast.error(error?.response?.data?.detail || '密码修改失败')
  } finally {
     busyKey.value = ''
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto pb-20 space-y-8">
    <section class="rounded-2xl border border-gray-300 dark:border-term-muted bg-white dark:bg-[#111] shadow-sm overflow-hidden">
      <div class="px-6 py-5 border-b border-gray-200 dark:border-term-muted bg-gray-50 dark:bg-black/40">
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 rounded-xl bg-black text-white dark:bg-term-primary dark:text-black flex items-center justify-center">
            <Settings class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-2xl font-black uppercase">系统设置</h2>
            <p class="text-sm opacity-60 mt-1">这里专门处理前台提交进来的申请数据，避免和内容新增页重复。</p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-6 bg-gray-50 dark:bg-black/20">
        <div class="rounded-xl border border-gray-200 dark:border-term-muted bg-white dark:bg-black/30 p-5">
          <div class="text-xs opacity-60 font-bold uppercase">待审核网站</div>
          <div class="text-3xl font-black mt-2">{{ pendingSiteSubmissions.length }}</div>
        </div>
        <div class="rounded-xl border border-gray-200 dark:border-term-muted bg-white dark:bg-black/30 p-5">
          <div class="text-xs opacity-60 font-bold uppercase">待审核友链</div>
          <div class="text-3xl font-black mt-2">{{ pendingFriendLinks.length }}</div>
        </div>
      </div>
    </section>

    <!-- Password update section -->
    <section class="rounded-2xl border border-gray-300 dark:border-term-muted bg-white dark:bg-[#111] shadow-sm overflow-hidden">
      <div class="px-6 py-5 border-b border-gray-200 dark:border-term-muted bg-gray-50 dark:bg-black/40">
        <div class="flex items-center gap-2">
          <Settings class="w-5 h-5" />
          <div>
            <h3 class="text-xl font-black uppercase">修改密码</h3>
            <p class="text-sm opacity-60 mt-1">修改管理员登录密码</p>
          </div>
        </div>
      </div>
      <div class="p-6">
         <form @submit.prevent="handleUpdatePassword" class="space-y-4 max-w-sm">
            <div>
              <label class="block text-sm font-bold opacity-80 mb-1">旧密码</label>
              <input type="password" v-model="pwdForm.oldPass" placeholder="输入当前密码" class="w-full px-3 py-2 bg-transparent border-2 rounded focus:outline-none focus:border-neo-accent dark:focus:border-term-primary transition-colors" required>
            </div>
            <div>
              <label class="block text-sm font-bold opacity-80 mb-1">新密码</label>
              <input type="password" v-model="pwdForm.newPass" placeholder="输入新密码" class="w-full px-3 py-2 bg-transparent border-2 rounded focus:outline-none focus:border-neo-accent dark:focus:border-term-primary transition-colors" required>
            </div>
            <button type="submit" class="w-full btn-primary h-10 px-4 rounded font-bold" :disabled="busyKey === 'password-update'">
               {{ busyKey === 'password-update' ? '修改中...' : '确认修改' }}
            </button>
         </form>
      </div>
    </section>

    <div v-if="loading" class="rounded-2xl border border-gray-300 dark:border-term-muted bg-white dark:bg-[#111] p-8 text-sm opacity-60">
      正在加载审核数据...
    </div>

    <template v-else>
      <section class="rounded-2xl border border-gray-300 dark:border-term-muted bg-white dark:bg-[#111] shadow-sm overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-200 dark:border-term-muted flex items-center justify-between bg-gray-50 dark:bg-black/40">
          <div>
            <h3 class="text-xl font-black uppercase">提交的网站申请</h3>
            <p class="text-sm opacity-60 mt-1">处理 `/submit` 过来的待审核网站。</p>
          </div>
          <button class="px-4 py-2 text-sm font-bold border border-gray-300 dark:border-term-muted rounded-lg hover:bg-gray-100 dark:hover:bg-term-muted/20" @click="loadData">
            刷新
          </button>
        </div>

        <div v-if="!siteSubmissions.length" class="p-6 text-sm opacity-60">当前没有待审核的网站提交。</div>
        <div v-else class="divide-y divide-gray-200 dark:divide-term-muted/30">
          <article v-for="site in siteSubmissions" :key="site.id" class="p-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div class="space-y-2 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="text-lg font-black">{{ site.name }}</h4>
                <span class="px-2 py-0.5 rounded-full text-xs font-bold border border-yellow-300 text-yellow-700 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-700/40">
                  待审核
                </span>
              </div>
              <a :href="site.url" target="_blank" rel="noreferrer" class="text-sm text-blue-600 hover:underline break-all">{{ site.url }}</a>
              <div class="text-sm font-bold opacity-80">{{ site.level1 }} / {{ site.level2 }}</div>
              <p class="text-sm opacity-70">{{ site.description || '暂无描述' }}</p>
            </div>

            <div class="flex items-center gap-3 shrink-0">
              <button
                class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 text-white text-sm font-bold hover:opacity-90 disabled:opacity-60"
                :disabled="busyKey === `site-approve-${site.id}`"
                @click="approveSite(site)"
              >
                <Check class="w-4 h-4" />
                {{ busyKey === `site-approve-${site.id}` ? '处理中...' : '通过' }}
              </button>
              <button
                class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-red-400 text-red-500 text-sm font-bold hover:bg-red-50 dark:hover:bg-red-900/10 disabled:opacity-60"
                :disabled="busyKey === `site-delete-${site.id}`"
                @click="deleteSiteSubmission(site)"
              >
                <Trash2 class="w-4 h-4" />
                {{ busyKey === `site-delete-${site.id}` ? '删除中...' : '删除' }}
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="rounded-2xl border border-gray-300 dark:border-term-muted bg-white dark:bg-[#111] shadow-sm overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-200 dark:border-term-muted bg-gray-50 dark:bg-black/40">
          <div class="flex items-center gap-2">
            <Link2 class="w-5 h-5" />
            <div>
              <h3 class="text-xl font-black uppercase">友情链接申请</h3>
              <p class="text-sm opacity-60 mt-1">通过后会自动展示到前台页脚友情链接区域。</p>
            </div>
          </div>
        </div>

        <div v-if="!friendLinks.length" class="p-6 text-sm opacity-60">当前没有友链申请记录。</div>
        <div v-else class="divide-y divide-gray-200 dark:divide-term-muted/30">
          <article v-for="item in friendLinks" :key="item.id" class="p-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div class="space-y-2 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="text-lg font-black">{{ item.siteName }}</h4>
                <span
                  class="px-2 py-0.5 rounded-full text-xs font-bold border"
                  :class="item.status === 'approved'
                    ? 'border-green-300 text-green-700 bg-green-50 dark:bg-green-900/20 dark:text-green-300 dark:border-green-700/40'
                    : item.status === 'rejected'
                      ? 'border-red-300 text-red-700 bg-red-50 dark:bg-red-900/20 dark:text-red-300 dark:border-red-700/40'
                      : 'border-yellow-300 text-yellow-700 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-700/40'"
                >
                  {{ item.status === 'approved' ? '已通过' : item.status === 'rejected' ? '已拒绝' : '待审核' }}
                </span>
              </div>
              <a :href="item.siteUrl" target="_blank" rel="noreferrer" class="text-sm text-blue-600 hover:underline break-all">{{ item.siteUrl }}</a>
              <div class="text-sm opacity-80">联系邮箱：{{ item.contactEmail }}</div>
              <p class="text-sm opacity-70">{{ item.siteDesc || '暂无描述' }}</p>
            </div>

            <div class="flex items-center gap-3 shrink-0 flex-wrap">
              <button
                class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 text-white text-sm font-bold hover:opacity-90 disabled:opacity-60"
                :disabled="busyKey === `friend-approve-${item.id}` || item.status === 'approved'"
                @click="approveFriendLink(item)"
              >
                <Check class="w-4 h-4" />
                {{ busyKey === `friend-approve-${item.id}` ? '处理中...' : '通过' }}
              </button>
              <button
                class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-yellow-400 text-yellow-600 text-sm font-bold hover:bg-yellow-50 dark:hover:bg-yellow-900/10 disabled:opacity-60"
                :disabled="busyKey === `friend-reject-${item.id}` || item.status === 'rejected'"
                @click="rejectFriendLink(item)"
              >
                <X class="w-4 h-4" />
                {{ busyKey === `friend-reject-${item.id}` ? '处理中...' : '拒绝' }}
              </button>
              <button
                class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-red-400 text-red-500 text-sm font-bold hover:bg-red-50 dark:hover:bg-red-900/10 disabled:opacity-60"
                :disabled="busyKey === `friend-delete-${item.id}`"
                @click="deleteFriendLinkItem(item)"
              >
                <Trash2 class="w-4 h-4" />
                {{ busyKey === `friend-delete-${item.id}` ? '删除中...' : '删除' }}
              </button>
            </div>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>
