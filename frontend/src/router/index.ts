import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
  { path: '/filters', name: 'FilterConfig', component: () => import('@/pages/FilterConfig.vue') },
  { path: '/filters/:id/results', name: 'FilterResults', component: () => import('@/pages/FilterResults.vue') },
  { path: '/analysis/:id', name: 'AnalysisProcess', component: () => import('@/pages/AnalysisProcess.vue') },
  { path: '/reverse/:id', name: 'ReverseProcess', component: () => import('@/pages/ReverseProcess.vue') },
  { path: '/replay/:id', name: 'ReplayView', component: () => import('@/pages/ReplayView.vue') },
  { path: '/history', name: 'History', component: () => import('@/pages/History.vue') },
  { path: '/whales', name: 'WhaleLibrary', component: () => import('@/pages/WhaleLibrary.vue') },
  { path: '/settings', name: 'Settings', component: () => import('@/pages/Settings.vue') },
  { path: '/recommend', name: 'SmartRecommend', component: () => import('@/pages/SmartRecommend.vue') },
  { path: '/landing', name: 'Landing', component: () => import('@/pages/Landing.vue') },
  { path: '/embed', name: 'Embed', component: () => import('@/pages/EmbedPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
