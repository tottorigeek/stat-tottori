<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-800">🏘️ 他自治体との比較分析</h3>
      <div class="flex items-center space-x-4">
        <select v-model="selectedComparison" class="border rounded px-3 py-2 text-sm">
          <option value="similar">類似自治体</option>
          <option value="neighboring">近隣自治体</option>
          <option value="successful">成功事例</option>
          <option value="all">全国平均</option>
        </select>
        <select v-model="selectedMetric" class="border rounded px-3 py-2 text-sm">
          <option value="population">人口動態</option>
          <option value="economy">経済指標</option>
          <option value="welfare">社会保障</option>
          <option value="education">教育</option>
          <option value="infrastructure">インフラ</option>
        </select>
      </div>
    </div>

    <!-- 比較サマリー --><div class="mb-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div class="text-2xl mb-2">🏔️</div>
          <h4 class="font-semibold text-gray-800">鳥取県</h4>
          <p class="text-2xl font-bold text-blue-600">{{ tottoriScore }}</p>
          <p class="text-xs text-gray-500">{{ getScoreLabel(tottoriScore) }}</p>
        </div>
        
        <div v-for="municipality in comparisonMunicipalities" :key="municipality.name" 
             class="text-center p-4 bg-gray-50 rounded-lg border">
          <div class="text-2xl mb-2">{{ municipality.icon }}</div>
          <h4 class="font-semibold text-gray-800">{{ municipality.name }}</h4>
          <p :class="getScoreColor(municipality.score)" class="text-2xl font-bold">
            {{ municipality.score }}
          </p>
          <p class="text-xs text-gray-500">{{ getScoreLabel(municipality.score) }}</p>
        </div>
      </div>

      <!-- 順位・ランキング表示 -->
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <h5 class="font-semibold text-gray-800">{{ getMetricTitle() }}ランキング</h5>
          <span class="text-sm text-gray-500">対象: {{ getComparisonTitle() }}</span>
        </div>
        <div class="space-y-2">
          <div v-for="(item, index) in rankingData" :key="item.name" 
               :class="[
                 'flex items-center justify-between p-2 rounded',
                 item.name === '鳥取県' ? 'bg-blue-100 border border-blue-300' : 'bg-white'
               ]">
            <div class="flex items-center">
              <span :class="getRankColor(index + 1)" class="font-bold text-lg w-8">
                {{ index + 1 }}位
              </span>
              <span class="font-medium text-gray-800 ml-3">{{ item.name }}</span>
            </div>
            <div class="text-right">
              <span :class="getScoreColor(item.score)" class="font-bold">{{ item.score }}</span>
              <span class="text-xs text-gray-500 ml-2">{{ item.change > 0 ? '+' : '' }}{{ item.change }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 詳細比較チャート -->
    <div class="mb-8">
      <h4 class="text-lg font-semibold text-gray-800 mb-4">項目別詳細比較</h4>
      <div class="space-y-4">
        <div v-for="category in detailedComparison" :key="category.name" 
             class="p-4 border rounded-lg">
          <div class="flex items-center justify-between mb-3">
            <h5 class="font-medium text-gray-800">{{ category.name }}</h5>
            <span class="text-sm text-gray-500">{{ category.unit }}</span>
          </div>
          
          <div class="space-y-2">
            <div v-for="item in category.items" :key="item.name" 
                 class="flex items-center justify-between">
              <span class="text-sm text-gray-600 w-20">{{ item.name }}</span>
              <div class="flex-1 mx-4">
                <div class="flex items-center">
                  <div class="w-32 bg-gray-200 rounded-full h-3 mr-3">
                    <div :class="getBarColor(item.name)" 
                         class="h-3 rounded-full transition-all duration-500" 
                         :style="{ width: (item.value / category.max * 100) + '%' }">
                    </div>
                  </div>
                  <span class="text-sm font-semibold text-gray-800 w-16 text-right">
                    {{ item.value }}{{ category.unit }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 成功事例・ベストプラクティス -->
    <div class="mb-6" v-if="selectedComparison === 'successful'">
      <h4 class="text-lg font-semibold text-gray-800 mb-4">💡 成功事例・ベストプラクティス</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="practice in bestPractices" :key="practice.municipality" 
             class="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-start justify-between mb-2">
            <h5 class="font-semibold text-green-800">{{ practice.municipality }}</h5>
            <span class="text-sm text-green-600 bg-green-100 px-2 py-1 rounded">
              {{ practice.category }}
            </span>
          </div>
          <h6 class="font-medium text-gray-800 mb-2">{{ practice.title }}</h6>
          <p class="text-sm text-gray-700 mb-3">{{ practice.description }}</p>
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <p class="text-gray-600">実施期間</p>
              <p class="font-semibold">{{ practice.period }}</p>
            </div>
            <div>
              <p class="text-gray-600">効果</p>
              <p class="font-semibold text-green-600">{{ practice.effect }}</p>
            </div>
          </div>
          <div class="mt-3 pt-3 border-t border-green-200">
            <h6 class="text-sm font-medium text-green-800 mb-1">鳥取県への応用可能性</h6>
            <div class="flex items-center">
              <div class="w-full bg-gray-200 rounded-full h-2 mr-2">
                <div class="bg-green-500 h-2 rounded-full" 
                     :style="{ width: practice.applicability + '%' }"></div>
              </div>
              <span class="text-sm font-semibold text-green-700">{{ practice.applicability }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 課題・改善提案 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="p-4 bg-orange-50 border border-orange-200 rounded-lg">
        <h5 class="font-semibold text-orange-800 mb-3">⚠️ 改善が必要な分野</h5>
        <ul class="text-sm text-orange-700 space-y-2">
          <li v-for="issue in improvementAreas" :key="issue.area">
            <div class="flex justify-between items-start">
              <span>• {{ issue.area }}</span>
              <span class="text-xs bg-orange-100 px-2 py-1 rounded">{{ issue.gap }}</span>
            </div>
            <p class="text-xs text-orange-600 ml-4 mt-1">{{ issue.reason }}</p>
          </li>
        </ul>
      </div>
      
      <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h5 class="font-semibold text-blue-800 mb-3">💡 推奨される取り組み</h5>
        <ul class="text-sm text-blue-700 space-y-2">
          <li v-for="recommendation in recommendations" :key="recommendation.title">
            <div class="flex justify-between items-start">
              <span>• {{ recommendation.title }}</span>
              <span class="text-xs bg-blue-100 px-2 py-1 rounded">{{ recommendation.priority }}</span>
            </div>
            <p class="text-xs text-blue-600 ml-4 mt-1">{{ recommendation.description }}</p>
          </li>
        </ul>
      </div>
    </div>

    <!-- データ更新時刻 -->
    <div class="mt-6 pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500">比較データ更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MunicipalityComparison',
  data() {
    return {
      selectedComparison: 'similar',
      selectedMetric: 'population',
      lastUpdated: '',
      tottoriScore: 72.5,
      
      // 比較対象自治体データ
      comparisonData: {
        similar: [
          { name: '島根県', score: 74.8, change: 1.5, icon: '🏔️' },
          { name: '徳島県', score: 71.2, change: 0.8, icon: '🌊' },
          { name: '高知県', score: 69.4, change: -0.3, icon: '🏞️' }
        ],
        neighboring: [
          { name: '岡山県', score: 78.2, change: 2.1, icon: '🍑' },
          { name: '兵庫県', score: 76.9, change: 1.0, icon: '🏰' },
          { name: '広島県', score: 79.5, change: 1.8, icon: '🦌' }
        ],
        successful: [
          { name: '福井県', score: 85.3, change: 3.2, icon: '🦕' },
          { name: '石川県', score: 82.1, change: 2.8, icon: '🍱' },
          { name: '富山県', score: 84.6, change: 2.5, icon: '⛰️' }
        ],
        all: [
          { name: '全国平均', score: 75.0, change: 1.2, icon: '🗾' },
          { name: '地方平均', score: 73.8, change: 0.9, icon: '🌾' },
          { name: '類似規模', score: 72.8, change: 0.6, icon: '🏘️' }
        ]
      },
      
      // 詳細比較データ
      comparisonMetrics: {
        population: {
          title: '人口動態',
          categories: [
            {
              name: '人口増減率',
              unit: '%',
              max: 2.0,
              items: [
                { name: '鳥取県', value: -0.8 },
                { name: '比較1', value: -0.5 },
                { name: '比較2', value: 1.2 },
                { name: '比較3', value: 0.3 }
              ]
            },
            {
              name: '転入転出',
              unit: '人',
              max: 1000,
              items: [
                { name: '鳥取県', value: -500 },
                { name: '比較1', value: -200 },
                { name: '比較2', value: 800 },
                { name: '比較3', value: 150 }
              ]
            }
          ]
        },
        economy: {
          title: '経済指標',
          categories: [
            {
              name: '平均所得',
              unit: '万円',
              max: 400,
              items: [
                { name: '鳥取県', value: 285 },
                { name: '比較1', value: 295 },
                { name: '比較2', value: 350 },
                { name: '比較3', value: 320 }
              ]
            },
            {
              name: '就業率',
              unit: '%',
              max: 100,
              items: [
                { name: '鳥取県', value: 78.5 },
                { name: '比較1', value: 80.2 },
                { name: '比較2', value: 82.1 },
                { name: '比較3', value: 79.8 }
              ]
            }
          ]
        }
      },
      
      // ベストプラクティス
      bestPractices: [
        {
          municipality: '福井県',
          category: '人口減少対策',
          title: 'UIJターン包括支援制度',
          description: '移住前から定着まで一貫した支援体制を構築し、定着率90%を達成',
          period: '2020-2024年',
          effect: '移住者3倍増',
          applicability: 85
        },
        {
          municipality: '石川県',
          category: '産業振興',
          title: 'デジタル産業クラスター構想',
          description: 'IT企業誘致と地元大学連携により新産業エコシステムを創出',
          period: '2019-2023年',
          effect: '雇用1200人創出',
          applicability: 70
        }
      ],
      
      // 改善が必要な分野
      improvementAreas: [
        {
          area: '就業機会の創出',
          gap: '全国-8.2pt',
          reason: '製造業・IT産業の誘致が不十分'
        },
        {
          area: '交通アクセス',
          gap: '類似県-5.1pt',
          reason: '公共交通機関の利便性に課題'
        },
        {
          area: '高等教育環境',
          gap: '近隣県-6.8pt',
          reason: '大学進学者の県外流出が深刻'
        }
      ],
      
      // 推奨取り組み
      recommendations: [
        {
          title: 'デジタル産業拠点の整備',
          priority: '高',
          description: 'リモートワーク環境とスタートアップ支援の充実'
        },
        {
          title: '交通インフラの整備',
          priority: '中',
          description: '空港アクセス改善と地域間連携強化'
        },
        {
          title: '教育機関との連携強化',
          priority: '高',
          description: '産学官連携による人材育成・定着促進'
        }
      ]
    }
  },
  computed: {
    comparisonMunicipalities() {
      return this.comparisonData[this.selectedComparison] || []
    },
    rankingData() {
      const allData = [
        { name: '鳥取県', score: this.tottoriScore, change: 1.2 },
        ...this.comparisonMunicipalities
      ]
      return allData.sort((a, b) => b.score - a.score)
    },
    detailedComparison() {
      return this.comparisonMetrics[this.selectedMetric]?.categories || []
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
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getMetricTitle() {
      return this.comparisonMetrics[this.selectedMetric]?.title || ''
    },
    getComparisonTitle() {
      const titles = {
        similar: '類似自治体',
        neighboring: '近隣自治体',
        successful: '成功事例',
        all: '全国平均'
      }
      return titles[this.selectedComparison]
    },
    getScoreColor(score) {
      if (score >= 80) return 'text-green-600'
      if (score >= 70) return 'text-blue-600'
      if (score >= 60) return 'text-orange-600'
      return 'text-red-600'
    },
    getScoreLabel(score) {
      if (score >= 80) return '優秀'
      if (score >= 70) return '良好'
      if (score >= 60) return '標準'
      return '要改善'
    },
    getRankColor(rank) {
      if (rank === 1) return 'text-yellow-600'
      if (rank === 2) return 'text-gray-500'
      if (rank === 3) return 'text-orange-600'
      return 'text-gray-700'
    },
    getBarColor(name) {
      if (name === '鳥取県') return 'bg-blue-500'
      return 'bg-gray-400'
    }
  }
}
</script>

<style scoped>
/* カスタムスタイル */
</style>