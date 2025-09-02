<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-800">📊 政策詳細分析</h3>
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-500">評価:</span>
        <span :class="getEvaluationClass(policy.evaluation)" class="px-3 py-1 rounded-full text-sm font-semibold">
          {{ policy.evaluation }}
        </span>
      </div>
    </div>

    <!-- 政策基本情報 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <div>
        <h4 class="font-semibold text-gray-700 mb-2">政策名</h4>
        <p class="text-lg text-gray-800">{{ policy.name }}</p>
      </div>
      <div>
        <h4 class="font-semibold text-gray-700 mb-2">担当部署</h4>
        <p class="text-gray-800">{{ policy.department }}</p>
      </div>
      <div>
        <h4 class="font-semibold text-gray-700 mb-2">実施期間</h4>
        <p class="text-gray-800">{{ policy.period }}</p>
      </div>
      <div>
        <h4 class="font-semibold text-gray-700 mb-2">予算</h4>
        <p class="text-gray-800">{{ policy.budget.toLocaleString() }}万円</p>
      </div>
    </div>

    <!-- 政策説明 -->
    <div class="mb-6">
      <h4 class="font-semibold text-gray-700 mb-2">政策概要</h4>
      <p class="text-gray-800">{{ policy.description }}</p>
    </div>

    <!-- KPI達成状況 -->
    <div class="mb-6">
      <h4 class="font-semibold text-gray-700 mb-4">KPI達成状況</h4>
      <div class="space-y-4">
        <div v-for="kpi in policy.kpis" :key="kpi.name" class="bg-gray-50 rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <h5 class="font-medium text-gray-700">{{ kpi.name }}</h5>
            <span class="text-sm text-gray-500">{{ kpi.unit }}</span>
          </div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">目標: {{ kpi.target }}</span>
            <span class="text-sm text-gray-600">実績: {{ kpi.actual }}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all duration-300"
              :class="getKPIProgressClass(kpi.actual, kpi.target)"
              :style="{ width: Math.min((kpi.actual / kpi.target) * 100, 100) + '%' }"
            ></div>
          </div>
          <div class="text-right mt-1">
            <span class="text-sm font-medium" :class="getKPIProgressClass(kpi.actual, kpi.target)">
              {{ Math.round((kpi.actual / kpi.target) * 100) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 総合評価 -->
    <div class="bg-blue-50 rounded-lg p-4">
      <h4 class="font-semibold text-blue-800 mb-2">総合評価</h4>
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-blue-600">KPI達成率</p>
          <p class="text-2xl font-bold text-blue-800">{{ policy.kpiAchievement }}%</p>
        </div>
        <div class="text-right">
          <p class="text-sm text-blue-600">評価ランク</p>
          <span :class="getEvaluationClass(policy.evaluation)" class="text-2xl font-bold px-4 py-2 rounded-full">
            {{ policy.evaluation }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PolicyDetailAnalysis',
  props: {
    policy: {
      type: Object,
      required: true
    }
  },
  methods: {
    getEvaluationClass(evaluation) {
      switch (evaluation) {
        case 'A':
          return 'bg-green-100 text-green-800'
        case 'B':
          return 'bg-blue-100 text-blue-800'
        case 'C':
          return 'bg-yellow-100 text-yellow-800'
        case 'D':
          return 'bg-red-100 text-red-800'
        default:
          return 'bg-gray-100 text-gray-800'
      }
    },
    getKPIProgressClass(actual, target) {
      const ratio = actual / target
      if (ratio >= 1) return 'bg-green-500'
      if (ratio >= 0.8) return 'bg-blue-500'
      if (ratio >= 0.6) return 'bg-yellow-500'
      return 'bg-red-500'
    }
  }
}
</script>

<style scoped>
/* 必要に応じてカスタムスタイルを追加 */
</style>
