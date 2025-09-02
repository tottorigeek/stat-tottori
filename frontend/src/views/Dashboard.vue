<template>
  <div class="min-h-screen bg-gray-50">
    <!-- ヘッダー -->
    <header class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">🏔️ すたっととっとり</h1>
            <p class="text-blue-100 mt-2">鳥取県の住みやすさ向上と人口増加をサポートする情報ダッシュボード</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-blue-100">最終更新: {{ lastUpdated }}</p>
            <div class="flex items-center mt-1">
              <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              <span class="text-xs text-green-200">リアルタイム更新中</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 共通ナビゲーションバー -->
    <CommonNavigation />

    <!-- メインコンテンツ -->
    <main class="container mx-auto px-4 py-8">
      <!-- ページヘッダー -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">📊 社会課題分析ダッシュボード</h1>
        <p class="text-gray-600">鳥取県の主要な社会課題を統計データで俯瞰し、解決策の優先順位を分析します</p>
        <div class="flex items-center mt-2">
          <div class="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
          <span class="text-sm text-blue-600">データ更新: {{ lastUpdated }}</span>
        </div>
      </div>

      <!-- 重要課題アラート -->
      <div v-if="criticalIssues.length > 0" class="mb-8">
        <div v-for="issue in criticalIssues" :key="issue.id" class="bg-orange-100 border-l-4 border-orange-500 p-4 mb-4 rounded-r-lg">
          <div class="flex items-center">
            <span class="text-orange-600 text-xl mr-3">⚠️</span>
            <div>
              <p class="text-sm text-orange-700">
                <strong>{{ issue.category }}:</strong> {{ issue.message }}
              </p>
              <p class="text-xs text-orange-600 mt-1">優先度: {{ issue.priority }} | 影響度: {{ issue.impact }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 主要課題分析セクション -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <!-- 人口動態分析 -->
        <SocialIssueCard 
          title="人口動態の課題"
          icon="👥"
          :metrics="populationMetrics"
          trend="decreasing"
          priority="高"
        />
        
        <!-- 経済・雇用分析 -->
        <SocialIssueCard 
          title="経済・雇用の課題"
          icon="💼"
          :metrics="economicMetrics"
          trend="stagnant"
          priority="高"
        />
        
        <!-- 地域格差分析 -->
        <SocialIssueCard 
          title="地域格差の課題"
          icon="🗾"
          :metrics="regionalMetrics"
          trend="widening"
          priority="中"
        />
      </div>

      <!-- 人口統計セクション -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-gray-800">📊 人口統計</h3>
          <button @click="showPopulationDetail = true" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
            詳細を見る
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center">
            <h4 class="text-lg font-semibold text-gray-700 mb-2">総人口</h4>
            <p class="text-3xl font-bold text-blue-600">{{ populationSummary.total.toLocaleString() }}人</p>
            <p class="text-sm text-gray-500 mt-1">前年比: {{ populationSummary.change > 0 ? '+' : '' }}{{ populationSummary.change }}人</p>
          </div>
          <div class="text-center">
            <h4 class="text-lg font-semibold text-gray-700 mb-2">転入者数</h4>
            <p class="text-3xl font-bold text-green-600">{{ populationSummary.inflow.toLocaleString() }}人</p>
            <p class="text-sm text-gray-500 mt-1">前年比: {{ populationSummary.inflowChange > 0 ? '+' : '' }}{{ populationSummary.inflowChange }}人</p>
          </div>
          <div class="text-center">
            <h4 class="text-lg font-semibold text-gray-700 mb-2">転出者数</h4>
            <p class="text-3xl font-bold text-red-600">{{ populationSummary.outflow.toLocaleString() }}人</p>
            <p class="text-sm text-gray-500 mt-1">前年比: {{ populationSummary.outflowChange > 0 ? '+' : '' }}{{ populationSummary.outflowChange }}人</p>
          </div>
        </div>
      </div>

      <!-- 天気・災害情報 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
          🌤️ 天気・災害情報
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-lg font-semibold text-gray-700">鳥取市</p>
            <div class="text-3xl my-2">{{ weather.tottori.icon }}</div>
            <p class="text-sm text-gray-600">{{ weather.tottori.temp }}°C</p>
            <p class="text-xs text-gray-500">{{ weather.tottori.condition }}</p>
          </div>
          <div class="text-center">
            <p class="text-lg font-semibold text-gray-700">米子市</p>
            <div class="text-3xl my-2">{{ weather.yonago.icon }}</div>
            <p class="text-sm text-gray-600">{{ weather.yonago.temp }}°C</p>
            <p class="text-xs text-gray-500">{{ weather.yonago.condition }}</p>
          </div>
          <div class="text-center">
            <p class="text-lg font-semibold text-gray-700">倉吉市</p>
            <div class="text-3xl my-2">{{ weather.kurayoshi.icon }}</div>
            <p class="text-sm text-gray-600">{{ weather.kurayoshi.temp }}°C</p>
            <p class="text-xs text-gray-500">{{ weather.kurayoshi.condition }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import SocialIssueCard from '@/components/SocialIssueCard.vue'
import CommonNavigation from '@/components/CommonNavigation.vue'

export default {
  name: 'Dashboard',
  components: {
    SocialIssueCard,
    CommonNavigation
  },
  data() {
    return {
      lastUpdated: '',
      showPopulationDetail: false,
      criticalIssues: [
        {
          id: 1,
          category: '人口減少',
          message: '年間1,500人の人口減少が継続中。現在のペースでは10年後に人口50万人を下回る予測',
          priority: '最高',
          impact: '大'
        },
        {
          id: 2,
          category: '労働力不足',
          message: '15-64歳人口が過去5年で8%減少。主要産業での人材確保が困難',
          priority: '高',
          impact: '中'
        }
      ],
      populationMetrics: {
        current: '550,234人',
        trend: '-1,500人/年',
        projection: '10年後: 484,000人',
        severity: 'critical'
      },
      economicMetrics: {
        current: '求人倍率 1.25倍',
        trend: '新規求人数 -5%',
        projection: '労働力不足深刻化',
        severity: 'high'
      },
      regionalMetrics: {
        current: '東部集中率 68%',
        trend: '中部・西部流出継続',
        projection: '過疎化加速',
        severity: 'medium'
      },
      populationSummary: {
        total: 550000,
        change: -1500,
        inflow: 8500,
        inflowChange: 200,
        outflow: 10000,
        outflowChange: -300
      },
      weather: {
        tottori: { icon: '☀️', temp: 25, condition: '晴れ' },
        yonago: { icon: '⛅', temp: 22, condition: '曇り' },
        kurayoshi: { icon: '🌧️', temp: 18, condition: '雨' }
      }
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 60000)
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
    }
  }
}
</script>