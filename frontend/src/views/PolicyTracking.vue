<template>
  <div class="container mx-auto px-4 py-8">
    <!-- ページヘッダー -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">📈 施策効果追跡システム</h1>
      <p class="text-gray-600">鳥取県の政策・施策の効果を定量的に評価し、データ駆動型の政策立案を支援します</p>
    </div>

    <!-- 施策選択・フィルター -->
    <div class="mb-8 bg-white rounded-lg shadow-md p-6">
      <div class="flex flex-wrap items-center gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">施策分野</label>
          <select v-model="selectedCategory" class="border rounded px-3 py-2">
            <option value="">全分野</option>
            <option v-for="category in policyCategories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">対象年度</label>
          <select v-model="selectedYear" class="border rounded px-3 py-2">
            <option v-for="year in availableYears" :key="year" :value="year">
              {{ year }}年度
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ステータス</label>
          <select v-model="selectedStatus" class="border rounded px-3 py-2">
            <option value="">全ステータス</option>
            <option value="計画中">計画中</option>
            <option value="実施中">実施中</option>
            <option value="完了">完了</option>
            <option value="検証中">効果検証中</option>
          </select>
        </div>
        <button @click="applyFilters" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors">
          フィルター適用
        </button>
      </div>
    </div>

    <!-- KPI達成状況ダッシュボード -->
    <div class="mb-8">
      <KPIDashboard :policies="filteredPolicies" />
    </div>

    <!-- 施策一覧と効果分析 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
      <!-- 施策一覧 -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-gray-800">施策一覧</h3>
            <span class="text-sm text-gray-500">{{ filteredPolicies.length }}件</span>
          </div>
          
          <div class="space-y-4">
            <div v-for="policy in filteredPolicies" :key="policy.id" 
                 @click="selectPolicy(policy)"
                 :class="[
                   'p-4 border rounded-lg cursor-pointer transition-all',
                   selectedPolicy?.id === policy.id 
                     ? 'border-blue-500 bg-blue-50' 
                     : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                 ]">
              
              <div class="flex items-start justify-between mb-2">
                <div>
                  <h4 class="font-semibold text-gray-800">{{ policy.name }}</h4>
                  <p class="text-sm text-gray-600">{{ policy.category }} | {{ policy.department }}</p>
                </div>
                <div class="text-right">
                  <span :class="getStatusColor(policy.status)" class="px-2 py-1 text-xs rounded">
                    {{ policy.status }}
                  </span>
                  <p class="text-sm text-gray-500 mt-1">{{ policy.period }}</p>
                </div>
              </div>
              
              <div class="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p class="text-gray-600">予算</p>
                  <p class="font-semibold text-blue-600">{{ policy.budget }}万円</p>
                </div>
                <div>
                  <p class="text-gray-600">KPI達成率</p>
                  <p :class="getAchievementColor(policy.kpiAchievement)" class="font-semibold">
                    {{ policy.kpiAchievement }}%
                  </p>
                </div>
                <div>
                  <p class="text-gray-600">総合評価</p>
                  <p :class="getEvaluationColor(policy.evaluation)" class="font-semibold">
                    {{ policy.evaluation }}
                  </p>
                </div>
              </div>
              
              <div class="mt-3">
                <p class="text-xs text-gray-600">{{ policy.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 選択施策の詳細分析 -->
      <div>
        <PolicyDetailAnalysis :policy="selectedPolicy" v-if="selectedPolicy" />
        <div v-else class="bg-white rounded-lg shadow-md p-6 text-center">
          <div class="text-gray-400 mb-4">
            <svg class="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clip-rule="evenodd" />
            </svg>
          </div>
          <p class="text-gray-500">施策を選択すると詳細分析が表示されます</p>
        </div>
      </div>
    </div>

    <!-- Before/After比較分析 -->
    <div class="mb-8" v-if="selectedPolicy">
      <BeforeAfterAnalysis :policy="selectedPolicy" />
    </div>

    <!-- 他自治体との比較分析 -->
    <div class="mb-8">
      <MunicipalityComparison />
    </div>

    <!-- 課題分析・解決策立案支援 -->
    <div class="mb-8">
      <PolicyRecommendation :currentPolicies="filteredPolicies" />
    </div>
  </div>
</template>

<script>
import KPIDashboard from '@/components/KPIDashboard.vue'
import PolicyDetailAnalysis from '@/components/PolicyDetailAnalysis.vue'
import BeforeAfterAnalysis from '@/components/BeforeAfterAnalysis.vue'
import MunicipalityComparison from '@/components/MunicipalityComparison.vue'
import PolicyRecommendation from '@/components/PolicyRecommendation.vue'

export default {
  name: 'PolicyTracking',
  components: {
    KPIDashboard,
    PolicyDetailAnalysis,
    BeforeAfterAnalysis,
    MunicipalityComparison,
    PolicyRecommendation
  },
  data() {
    return {
      selectedCategory: '',
      selectedYear: '2024',
      selectedStatus: '',
      selectedPolicy: null,
      policyCategories: [
        '人口減少対策', '経済・雇用', '教育・子育て', '医療・福祉',
        'インフラ整備', '地域活性化', '環境・エネルギー', 'DX推進'
      ],
      availableYears: ['2024', '2023', '2022', '2021', '2020'],
      policies: [
        {
          id: 1,
          name: 'UIJターン促進事業',
          category: '人口減少対策',
          department: '総合政策部',
          status: '実施中',
          period: '2023-2025年度',
          budget: 5000,
          kpiAchievement: 75,
          evaluation: 'B',
          description: 'UIJターンによる移住促進と定着支援',
          kpis: [
            { name: '移住者数', target: 100, actual: 75, unit: '人/年' },
            { name: '定着率', target: 80, actual: 85, unit: '%' },
            { name: '就職率', target: 70, actual: 68, unit: '%' }
          ]
        },
        {
          id: 2,
          name: '子育て支援拡充事業',
          category: '教育・子育て',
          department: '子育て・人財局',
          status: '実施中',
          period: '2024-2026年度',
          budget: 8000,
          kpiAchievement: 85,
          evaluation: 'A',
          description: '保育環境整備と子育て世帯への支援強化',
          kpis: [
            { name: '待機児童数', target: 0, actual: 3, unit: '人' },
            { name: '出生率', target: 1.6, actual: 1.58, unit: '' },
            { name: '満足度', target: 80, actual: 88, unit: '%' }
          ]
        },
        {
          id: 3,
          name: 'DX推進プロジェクト',
          category: 'DX推進',
          department: 'デジタル推進課',
          status: '計画中',
          period: '2025-2027年度',
          budget: 12000,
          kpiAchievement: 0,
          evaluation: '-',
          description: 'デジタル技術を活用した行政サービス向上',
          kpis: [
            { name: 'オンライン手続き率', target: 60, actual: 35, unit: '%' },
            { name: 'システム稼働率', target: 99.5, actual: 98.2, unit: '%' },
            { name: '利用者満足度', target: 85, actual: 0, unit: '%' }
          ]
        },
        {
          id: 4,
          name: '地域産業振興事業',
          category: '経済・雇用',
          department: '商工労働部',
          status: '完了',
          period: '2022-2024年度',
          budget: 15000,
          kpiAchievement: 90,
          evaluation: 'A',
          description: '地場産業の競争力強化と新産業創出',
          kpis: [
            { name: '新規雇用創出', target: 200, actual: 185, unit: '人' },
            { name: '売上向上率', target: 15, actual: 18, unit: '%' },
            { name: '企業満足度', target: 80, actual: 92, unit: '%' }
          ]
        }
      ]
    }
  },
  computed: {
    filteredPolicies() {
      return this.policies.filter(policy => {
        const categoryMatch = !this.selectedCategory || policy.category === this.selectedCategory
        const yearMatch = policy.period.includes(this.selectedYear)
        const statusMatch = !this.selectedStatus || policy.status === this.selectedStatus
        
        return categoryMatch && yearMatch && statusMatch
      })
    }
  },
  methods: {
    applyFilters() {
      // フィルター適用時の処理（必要に応じて）
    },
    selectPolicy(policy) {
      this.selectedPolicy = policy
    },
    getStatusColor(status) {
      switch(status) {
        case '計画中': return 'bg-yellow-100 text-yellow-800'
        case '実施中': return 'bg-blue-100 text-blue-800'
        case '完了': return 'bg-green-100 text-green-800'
        case '検証中': return 'bg-purple-100 text-purple-800'
        default: return 'bg-gray-100 text-gray-800'
      }
    },
    getAchievementColor(achievement) {
      if (achievement >= 80) return 'text-green-600'
      if (achievement >= 60) return 'text-yellow-600'
      if (achievement > 0) return 'text-red-600'
      return 'text-gray-500'
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
    }
  }
}
</script>

<style scoped>
/* カスタムスタイル */
</style>