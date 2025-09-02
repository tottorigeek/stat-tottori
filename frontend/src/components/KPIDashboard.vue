<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-800">KPI達成状況ダッシュボード</h3>
      <div class="flex items-center space-x-4">
        <div class="text-sm text-gray-500">
          対象施策: {{ policies.length }}件
        </div>
        <button @click="toggleView" class="text-blue-600 hover:text-blue-800 text-sm">
          {{ viewMode === 'summary' ? '詳細表示' : 'サマリー表示' }}
        </button>
      </div>
    </div>

    <!-- サマリー表示 -->
    <div v-if="viewMode === 'summary'">
      <!-- 全体達成状況 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="text-center p-4 bg-green-50 rounded-lg border border-green-200">
          <div class="text-2xl font-bold text-green-600 mb-1">{{ overallStats.excellent }}件</div>
          <div class="text-sm text-green-700">優秀 (80%以上)</div>
          <div class="text-xs text-gray-500 mt-1">{{ Math.round(overallStats.excellent / policies.length * 100) }}%</div>
        </div>
        
        <div class="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div class="text-2xl font-bold text-blue-600 mb-1">{{ overallStats.good }}件</div>
          <div class="text-sm text-blue-700">良好 (60-79%)</div>
          <div class="text-xs text-gray-500 mt-1">{{ Math.round(overallStats.good / policies.length * 100) }}%</div>
        </div>
        
        <div class="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
          <div class="text-2xl font-bold text-orange-600 mb-1">{{ overallStats.needs_improvement }}件</div>
          <div class="text-sm text-orange-700">要改善 (40-59%)</div>
          <div class="text-xs text-gray-500 mt-1">{{ Math.round(overallStats.needs_improvement / policies.length * 100) }}%</div>
        </div>
        
        <div class="text-center p-4 bg-red-50 rounded-lg border border-red-200">
          <div class="text-2xl font-bold text-red-600 mb-1">{{ overallStats.poor }}件</div>
          <div class="text-sm text-red-700">不十分 (40%未満)</div>
          <div class="text-xs text-gray-500 mt-1">{{ Math.round(overallStats.poor / policies.length * 100) }}%</div>
        </div>
      </div>

      <!-- 分野別達成率 -->
      <div class="mb-8">
        <h4 class="text-lg font-semibold text-gray-800 mb-4">分野別達成状況</h4>
        <div class="space-y-4">
          <div v-for="category in categoryStats" :key="category.name" class="flex items-center justify-between p-4 bg-gray-50 rounded">
            <div>
              <p class="font-medium text-gray-800">{{ category.name }}</p>
              <p class="text-sm text-gray-600">{{ category.policyCount }}施策</p>
            </div>
            <div class="flex items-center">
              <div class="w-32 bg-gray-200 rounded-full h-3 mr-4">
                <div :class="getAchievementBarColor(category.avgAchievement)" 
                     class="h-3 rounded-full transition-all duration-500" 
                     :style="{ width: category.avgAchievement + '%' }">
                </div>
              </div>
              <div class="text-right">
                <p :class="getAchievementColor(category.avgAchievement)" class="font-bold text-lg">
                  {{ Math.round(category.avgAchievement) }}%
                </p>
                <p class="text-xs text-gray-500">平均達成率</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- トップ/ボトム施策 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 高達成率施策 -->
        <div>
          <h4 class="text-lg font-semibold text-gray-800 mb-4">📈 高達成率施策 TOP3</h4>
          <div class="space-y-3">
            <div v-for="policy in topPerformingPolicies" :key="policy.id" class="p-3 bg-green-50 border border-green-200 rounded">
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-medium text-gray-800">{{ policy.name }}</p>
                  <p class="text-sm text-gray-600">{{ policy.category }}</p>
                </div>
                <div class="text-right">
                  <p class="text-lg font-bold text-green-600">{{ policy.kpiAchievement }}%</p>
                  <p class="text-xs text-gray-500">達成率</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 要改善施策 -->
        <div>
          <h4 class="text-lg font-semibold text-gray-800 mb-4">⚠️ 要改善施策</h4>
          <div class="space-y-3">
            <div v-for="policy in underPerformingPolicies" :key="policy.id" class="p-3 bg-orange-50 border border-orange-200 rounded">
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-medium text-gray-800">{{ policy.name }}</p>
                  <p class="text-sm text-gray-600">{{ policy.category }}</p>
                </div>
                <div class="text-right">
                  <p class="text-lg font-bold text-orange-600">{{ policy.kpiAchievement }}%</p>
                  <p class="text-xs text-gray-500">達成率</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 詳細表示 -->
    <div v-else>
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="text-left py-3 px-2 font-semibold text-gray-800">施策名</th>
              <th class="text-left py-3 px-2 font-semibold text-gray-800">分野</th>
              <th class="text-center py-3 px-2 font-semibold text-gray-800">予算(万円)</th>
              <th class="text-center py-3 px-2 font-semibold text-gray-800">KPI数</th>
              <th class="text-center py-3 px-2 font-semibold text-gray-800">達成率</th>
              <th class="text-center py-3 px-2 font-semibold text-gray-800">評価</th>
              <th class="text-center py-3 px-2 font-semibold text-gray-800">ステータス</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="policy in policies" :key="policy.id" class="border-b border-gray-100 hover:bg-gray-50">
              <td class="py-3 px-2">
                <div>
                  <p class="font-medium text-gray-800">{{ policy.name }}</p>
                  <p class="text-xs text-gray-500">{{ policy.department }}</p>
                </div>
              </td>
              <td class="py-3 px-2 text-sm text-gray-600">{{ policy.category }}</td>
              <td class="py-3 px-2 text-center text-sm">{{ policy.budget?.toLocaleString() }}</td>
              <td class="py-3 px-2 text-center text-sm">{{ policy.kpis?.length || 0 }}</td>
              <td class="py-3 px-2 text-center">
                <span :class="getAchievementColor(policy.kpiAchievement)" class="font-semibold">
                  {{ policy.kpiAchievement }}%
                </span>
              </td>
              <td class="py-3 px-2 text-center">
                <span :class="getEvaluationColor(policy.evaluation)" class="font-semibold">
                  {{ policy.evaluation }}
                </span>
              </td>
              <td class="py-3 px-2 text-center">
                <span :class="getStatusColor(policy.status)" class="px-2 py-1 text-xs rounded">
                  {{ policy.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- データ更新時刻 -->
    <div class="mt-6 pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500">データ更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KPIDashboard',
  props: {
    policies: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      viewMode: 'summary', // 'summary' or 'detailed'
      lastUpdated: ''
    }
  },
  computed: {
    overallStats() {
      const stats = {
        excellent: 0,
        good: 0,
        needs_improvement: 0,
        poor: 0
      }
      
      this.policies.forEach(policy => {
        const achievement = policy.kpiAchievement
        if (achievement >= 80) stats.excellent++
        else if (achievement >= 60) stats.good++
        else if (achievement >= 40) stats.needs_improvement++
        else stats.poor++
      })
      
      return stats
    },
    categoryStats() {
      const categories = {}
      
      this.policies.forEach(policy => {
        if (!categories[policy.category]) {
          categories[policy.category] = {
            name: policy.category,
            policyCount: 0,
            totalAchievement: 0
          }
        }
        categories[policy.category].policyCount++
        categories[policy.category].totalAchievement += policy.kpiAchievement
      })
      
      return Object.values(categories).map(category => ({
        ...category,
        avgAchievement: category.totalAchievement / category.policyCount
      })).sort((a, b) => b.avgAchievement - a.avgAchievement)
    },
    topPerformingPolicies() {
      return [...this.policies]
        .sort((a, b) => b.kpiAchievement - a.kpiAchievement)
        .slice(0, 3)
    },
    underPerformingPolicies() {
      return [...this.policies]
        .filter(policy => policy.kpiAchievement < 60)
        .sort((a, b) => a.kpiAchievement - b.kpiAchievement)
        .slice(0, 3)
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 300000) // 5分ごと更新
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.lastUpdated = now.toLocaleString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    toggleView() {
      this.viewMode = this.viewMode === 'summary' ? 'detailed' : 'summary'
    },
    getAchievementColor(achievement) {
      if (achievement >= 80) return 'text-green-600'
      if (achievement >= 60) return 'text-blue-600'
      if (achievement >= 40) return 'text-orange-600'
      return 'text-red-600'
    },
    getAchievementBarColor(achievement) {
      if (achievement >= 80) return 'bg-green-500'
      if (achievement >= 60) return 'bg-blue-500'
      if (achievement >= 40) return 'bg-orange-500'
      return 'bg-red-500'
    },
    getEvaluationColor(evaluation) {
      switch(evaluation) {
        case 'S': return 'text-purple-600'
        case 'A': return 'text-green-600'
        case 'B': return 'text-blue-600'
        case 'C': return 'text-orange-600'
        case 'D': return 'text-red-600'
        default: return 'text-gray-500'
      }
    },
    getStatusColor(status) {
      switch(status) {
        case '計画中': return 'bg-yellow-100 text-yellow-800'
        case '実施中': return 'bg-blue-100 text-blue-800'
        case '完了': return 'bg-green-100 text-green-800'
        case '検証中': return 'bg-purple-100 text-purple-800'
        default: return 'bg-gray-100 text-gray-800'
      }
    }
  }
}
</script>

<style scoped>
/* カスタムスタイル */
</style>