<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-purple-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">📈 人口詳細分析</h1>
            <p class="text-purple-100 mt-2">すたっととっとり - 鳥取県の人口動態を年齢別・市区町村別で分析</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-purple-100">最終更新: {{ lastUpdated }}</p>
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

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <!-- 概要カード -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">総人口</h3>
          <p class="text-3xl font-bold text-blue-600">{{ populationSummary.total.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ populationSummary.change > 0 ? '+' : '' }}{{ populationSummary.change }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">転入者数</h3>
          <p class="text-3xl font-bold text-green-600">{{ populationSummary.inflow.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ populationSummary.inflowChange > 0 ? '+' : '' }}{{ populationSummary.inflowChange }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">転出者数</h3>
          <p class="text-3xl font-bold text-red-600">{{ populationSummary.outflow.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ populationSummary.outflowChange > 0 ? '+' : '' }}{{ populationSummary.outflowChange }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">自然増減</h3>
          <p class="text-3xl font-bold text-purple-600">{{ populationSummary.naturalChange > 0 ? '+' : '' }}{{ populationSummary.naturalChange }}人</p>
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
      <div v-if="activeTab === 'age'" class="space-y-8">
        <!-- 年齢別人口推移 -->
        <PopulationChart 
          title="年齢別人口推移（転入・転出）" 
          :data="ageGroupData" 
          type="line"
        />
        
        <!-- 年齢別詳細テーブル -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">年齢別人口詳細</h3>
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
        <PopulationChart 
          title="市区町村別人口推移（転入・転出）" 
          :data="municipalityData" 
          type="line"
        />
        
        <!-- 市区町村別詳細テーブル -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">市区町村別人口詳細</h3>
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

      <div v-else-if="activeTab === 'trend'" class="space-y-8">
        <!-- 月別推移グラフ -->
        <PopulationChart 
          title="月別人口移動推移" 
          :data="monthlyTrendData" 
          type="bar"
        />
        
        <!-- 季節性分析 -->
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
import PopulationChart from '../components/PopulationChart.vue'
import CommonNavigation from '../components/CommonNavigation.vue'

export default {
  name: 'PopulationDetail',
  components: {
    PopulationChart,
    CommonNavigation
  },
  data() {
    return {
      lastUpdated: '',
      activeTab: 'age',
      tabs: [
        { id: 'age', name: '年齢別分析' },
        { id: 'municipality', name: '市区町村別分析' },
        { id: 'trend', name: '推移・季節性分析' }
      ],
      populationSummary: {
        total: 550000,
        change: -1500,
        inflow: 8500,
        inflowChange: 200,
        outflow: 10000,
        outflowChange: -300,
        naturalChange: -200
      },
      // 年齢別データ
      ageGroupData: {
        ageGroups: {
          '0-14歳': { '2024/1': 120, '2024/2': 115, '2024/3': 118, '2024/4': 122, '2024/5': 125, '2024/6': 128, '2024/7': 130, '2024/8': 132, '2024/9': 135, '2024/10': 138, '2024/11': 140, '2024/12': 142 },
          '15-24歳': { '2024/1': 180, '2024/2': 175, '2024/3': 170, '2024/4': 165, '2024/5': 160, '2024/6': 155, '2024/7': 150, '2024/8': 145, '2024/9': 140, '2024/10': 135, '2024/11': 130, '2024/12': 125 },
          '25-34歳': { '2024/1': 200, '2024/2': 205, '2024/3': 210, '2024/4': 215, '2024/5': 220, '2024/6': 225, '2024/7': 230, '2024/8': 235, '2024/9': 240, '2024/10': 245, '2024/11': 250, '2024/12': 255 },
          '35-44歳': { '2024/1': 150, '2024/2': 155, '2024/3': 160, '2024/4': 165, '2024/5': 170, '2024/6': 175, '2024/7': 180, '2024/8': 185, '2024/9': 190, '2024/10': 195, '2024/11': 200, '2024/12': 205 },
          '45-54歳': { '2024/1': 100, '2024/2': 105, '2024/3': 110, '2024/4': 115, '2024/5': 120, '2024/6': 125, '2024/7': 130, '2024/8': 135, '2024/9': 140, '2024/10': 145, '2024/11': 150, '2024/12': 155 },
          '55-64歳': { '2024/1': 80, '2024/2': 85, '2024/3': 90, '2024/4': 95, '2024/5': 100, '2024/6': 105, '2024/7': 110, '2024/8': 115, '2024/9': 120, '2024/10': 125, '2024/11': 130, '2024/12': 135 },
          '65歳以上': { '2024/1': 60, '2024/2': 65, '2024/3': 70, '2024/4': 75, '2024/5': 80, '2024/6': 85, '2024/7': 90, '2024/8': 95, '2024/9': 100, '2024/10': 105, '2024/11': 110, '2024/12': 115 }
        }
      },
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
      municipalityData: {
        municipalities: {
          '鳥取市': { '2024/1': 190, '2024/2': 195, '2024/3': 200, '2024/4': 205, '2024/5': 210, '2024/6': 215, '2024/7': 220, '2024/8': 225, '2024/9': 230, '2024/10': 235, '2024/11': 240, '2024/12': 245 },
          '米子市': { '2024/1': 150, '2024/2': 155, '2024/3': 160, '2024/4': 165, '2024/5': 170, '2024/6': 175, '2024/7': 180, '2024/8': 185, '2024/9': 190, '2024/10': 195, '2024/11': 200, '2024/12': 205 },
          '倉吉市': { '2024/1': 120, '2024/2': 125, '2024/3': 130, '2024/4': 135, '2024/5': 140, '2024/6': 145, '2024/7': 150, '2024/8': 155, '2024/9': 160, '2024/10': 165, '2024/11': 170, '2024/12': 175 },
          '境港市': { '2024/1': 80, '2024/2': 85, '2024/3': 90, '2024/4': 95, '2024/5': 100, '2024/6': 105, '2024/7': 110, '2024/8': 115, '2024/9': 120, '2024/10': 125, '2024/11': 130, '2024/12': 135 },
          '岩美町': { '2024/1': 60, '2024/2': 65, '2024/3': 70, '2024/4': 75, '2024/5': 80, '2024/6': 85, '2024/7': 90, '2024/8': 95, '2024/9': 100, '2024/10': 105, '2024/11': 110, '2024/12': 115 },
          '八頭町': { '2024/1': 50, '2024/2': 55, '2024/3': 60, '2024/4': 65, '2024/5': 70, '2024/6': 75, '2024/7': 80, '2024/8': 85, '2024/9': 90, '2024/10': 95, '2024/11': 100, '2024/12': 105 }
        }
      },
      municipalityTableData: {
        '鳥取市': { total: 190000, inflow: 3200, outflow: 2800, netChange: 400, yearChange: 100 },
        '米子市': { total: 150000, inflow: 2500, outflow: 2300, netChange: 200, yearChange: 50 },
        '倉吉市': { total: 120000, inflow: 1800, outflow: 1600, netChange: 200, yearChange: 50 },
        '境港市': { total: 80000, inflow: 1200, outflow: 1100, netChange: 100, yearChange: 25 },
        '岩美町': { total: 60000, inflow: 800, outflow: 900, netChange: -100, yearChange: -25 },
        '八頭町': { total: 50000, inflow: 600, outflow: 700, netChange: -100, yearChange: -25 }
      },
      // 月別推移データ
      monthlyTrendData: {
        ageGroups: {
          '転入者数': { '2024/1': 850, '2024/2': 920, '2024/3': 1100, '2024/4': 1200, '2024/5': 1150, '2024/6': 1080, '2024/7': 980, '2024/8': 1050, '2024/9': 1180, '2024/10': 1250, '2024/11': 1320, '2024/12': 1400 },
          '転出者数': { '2024/1': 1200, '2024/2': 1180, '2024/3': 1250, '2024/4': 1300, '2024/5': 1280, '2024/6': 1220, '2024/7': 1150, '2024/8': 1200, '2024/9': 1280, '2024/10': 1350, '2024/11': 1420, '2024/12': 1500 }
        }
      },
      // 季節性データ
      seasonalInflow: {
        '4月': 1200,
        '7月': 1180,
        '10月': 1250,
        '1月': 850,
        '2月': 920,
        '3月': 1100,
        '5月': 1150,
        '6月': 1080,
        '8月': 1050,
        '9月': 1180,
        '11月': 1320,
        '12月': 1400
      },
      seasonalOutflow: {
        '3月': 1250,
        '4月': 1300,
        '7月': 1150,
        '10月': 1350,
        '1月': 1200,
        '2月': 1180,
        '5月': 1280,
        '6月': 1220,
        '8月': 1200,
        '9月': 1280,
        '11月': 1420,
        '12月': 1500
      }
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
