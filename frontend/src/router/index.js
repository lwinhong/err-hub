import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Projects from '../views/Projects.vue'
import ProjectErrors from '../views/ProjectErrors.vue'
import ErrorDetail from '../views/ErrorDetail.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import Users from '../views/admin/Users.vue'
import Settings from '../views/admin/Settings.vue'
import PushManagement from '../views/admin/PushManagement.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:id/errors',
    name: 'ProjectErrors',
    component: ProjectErrors,
    meta: { requiresAuth: true }
  },
  {
    path: '/errors/:id',
    name: 'ErrorDetail',
    component: ErrorDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/users',
    children: [
      {
        path: 'users',
        name: 'AdminUsers',
        component: Users,
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: Settings,
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'push',
        name: 'AdminPush',
        component: PushManagement,
        meta: { requiresAuth: true, requiresAdmin: true }
      }
    ]
  },
  {
    path: '/users',
    redirect: '/admin/users'
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach(async (to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return { name: 'Login' }
  }
  if (to.name === 'Login' && token) {
    return { name: 'Dashboard' }
  }
  if (to.meta.requiresAdmin && token) {
    // 确保用户信息已加载
    const { useAuthStore } = await import('../stores/auth')
    const authStore = useAuthStore()
    if (!authStore.user) {
      await authStore.fetchUser()
    }
    if (!authStore.isAdmin) {
      return { name: 'Dashboard' }
    }
  }
})

export default router
