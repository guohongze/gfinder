import { createRouter, createWebHistory } from 'vue-router'
import FileManager from '../views/FileManager.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: FileManager
    },
    {
      path: '/folder/:path*',
      name: 'folder',
      component: FileManager,
      props: true
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

export default router 