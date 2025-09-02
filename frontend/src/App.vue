<template>
  <div id="app" class="min-h-screen bg-gray-50">
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
      
      <!-- ナビゲーションメニュー -->
      <nav class="bg-blue-700">
        <div class="container mx-auto px-4">
          <div class="flex space-x-8">
            <router-link 
              to="/" 
              class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              active-class="bg-blue-800 text-white"
            >
              🏠 ホーム
            </router-link>
            <router-link 
              to="/population" 
              class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              active-class="bg-blue-800 text-white"
            >
              📊 人口推移
            </router-link>
            <router-link 
              to="/livability-comparison" 
              class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              active-class="bg-blue-800 text-white"
            >
              🏠 住みやすさ比較
            </router-link>
            <router-link 
              to="/population-detail" 
              class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              active-class="bg-blue-800 text-white"
            >
              📈 人口詳細
            </router-link>
          </div>
        </div>
      </nav>
    </header>

    <!-- メインコンテンツ -->
    <main class="container mx-auto px-4 py-8">

               <!-- 人口統計セクション -->
        <div class="mt-8 bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-gray-800">📊 人口統計</h3>
            <div class="flex space-x-3">
              <button @click="showPopulationDetail = true" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                詳細を見る
              </button>
              <button @click="navigateToPopulationTrend" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                推移分析
              </button>
            </div>
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

        <!-- 住みやすさ比較セクション -->
        <div class="mt-8 bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-gray-800">🏠 住みやすさ比較</h3>
            <button @click="showLivabilityComparison = true" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
              比較を見る
            </button>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="text-center">
              <h4 class="text-lg font-semibold text-gray-700 mb-2">鳥取県の総合スコア</h4>
              <p class="text-3xl font-bold text-green-600">72.5点</p>
              <p class="text-sm text-gray-500 mt-1">前年比: +1.2点</p>
            </div>
            <div class="text-center">
              <h4 class="text-lg font-semibold text-gray-700 mb-2">近隣県との比較</h4>
              <p class="text-lg font-semibold text-gray-800">島根県: 74.8点</p>
              <p class="text-lg font-semibold text-gray-800">岡山県: 78.2点</p>
            </div>
          </div>
        </div>
    </main>

    <!-- 人口統計詳細モーダル -->
    <div v-if="showPopulationDetail" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-7xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-2xl font-bold text-gray-800">📊 人口統計詳細</h3>
            <button @click="showPopulationDetail = false" class="text-gray-400 hover:text-gray-600 text-2xl font-bold">
              ×
            </button>
          </div>
          
          <!-- タブナビゲーション -->
          <div class="mb-6">
            <nav class="flex space-x-8 border-b border-gray-200">
              <button 
                v-for="tab in populationTabs" 
                :key="tab.id"
                @click="activePopulationTab = tab.id"
                :class="[
                  'py-2 px-1 border-b-2 font-medium text-sm',
                  activePopulationTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                {{ tab.name }}
              </button>
            </nav>
          </div>

          <!-- タブコンテンツ -->
          <div v-if="activePopulationTab === 'age'" class="space-y-6">
            <div class="bg-gray-50 rounded-lg p-6">
              <h4 class="text-lg font-semibold text-gray-800 mb-4">年齢別人口推移（転入・転出）</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div v-for="(data, ageGroup) in ageGroupData" :key="ageGroup" class="bg-white rounded-lg p-4 shadow-sm">
                  <h5 class="font-semibold text-gray-700 mb-2">{{ ageGroup }}</h5>
                  <p class="text-2xl font-bold text-blue-600">{{ data.total.toLocaleString() }}人</p>
                  <div class="mt-2 text-sm">
                    <p class="text-green-600">転入: {{ data.inflow.toLocaleString() }}人</p>
                    <p class="text-red-600">転出: {{ data.outflow.toLocaleString() }}人</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activePopulationTab === 'municipality'" class="space-y-6">
            <div class="bg-gray-50 rounded-lg p-6">
              <h4 class="text-lg font-semibold text-gray-800 mb-4">市区町村別人口推移（転入・転出）</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="(data, municipality) in municipalityData" :key="municipality" class="bg-white rounded-lg p-4 shadow-sm">
                  <h5 class="font-semibold text-gray-700 mb-2">{{ municipality }}</h5>
                  <p class="text-2xl font-bold text-blue-600">{{ data.total.toLocaleString() }}人</p>
                  <div class="mt-2 text-sm">
                    <p class="text-green-600">転入: {{ data.inflow.toLocaleString() }}人</p>
                    <p class="text-red-600">転出: {{ data.outflow.toLocaleString() }}人</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activePopulationTab === 'trend'" class="space-y-6">
            <div class="bg-gray-50 rounded-lg p-6">
              <h4 class="text-lg font-semibold text-gray-800 mb-4">月別推移・季節性分析</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 class="font-semibold text-gray-700 mb-3">転入が多い月</h5>
                  <div class="space-y-2">
                    <div v-for="(count, month) in seasonalInflow" :key="month" class="flex items-center justify-between">
                      <span class="text-gray-600">{{ month }}</span>
                      <div class="flex items-center">
                        <div class="w-20 bg-gray-200 rounded-full h-2 mr-3">
                          <div class="bg-green-500 h-2 rounded-full" :style="{ width: (count / maxSeasonalInflow * 100) + '%' }"></div>
                        </div>
                        <span class="text-sm font-semibold text-gray-800">{{ count }}人</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <h5 class="font-semibold text-gray-700 mb-3">転出が多い月</h5>
                  <div class="space-y-2">
                    <div v-for="(count, month) in seasonalOutflow" :key="month" class="flex items-center justify-between">
                      <span class="text-gray-600">{{ month }}</span>
                      <div class="flex items-center">
                        <div class="w-20 bg-gray-200 rounded-full h-2 mr-3">
                          <div class="bg-red-500 h-2 rounded-full" :style="{ width: (count / maxSeasonalOutflow * 100) + '%' }"></div>
                        </div>
                        <span class="text-sm font-semibold text-gray-800">{{ count }}人</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 住みやすさ比較モーダル -->
    <div v-if="showLivabilityComparison" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-7xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-2xl font-bold text-gray-800">🏠 住みやすさ比較</h3>
            <button @click="showLivabilityComparison = false" class="text-gray-400 hover:text-gray-600 text-2xl font-bold">
              ×
            </button>
          </div>
          
          <!-- 簡易比較表示 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="font-semibold text-gray-800 mb-3">鳥取県の強み</h4>
              <ul class="text-sm text-gray-600 space-y-2">
                <li class="flex items-start">
                  <span class="text-green-500 mr-2">✓</span>
                  豊かな自然環境と美しい景観
                </li>
                <li class="flex items-start">
                  <span class="text-green-500 mr-2">✓</span>
                  安全で安心な生活環境
                </li>
                <li class="flex items-start">
                  <span class="text-green-500 mr-2">✓</span>
                  医療・福祉サービスの充実
                </li>
              </ul>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="font-semibold text-gray-800 mb-3">改善が必要な分野</h4>
              <ul class="text-sm text-gray-600 space-y-2">
                <li class="flex items-start">
                  <span class="text-orange-500 mr-2">⚠</span>
                  就業機会の拡大と所得向上
                </li>
                <li class="flex items-start">
                  <span class="text-orange-500 mr-2">⚠</span>
                  交通アクセスの改善
                </li>
                <li class="flex items-start">
                  <span class="text-orange-500 mr-2">⚠</span>
                  教育・文化施設の充実
                </li>
              </ul>
            </div>
          </div>
          
          <!-- 詳細ページへのリンク -->
          <div class="text-center">
            <p class="text-gray-600 mb-4">より詳細な比較分析をご覧になりたい方は、詳細ページをご利用ください</p>
            <button @click="navigateToComparison" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200">
              詳細比較ページへ
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- フッター -->
    <footer class="bg-gray-800 text-white py-6 mt-12">
      <div class="container mx-auto px-4 text-center">
                 <p>&copy; 2025 すたっととっとり. All rights reserved.</p>
        <p class="text-xs text-gray-400 mt-2">データは各機関から提供されたものを使用しています</p>
      </div>
    </footer>
  </div>
</template>

<script>
import MedicalInfo from './components/MedicalInfo.vue'
import TransportInfo from './components/TransportInfo.vue'
import GovernmentInfo from './components/GovernmentInfo.vue'

export default {
  name: 'App',
  components: {
    MedicalInfo,
    TransportInfo,
    GovernmentInfo
  },
  data() {
    return {
      lastUpdated: '',
      showPopulationDetail: false,
      showLivabilityComparison: false,
      emergencyInfo: [
        {
          id: 1,
          type: '交通情報',
          message: '国道9号線（鳥取市内）で工事による片側通行中です',
          time: '2025-01-02 14:30'
        }
      ],
      weather: {
        tottori: {
          icon: '☀️',
          temp: 8,
          condition: '晴れ'
        },
        yonago: {
          icon: '⛅',
          temp: 6,
          condition: '曇り'
        },
        kurayoshi: {
          icon: '☀️',
          temp: 7,
          condition: '晴れ'
        }
      },
      populationSummary: {
        total: 550000,
        change: -1500,
        inflow: 8500,
        inflowChange: 200,
        outflow: 10000,
        outflowChange: -300
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
    },
    navigateToComparison() {
      // 住みやすさ比較詳細ページへのナビゲーション
      this.showLivabilityComparison = false
      this.$router.push('/livability-comparison')
    },
    navigateToPopulationTrend() {
      // 人口推移分析ページへのナビゲーション
      this.$router.push('/population')
    }
  }
}
</script>

<style>
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

#app {
  font-family: 'Noto Sans JP', sans-serif;
}
</style>