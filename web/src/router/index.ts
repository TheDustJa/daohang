import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      title: 'AI 导航网站 - 发现核心工具',
      desc: '收录 AI 工具、平台与站内文章内容。'
    }
  },
  {
    path: '/content/:type/:id',
    name: 'SiteDetail',
    component: () => import('../views/SiteDetail.vue')
  },
  { path: '/submit', name: 'Submit', component: () => import('../views/Submit.vue') },
  { path: '/friend-link', name: 'FriendLink', component: () => import('../views/FriendLink.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    children: [
      { path: '', name: 'AdminDashboard', component: () => import('../views/admin/Dashboard.vue') },
      { path: 'create', name: 'AdminCreate', component: () => import('../views/admin/CreateContent.vue') },
      { path: 'settings', name: 'AdminSettings', component: () => import('../views/admin/Settings.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach(() => {
  window.scrollTo(0, 0)
})

export default router
