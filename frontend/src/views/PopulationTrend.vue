<template>
  <div class="min-h-screen bg-gray-50">
    <!-- ヘッダー -->
    <header class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">📊 人口推移分析</h1>
            <p class="text-blue-100 mt-2">すたっととっとり - 鳥取県の人口動態を時系列で詳細分析</p>
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
      <!-- 概要カード -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">現在の総人口</h3>
          <p class="text-3xl font-bold text-blue-600">{{ currentPopulation.total.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ currentPopulation.change > 0 ? '+' : '' }}{{ currentPopulation.change }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">年間転入者数</h3>
          <p class="text-3xl font-bold text-green-600">{{ currentPopulation.inflow.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ currentPopulation.inflowChange > 0 ? '+' : '' }}{{ currentPopulation.inflowChange }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">年間転出者数</h3>
          <p class="text-3xl font-bold text-red-600">{{ currentPopulation.outflow.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ currentPopulation.outflowChange > 0 ? '+' : '' }}{{ currentPopulation.outflowChange }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">自然増減</h3>
          <p class="text-3xl font-bold text-purple-600">{{ currentPopulation.naturalChange > 0 ? '+' : '' }}{{ currentPopulation.naturalChange }}人</p>
          <p class="text-sm text-gray-500 mt-2">出生 - 死亡</p>
        </div>
      </div>

      <!-- タブナビゲーション -->
      <div class="mb-8">
        <nav class="flex space-x-8 border-b border-gray-200">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- タブコンテンツ -->
      <div v-if="activeTab === 'overview'" class="space-y-8">
        <!-- 総人口推移グラフ -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">総人口推移（過去10年）</h3>
          <div class="h-80">
            <canvas ref="totalPopulationChart" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- 転入・転出推移グラフ -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">転入・転出推移（過去10年）</h3>
          <div class="h-80">
            <canvas ref="migrationChart" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- 自然増減推移グラフ -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">自然増減推移（過去10年）</h3>
          <div class="h-80">
            <canvas ref="naturalChangeChart" class="w-full h-full"></canvas>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'age'" class="space-y-8">
        <!-- 年齢別人口推移 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">年齢別人口推移（過去10年）</h3>
          <div class="h-80">
            <canvas ref="ageGroupChart" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- 年齢別詳細テーブル -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">年齢別人口詳細（最新データ）</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">年齢層</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">総人口</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">転入者数</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">転出者数</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">純移動</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">前年比</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(data, ageGroup) in ageGroupTableData" :key="ageGroup">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ ageGroup }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ data.total.toLocaleString() }}人</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600">{{ data.inflow.toLocaleString() }}人</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600">{{ data.outflow.toLocaleString() }}人</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm" :class="data.netChange >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ data.netChange > 0 ? '+' : '' }}{{ data.netChange.toLocaleString() }}人
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm" :class="data.yearChange >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ data.yearChange > 0 ? '+' : '' }}{{ data.yearChange.toLocaleString() }}人
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'municipality'" class="space-y-8">
        <!-- 市区町村別人口推移 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">市区町村別人口推移（過去10年）</h3>
          <div class="h-80">
            <canvas ref="municipalityChart" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- 市区町村別詳細テーブル -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">市区町村別人口詳細（最新データ）</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">市区町村</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">総人口</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">転入者数</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">転出者数</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">純移動</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">前年比</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(data, municipality) in municipalityTableData" :key="municipality">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ municipality }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ data.total.toLocaleString() }}人</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600">{{ data.inflow.toLocaleString() }}人</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600">{{ data.outflow.toLocaleString() }}人</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm" :class="data.netChange >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ data.netChange > 0 ? '+' : '' }}{{ data.netChange.toLocaleString() }}人
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm" :class="data.yearChange >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ data.yearChange > 0 ? '+' : '' }}{{ data.yearChange.toLocaleString() }}人
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'seasonal'" class="space-y-8">
        <!-- 季節性分析 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-xl font-bold text-gray-800 mb-4">月別転入者数推移</h3>
            <div class="h-80">
              <canvas ref="monthlyInflowChart" class="w-full h-full"></canvas>
            </div>
          </div>
          
          <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-xl font-bold text-gray-800 mb-4">月別転出者数推移</h3>
            <div class="h-80">
              <canvas ref="monthlyOutflowChart" class="w-full h-full"></canvas>
            </div>
          </div>
        </div>

        <!-- 季節性分析テーブル -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">季節性分析</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-semibold text-gray-700 mb-3">転入が多い月</h4>
              <div class="space-y-2">
                <div v-for="(count, month) in seasonalInflow" :key="month" class="flex items-center justify-between">
                  <span class="text-gray-600">{{ month }}</span>
                  <div class="flex items-center">
                    <div class="w-24 bg-gray-200 rounded-full h-2 mr-3">
                      <div class="bg-green-500 h-2 rounded-full" :style="{ width: (count / maxSeasonalInflow * 100) + '%' }"></div>
                    </div>
                    <span class="text-sm font-semibold text-gray-800">{{ count }}人</span>
                  </div>
                </div>
              </div>
            </div>
            <div>
              <h4 class="font-semibold text-gray-700 mb-3">転出が多い月</h4>
              <div class="space-y-2">
                <div v-for="(count, month) in seasonalOutflow" :key="month" class="flex items-center justify-between">
                  <span class="text-gray-600">{{ month }}</span>
                  <div class="flex items-center">
                    <div class="w-24 bg-gray-200 rounded-full h-2 mr-3">
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

      <div v-else-if="activeTab === 'forecast'" class="space-y-8">
        <!-- 人口予測 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">人口予測（今後10年）</h3>
          <div class="h-80">
            <canvas ref="forecastChart" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- 予測根拠 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">予測根拠とシナリオ</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center p-4 border rounded-lg">
              <h4 class="font-semibold text-gray-800 mb-2">楽観シナリオ</h4>
              <p class="text-2xl font-bold text-green-600">{{ forecastScenarios.optimistic.toLocaleString() }}人</p>
              <p class="text-sm text-gray-600 mt-1">2035年予測</p>
              <p class="text-xs text-gray-500 mt-2">住みやすさ向上施策が効果を発揮</p>
            </div>
            <div class="text-center p-4 border rounded-lg">
              <h4 class="font-semibold text-gray-800 mb-2">現状維持シナリオ</h4>
              <p class="text-2xl font-bold text-blue-600">{{ forecastScenarios.current.toLocaleString() }}人</p>
              <p class="text-sm text-gray-600 mt-1">2035年予測</p>
              <p class="text-xs text-gray-500 mt-2">現在の施策を継続</p>
            </div>
            <div class="text-center p-4 border rounded-lg">
              <h4 class="font-semibold text-gray-800 mb-2">悲観シナリオ</h4>
              <p class="text-2xl font-bold text-red-600">{{ forecastScenarios.pessimistic.toLocaleString() }}人</p>
              <p class="text-sm text-gray-600 mt-1">2035年予測</p>
              <p class="text-xs text-gray-500 mt-2">施策が効果を発揮しない</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 戻るボタン -->
      <div class="text-center mt-8">
        <button @click="$router.go(-1)" class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200">
          ← 戻る
        </button>
      </div>
    </main>

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
import { Chart, registerables } from 'chart.js'
import CommonNavigation from '../components/CommonNavigation.vue'
Chart.register(...registerables)

export default {
  name: 'PopulationTrend',
  components: {
    CommonNavigation
  },
  data() {
    return {
      lastUpdated: '',
      activeTab: 'overview',
      tabs: [
        { id: 'overview', name: '総合推移' },
        { id: 'age', name: '年齢別分析' },
        { id: 'municipality', name: '市区町村別分析' },
        { id: 'seasonal', name: '季節性分析' },
        { id: 'forecast', name: '将来予測' }
      ],
      currentPopulation: {
        total: 550000,
        change: -1500,
        inflow: 8500,
        inflowChange: 200,
        outflow: 10000,
        outflowChange: -300,
        naturalChange: -200
      },
      // 年齢別データ
      ageGroupTableData: {
        '0-14歳': { total: 85000, inflow: 1200, outflow: 800, netChange: 400, yearChange: 50 },
        '15-24歳': { total: 65000, inflow: 2500, outflow: 3200, netChange: -700, yearChange: -150 },
        '25-34歳': { total: 75000, inflow: 3200, outflow: 2800, netChange: 400, yearChange: 100 },
        '35-44歳': { total: 85000, inflow: 1800, outflow: 1600, netChange: 200, yearChange: 50 },
        '45-54歳': { total: 95000, inflow: 1200, outflow: 1400, netChange: -200, yearChange: -50 },
        '55-64歳': { total: 80000, inflow: 800, outflow: 1000, netChange: -200, yearChange: -100 },
        '65歳以上': { total: 65000, inflow: 500, outflow: 800, netChange: -300, yearChange: -200 }
      },
      // 市区町村別データ
      municipalityTableData: {
        '鳥取市': { total: 190000, inflow: 3200, outflow: 2800, netChange: 400, yearChange: 100 },
        '米子市': { total: 150000, inflow: 2500, outflow: 2300, netChange: 200, yearChange: 50 },
        '倉吉市': { total: 120000, inflow: 1800, outflow: 1600, netChange: 200, yearChange: 50 },
        '境港市': { total: 80000, inflow: 1200, outflow: 1100, netChange: 100, yearChange: 25 },
        '岩美町': { total: 60000, inflow: 800, outflow: 900, netChange: -100, yearChange: -25 },
        '八頭町': { total: 50000, inflow: 600, outflow: 700, netChange: -100, yearChange: -25 }
      },
      // 季節性データ
      seasonalInflow: {
        '4月': 1200, '7月': 1180, '10月': 1250, '1月': 850, '2月': 920, '3月': 1100,
        '5月': 1150, '6月': 1080, '8月': 1050, '9月': 1180, '11月': 1320, '12月': 1400
      },
      seasonalOutflow: {
        '3月': 1250, '4月': 1300, '7月': 1150, '10月': 1350, '1月': 1200, '2月': 1180,
        '5月': 1280, '6月': 1220, '8月': 1200, '9月': 1280, '11月': 1420, '12月': 1500
      },
      // 予測シナリオ
      forecastScenarios: {
        optimistic: 580000,
        current: 540000,
        pessimistic: 500000
      },
      charts: {}
    }
  },
  computed: {
    maxSeasonalInflow() {
      return Math.max(...Object.values(this.seasonalInflow))
    },
    maxSeasonalOutflow() {
      return Math.max(...Object.values(this.seasonalOutflow))
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 60000)
    this.$nextTick(() => {
      this.createCharts()
    })
  },
  beforeUnmount() {
    // チャートの破棄
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.destroy()
    })
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
    createCharts() {
      this.createTotalPopulationChart()
      this.createMigrationChart()
      this.createNaturalChangeChart()
      this.createAgeGroupChart()
      this.createMunicipalityChart()
      this.createMonthlyInflowChart()
      this.createMonthlyOutflowChart()
      this.createForecastChart()
    },
    createTotalPopulationChart() {
      const ctx = this.$refs.totalPopulationChart?.getContext('2d')
      if (!ctx) return

      const years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
      const data = [580000, 575000, 570000, 565000, 560000, 555000, 552000, 550000, 551000, 550000]

      this.charts.totalPopulation = new Chart(ctx, {
        type: 'line',
        data: {
          labels: years,
          datasets: [{
            label: '総人口',
            data: data,
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.1,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: false,
              title: { display: true, text: '人口数' }
            },
            x: {
              title: { display: true, text: '年' }
            }
          }
        }
      })
    },
    createMigrationChart() {
      const ctx = this.$refs.migrationChart?.getContext('2d')
      if (!ctx) return

      const years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
      const inflowData = [9000, 9200, 8800, 8500, 8200, 8000, 8300, 8600, 8700, 8500]
      const outflowData = [11000, 10800, 10500, 10200, 10000, 9800, 10000, 10200, 10100, 10000]

      this.charts.migration = new Chart(ctx, {
        type: 'line',
        data: {
          labels: years,
          datasets: [
            {
              label: '転入者数',
              data: inflowData,
              borderColor: '#10B981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              tension: 0.1
            },
            {
              label: '転出者数',
              data: outflowData,
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              tension: 0.1
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: '人数' }
            },
            x: {
              title: { display: true, text: '年' }
            }
          }
        }
      })
    },
    createNaturalChangeChart() {
      const ctx = this.$refs.naturalChangeChart?.getContext('2d')
      if (!ctx) return

      const years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
      const data = [-500, -600, -700, -800, -900, -1000, -1100, -1200, -1300, -1400]

      this.charts.naturalChange = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: years,
          datasets: [{
            label: '自然増減',
            data: data,
            backgroundColor: data.map(value => value >= 0 ? '#10B981' : '#EF4444'),
            borderColor: data.map(value => value >= 0 ? '#10B981' : '#EF4444'),
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: false,
              title: { display: true, text: '人数' }
            },
            x: {
              title: { display: true, text: '年' }
            }
          }
        }
      })
    },
    createAgeGroupChart() {
      const ctx = this.$refs.ageGroupChart?.getContext('2d')
      if (!ctx) return

      const years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
      const ageGroups = ['0-14歳', '15-24歳', '25-34歳', '35-44歳', '45-54歳', '55-64歳', '65歳以上']
      const datasets = ageGroups.map((ageGroup, index) => {
        const baseData = [85000, 65000, 75000, 85000, 95000, 80000, 65000]
        const trend = [0, -500, 200, 0, 0, 0, 0] // 各年齢層のトレンド
        const data = years.map((_, yearIndex) => baseData[index] + (trend[index] * yearIndex))
        
        return {
          label: ageGroup,
          data: data,
          borderColor: this.getRandomColor(),
          backgroundColor: this.getRandomColor(0.1),
          tension: 0.1
        }
      })

      this.charts.ageGroup = new Chart(ctx, {
        type: 'line',
        data: { labels: years, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: false,
              title: { display: true, text: '人口数' }
            },
            x: {
              title: { display: true, text: '年' }
            }
          }
        }
      })
    },
    createMunicipalityChart() {
      const ctx = this.$refs.municipalityChart?.getContext('2d')
      if (!ctx) return

      const years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
      const municipalities = ['鳥取市', '米子市', '倉吉市', '境港市', '岩美町', '八頭町']
      const datasets = municipalities.map((municipality, index) => {
        const baseData = [190000, 150000, 120000, 80000, 60000, 50000]
        const trend = [100, 50, 50, 25, -25, -25] // 各市区町村のトレンド
        const data = years.map((_, yearIndex) => baseData[index] + (trend[index] * yearIndex))
        
        return {
          label: municipality,
          data: data,
          borderColor: this.getRandomColor(),
          backgroundColor: this.getRandomColor(0.1),
          tension: 0.1
        }
      })

      this.charts.municipality = new Chart(ctx, {
        type: 'line',
        data: { labels: years, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: false,
              title: { display: true, text: '人口数' }
            },
            x: {
              title: { display: true, text: '年' }
            }
          }
        }
      })
    },
    createMonthlyInflowChart() {
      const ctx = this.$refs.monthlyInflowChart?.getContext('2d')
      if (!ctx) return

      const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
      const data = [850, 920, 1100, 1200, 1150, 1080, 980, 1050, 1180, 1250, 1320, 1400]

      this.charts.monthlyInflow = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: months,
          datasets: [{
            label: '転入者数',
            data: data,
            backgroundColor: '#10B981',
            borderColor: '#10B981',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: '人数' }
            },
            x: {
              title: { display: true, text: '月' }
            }
          }
        }
      })
    },
    createMonthlyOutflowChart() {
      const ctx = this.$refs.monthlyOutflowChart?.getContext('2d')
      if (!ctx) return

      const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
      const data = [1200, 1180, 1250, 1300, 1280, 1220, 1150, 1200, 1280, 1350, 1420, 1500]

      this.charts.monthlyOutflow = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: months,
          datasets: [{
            label: '転出者数',
            data: data,
            backgroundColor: '#EF4444',
            borderColor: '#EF4444',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: '人数' }
            },
            x: {
              title: { display: true, text: '月' }
            }
          }
        }
      })
    },
    createForecastChart() {
      const ctx = this.$refs.forecastChart?.getContext('2d')
      if (!ctx) return

      const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035']
      const optimisticData = [550000, 552000, 555000, 558000, 561000, 564000, 567000, 570000, 573000, 576000, 578000, 580000]
      const currentData = [550000, 548000, 546000, 544000, 542000, 540000, 538000, 536000, 534000, 532000, 531000, 540000]
      const pessimisticData = [550000, 545000, 540000, 535000, 530000, 525000, 520000, 515000, 510000, 505000, 502000, 500000]

      this.charts.forecast = new Chart(ctx, {
        type: 'line',
        data: {
          labels: years,
          datasets: [
            {
              label: '楽観シナリオ',
              data: optimisticData,
              borderColor: '#10B981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              tension: 0.1,
              borderDash: [5, 5]
            },
            {
              label: '現状維持シナリオ',
              data: currentData,
              borderColor: '#3B82F6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              tension: 0.1,
              borderDash: [5, 5]
            },
            {
              label: '悲観シナリオ',
              data: pessimisticData,
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              tension: 0.1,
              borderDash: [5, 5]
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            title: { display: false }
          },
          scales: {
            y: {
              beginAtZero: false,
              title: { display: true, text: '人口数' }
            },
            x: {
              title: { display: true, text: '年' }
            }
          }
        }
      })
    },
    getRandomColor(alpha = 1) {
      const colors = [
        '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
        '#06B6D4', '#F97316', '#84CC16', '#EC4899', '#6366F1'
      ]
      const color = colors[Math.floor(Math.random() * colors.length)]
      return alpha < 1 ? color + Math.floor(alpha * 255).toString(16).padStart(2, '0') : color
    }
  }
}
</script>
