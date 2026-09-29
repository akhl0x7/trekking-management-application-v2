import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import App from './App.vue'
import { routes } from './router'
import { auth } from './stores/auth'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach(async (to) => {
  await auth.load()
  if (to.meta.requiresAuth && !auth.user) return '/login'
  if ((to.path === '/login' || to.path === '/register') && auth.user) return '/dashboard'
  if (to.meta.role && auth.user?.role !== to.meta.role) return '/dashboard'
  return true
})

createApp(App).use(router).mount('#app')
