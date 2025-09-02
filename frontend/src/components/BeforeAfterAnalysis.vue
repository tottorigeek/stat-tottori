<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-800">Before/After 効果分析</h3>
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-500">{{ policy.name }}</span>
        <span :class="getStatusColor(policy.status)" class="px-2 py-1 text-xs rounded">
          {{ policy.status }}
        </span>
      </div>
    </div>

    <!-- 施策概要 -->
    <div class="mb-6 p-4 bg-gray-50 rounded-lg">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div>
          <p class="text-gray-600">実施期間</p>
          <p class="font-semibold">{{ policy.period }}</p>
        </div>
        <div>
          <p class="text-gray-600">予算規模</p>
          <p class="font-semibold text-blue-600">{{ policy.budget }}万円</p>
        </div>
        <div>
          <p class="text-gray-600">担当部署</p>
          <p class="font-semibold">{{ policy.department }}</p>
        </div>
      </div>
      <div class="mt-3">
        <p class="text-gray-600">施策内容</p>
        <p class="text-sm text-gray-800 mt-1">{{ policy.description }}</p>
      </div>
    </div>

    <!-- KPI別Before/After比較 -->
    <div class="mb-8">
      <h4 class="text-lg font-semibold text-gray-800 mb-4">KPI別効果測定</h4>
      <div class="space-y-6">
        <div v-for="kpi in policy.kpis" :key="kpi.name" class="p-4 border rounded-lg">
          <div class="flex items-center justify-between mb-3">
            <h5 class="font-semibold text-gray-800">{{ kpi.name }}</h5>
            <span class="text-sm text-gray-500">目標: {{ kpi.target }}{{ kpi.unit }}</span>
          </div>
          
          <!-- Before/After数値比較 -->
          <div class="grid grid-cols-3 gap-4 mb-4">
            <div class="text-center p-3 bg-red-50 rounded">
              <p class="text-xs text-red-600 mb-1">施策前 (Before)</p>
              <p class="text-lg font-bold text-red-700">{{ getBeforeValue(kpi) }}{{ kpi.unit }}</p>
            </div>
            <div class="text-center p-3 bg-blue-50 rounded">
              <p class="text-xs text-blue-600 mb-1">目標値 (Target)</p>
              <p class="text-lg font-bold text-blue-700">{{ kpi.target }}{{ kpi.unit }}</p>
            </div>
            <div class="text-center p-3 bg-green-50 rounded">
              <p class="text-xs text-green-600 mb-1">現在値 (After)</p>
              <p class="text-lg font-bold text-green-700">{{ kpi.actual }}{{ kpi.unit }}</p>
            </div>
          </div>

          <!-- 効果指標 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="p-3 bg-gray-50 rounded">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">改善度</span>
                <span :class="getImprovementColor(kpi)" class="font-semibold">
                  {{ getImprovementRate(kpi) }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div :class="getImprovementBarColor(kpi)" 
                     class="h-2 rounded-full" 
                     :style="{ width: Math.min(Math.abs(getImprovementPercentage(kpi)), 100) + '%' }">
                </div>
              </div>
            </div>
            
            <div class="p-3 bg-gray-50 rounded">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">目標達成率</span>
                <span :class="getAchievementColor(kpi)" class="font-semibold">
                  {{ getTargetAchievementRate(kpi) }}%
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div :class="getAchievementBarColor(kpi)" 
                     class="h-2 rounded-full" 
                     :style="{ width: Math.min(getTargetAchievementRate(kpi), 100) + '%' }">
                </div>
              </div>
            </div>
          </div>

          <!-- トレンド分析（時系列データがある場合） -->
          <div v-if="hasTimeSeriesData(kpi)" class="mt-4 p-3 bg-blue-50 rounded">
            <h6 class="text-sm font-medium text-blue-800 mb-2">月次推移</h6>
            <div class="flex items-end space-x-1 h-16">
              <div v-for="(value, index) in getTimeSeriesData(kpi)" :key="index" 
                   class="bg-blue-500 rounded-t" 
                   :style="{ height: (value / Math.max(...getTimeSeriesData(kpi)) * 100) + '%', width: '20px' }"
                   :title="`${index + 1}月: ${value}${kpi.unit}`">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 総合評価 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-4">総合評価</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 text-center border rounded-lg">
          <div class="text-2xl mb-2">📊</div>
          <h5 class="font-semibold text-gray-800 mb-1">効果測定</h5>
          <p :class="getOverallEffectColor()" class="text-lg font-bold">{{ getOverallEffect() }}</p>
          <p class="text-xs text-gray-500">平均改善率</p>
        </div>
        
        <div class="p-4 text-center border rounded-lg">
          <div class="text-2xl mb-2">🎯</div>
          <h5 class="font-semibold text-gray-800 mb-1">目標達成</h5>
          <p :class="getOverallAchievementColor()" class="text-lg font-bold">{{ policy.kpiAchievement }}%</p>
          <p class="text-xs text-gray-500">平均達成率</p>
        </div>
        
        <div class="p-4 text-center border rounded-lg">
          <div class="text-2xl mb-2">⭐</div>
          <h5 class="font-semibold text-gray-800 mb-1">総合評価</h5>
          <p :class="getEvaluationColor(policy.evaluation)" class="text-lg font-bold">{{ policy.evaluation }}ランク</p>
          <p class="text-xs text-gray-500">5段階評価</p>
        </div>
      </div>
    </div>

    <!-- 施策の効果・課題・改善点 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
        <h5 class="font-semibold text-green-800 mb-2">🎉 主な成果</h5>
        <ul class="text-sm text-green-700 space-y-1">
          <li v-for="success in getSuccesses()" :key="success">• {{ success }}</li>
        </ul>
      </div>
      
      <div class="p-4 bg-orange-50 border border-orange-200 rounded-lg">
        <h5 class="font-semibold text-orange-800 mb-2">⚠️ 課題・問題</h5>
        <ul class="text-sm text-orange-700 space-y-1">
          <li v-for="issue in getIssues()" :key="issue">• {{ issue }}</li>
        </ul>
      </div>
      
      <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h5 class="font-semibold text-blue-800 mb-2">💡 改善提案</h5>
        <ul class="text-sm text-blue-700 space-y-1">
          <li v-for="suggestion in getSuggestions()" :key="suggestion">• {{ suggestion }}</li>
        </ul>
      </div>
    </div>

    <!-- データ更新時刻 -->
    <div class="mt-6 pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500">分析データ更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BeforeAfterAnalysis',
  props: {
    policy: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      lastUpdated: '',
      // サンプルのBefore値（実際は施策実施前のデータから取得）
      beforeValues: {
        '移住者数': 45,
        '定着率': 65,
        '就職率': 55,
        '待機児童数': 12,
        '出生率': 1.48,
        '満足度': 72,
        'オンライン手続き率': 25,
        'システム稼働率': 96.8,
        '利用者満足度': 0,
        '新規雇用創出': 120,
        '売上向上率': 8,
        '企業満足度': 75
      }
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 300000)
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
    getBeforeValue(kpi) {
      return this.beforeValues[kpi.name] || 0
    },
    getImprovementRate(kpi) {
      const before = this.getBeforeValue(kpi)
      const after = kpi.actual
      const improvement = ((after - before) / before * 100)
      return improvement > 0 ? `+${improvement.toFixed(1)}%` : `${improvement.toFixed(1)}%`
    },
    getImprovementPercentage(kpi) {
      const before = this.getBeforeValue(kpi)
      const after = kpi.actual
      return ((after - before) / before * 100)
    },
    getTargetAchievementRate(kpi) {
      return Math.round((kpi.actual / kpi.target) * 100)
    },
    getOverallEffect() {
      const improvements = this.policy.kpis.map(kpi => this.getImprovementPercentage(kpi))
      const avgImprovement = improvements.reduce((sum, imp) => sum + imp, 0) / improvements.length
      return avgImprovement > 0 ? `+${avgImprovement.toFixed(1)}%` : `${avgImprovement.toFixed(1)}%`
    },
    getImprovementColor(kpi) {
      const improvement = this.getImprovementPercentage(kpi)
      if (improvement > 10) return 'text-green-600'
      if (improvement > 0) return 'text-blue-600'
      return 'text-red-600'
    },
    getImprovementBarColor(kpi) {
      const improvement = this.getImprovementPercentage(kpi)
      if (improvement > 10) return 'bg-green-500'
      if (improvement > 0) return 'bg-blue-500'
      return 'bg-red-500'
    },
    getAchievementColor(kpi) {
      const rate = this.getTargetAchievementRate(kpi)
      if (rate >= 100) return 'text-green-600'
      if (rate >= 80) return 'text-blue-600'
      if (rate >= 60) return 'text-orange-600'
      return 'text-red-600'
    },
    getAchievementBarColor(kpi) {
      const rate = this.getTargetAchievementRate(kpi)
      if (rate >= 100) return 'bg-green-500'
      if (rate >= 80) return 'bg-blue-500'
      if (rate >= 60) return 'bg-orange-500'
      return 'bg-red-500'
    },
    getOverallEffectColor() {
      const effect = parseFloat(this.getOverallEffect())
      if (effect > 10) return 'text-green-600'
      if (effect > 0) return 'text-blue-600'
      return 'text-red-600'
    },
    getOverallAchievementColor() {
      const achievement = this.policy.kpiAchievement
      if (achievement >= 80) return 'text-green-600'
      if (achievement >= 60) return 'text-blue-600'
      return 'text-orange-600'
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
    },
    hasTimeSeriesData(kpi) {
      // 実際の実装では時系列データの有無を判定
      return kpi.name === '移住者数' || kpi.name === '待機児童数'
    },
    getTimeSeriesData(kpi) {
      // サンプル時系列データ
      const sampleData = {
        '移住者数': [45, 52, 58, 63, 68, 72, 75],
        '待機児童数': [12, 10, 8, 6, 5, 4, 3]
      }
      return sampleData[kpi.name] || []
    },
    getSuccesses() {
      // 施策の成果（実際はAPIから取得）
      const successMap = {
        1: ['移住者数が67%増加', '定着率が目標を上回る', '地域コミュニティ活性化'],
        2: ['待機児童数が75%減少', '子育て満足度向上', '出生率の底上げ'],
        3: ['デジタル化基盤構築完了', '職員のITスキル向上', '市民からの好反応'],
        4: ['雇用創出目標の93%達成', '地場産業の売上18%向上', '企業満足度大幅改善']
      }
      return successMap[this.policy.id] || ['成果分析中']
    },
    getIssues() {
      // 課題・問題（実際はAPIから取得）
      const issueMap = {
        1: ['就職率が目標未達', '住居確保の難しさ', '若年層の定着に課題'],
        2: ['出生率の改善幅が小さい', '施設整備の遅れ', '人材確保の困難'],
        3: ['利用者満足度未測定', 'システム稼働率不安定', 'セキュリティ対策の強化必要'],
        4: ['新規雇用創出がやや不足', '一部業界での効果限定的', 'コスト効率の改善余地']
      }
      return issueMap[this.policy.id] || ['課題分析中']
    },
    getSuggestions() {
      // 改善提案（実際はAPIから取得）
      const suggestionMap = {
        1: ['職業訓練の充実', '住宅支援制度の拡充', 'メンター制度の導入'],
        2: ['働き方改革の推進', '保育士確保対策強化', '子育て相談体制拡充'],
        3: ['ユーザビリティ改善', '安定性向上対策', 'セキュリティ強化'],
        4: ['対象業界の拡大', 'マッチング精度向上', 'コスト最適化検討']
      }
      return suggestionMap[this.policy.id] || ['提案検討中']
    }
  }
}
</script>

<style scoped>
/* カスタムスタイル */
</style>