import { createRouter, createWebHistory } from 'vue-router'

const SITE_NAME = 'AI 导航站'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      title: `${SITE_NAME} - 发现核心 AI 工具`,
      description: '收录优质 AI 工具、平台与站内文章，一站式 AI 资源导航。'
    }
  },
  {
    path: '/content/:type/:id',
    name: 'SiteDetail',
    component: () => import('../views/SiteDetail.vue'),
    meta: {
      title: `内容详情 - ${SITE_NAME}`,
      description: '查看 AI 工具或文章的详细信息。'
    }
  },
  {
    path: '/articles',
    name: 'Articles',
    component: () => import('../views/Articles.vue'),
    meta: {
      title: `文章专区 - ${SITE_NAME}`,
      description: '浏览 AI 相关的技术文章、评测和教程。'
    }
  },
  {
    path: '/tags',
    name: 'Tags',
    component: () => import('../views/Tags.vue'),
    meta: {
      title: `标签云 - ${SITE_NAME}`,
      description: '通过标签发现和筛选 AI 工具与文章。'
    }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/Favorites.vue'),
    meta: {
      title: `我的收藏 - ${SITE_NAME}`,
      description: '查看您收藏的 AI 工具和文章。'
    }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: {
      title: `浏览历史 - ${SITE_NAME}`,
      description: '查看您最近浏览的 AI 工具和文章。'
    }
  },
  {
    path: '/submit',
    name: 'Submit',
    component: () => import('../views/Submit.vue'),
    meta: {
      title: `提交收录 - ${SITE_NAME}`,
      description: '提交优质 AI 网站，通过审核后即可展示在导航站。'
    }
  },
  {
    path: '/friend-link',
    name: 'FriendLink',
    component: () => import('../views/FriendLink.vue'),
    meta: {
      title: `友链申请 - ${SITE_NAME}`,
      description: '申请互换友情链接，与优质 AI 站点共同成长。'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: `管理登录 - ${SITE_NAME}`,
      description: '管理员登录入口。',
      robots: 'noindex, nofollow'
    }
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { robots: 'noindex, nofollow' },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: `管理后台 - ${SITE_NAME}`, robots: 'noindex, nofollow' }
      },
      {
        path: 'create',
        name: 'AdminCreate',
        component: () => import('../views/admin/CreateContent.vue'),
        meta: { title: `发布内容 - ${SITE_NAME}`, robots: 'noindex, nofollow' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('../views/admin/Settings.vue'),
        meta: { title: `系统设置 - ${SITE_NAME}`, robots: 'noindex, nofollow' }
      }
    ]
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: {
      title: `关于我们 - ${SITE_NAME}`,
      description: 'AI 导航站简介，了解我们的使命和特色功能。'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: `404 - ${SITE_NAME}` }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  const title = (to.meta?.title as string) || `${SITE_NAME}`
  document.title = title

  const descMeta = document.querySelector('meta[name="description"]')
  if (descMeta && to.meta?.description) {
    descMeta.setAttribute('content', to.meta.description as string)
  }

  const robotsMeta = document.querySelector('meta[name="robots"]')
  if (to.meta?.robots) {
    if (!robotsMeta) {
      const meta = document.createElement('meta')
      meta.name = 'robots'
      meta.content = to.meta.robots as string
      document.head.appendChild(meta)
    } else {
      robotsMeta.setAttribute('content', to.meta.robots as string)
    }
  } else if (robotsMeta) {
    robotsMeta.setAttribute('content', 'index, follow')
  }

  window.scrollTo(0, 0)
})

export default router
