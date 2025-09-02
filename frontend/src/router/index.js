import { createRouter, createWebHistory } from 'vue-router'
import App from '../App.vue'
import PopulationTrend from '../views/PopulationTrend.vue'
import LivabilityComparison from '../views/LivabilityComparison.vue'
import PopulationDetail from '../views/PopulationDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: App
  },
  {
    path: '/population',
    name: 'Population',
    component: PopulationTrend
  },
  {
    path: '/livability-comparison',
    name: 'LivabilityComparison',
    component: LivabilityComparison
  },
  {
    path: '/population-detail',
    name: 'PopulationDetail',
    component: PopulationDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router