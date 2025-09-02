import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import PopulationTrend from '../views/PopulationTrend.vue'
import LivabilityComparison from '../views/LivabilityComparison.vue'
import PopulationDetail from '../views/PopulationDetail.vue'
import LivabilityConfiguration from '../views/LivabilityConfiguration.vue'
import PolicyTracking from '../views/PolicyTracking.vue'
import Employment from '../views/Employment.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Dashboard
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
  },
  {
    path: '/livability-configuration',
    name: 'LivabilityConfiguration',
    component: LivabilityConfiguration
  },
  {
    path: '/policy-tracking',
    name: 'PolicyTracking',
    component: PolicyTracking
  },
  {
    path: '/employment',
    name: 'Employment',
    component: Employment
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('../views/Map.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router