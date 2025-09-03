<template>
  <div class="min-h-screen bg-gray-50">
    <!-- ヘッダー -->
    <header class="bg-purple-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold">📊 D3.js 高度可視化サンプル</h1>
        <p class="text-purple-100 mt-2">インタラクティブなデータ可視化コンポーネントのデモ</p>
      </div>
    </header>

    <!-- 共通ナビゲーションバー -->
    <CommonNavigation />

    <!-- メインコンテンツ -->
    <main class="container mx-auto px-4 py-8">
      
      <!-- ネットワーク可視化サンプル -->
      <section class="mb-12">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">🌐 ネットワーク可視化</h2>
          <p class="text-gray-600 mb-6">鳥取県内の地域間関係や政策影響のネットワーク図</p>
          
          <NetworkVisualization
            :nodes="networkNodes"
            :links="networkLinks"
            :height="500"
            category-field="category"
            label-field="name"
            value-field="population"
            @node-click="onNodeClick"
            @link-click="onLinkClick"
          />
          
          <div class="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 class="font-semibold text-blue-800">操作方法:</h4>
            <ul class="text-blue-700 text-sm mt-2 space-y-1">
              <li>• ノードをドラッグして位置を変更</li>
              <li>• Force強度で引力を調整</li>
              <li>• 接続距離でノード間の距離を調整</li>
              <li>• ノードやリンクをクリックで詳細情報表示</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 時系列分析サンプル -->
      <section class="mb-12">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">📈 インタラクティブ時系列分析</h2>
          <p class="text-gray-600 mb-6">鳥取県の人口動態と出生・死亡数の推移</p>
          
          <TimeSeriesAnalysis
            :data="timeSeriesData"
            :value-fields="['population', 'births', 'deaths']"
            :height="400"
            date-field="date"
            :show-brush="true"
            :enable-zoom="true"
            @period-selected="onPeriodSelected"
          />
          
          <div class="mt-4 p-4 bg-green-50 rounded-lg">
            <h4 class="font-semibold text-green-800">操作方法:</h4>
            <ul class="text-green-700 text-sm mt-2 space-y-1">
              <li>• チェックボックスで表示系列の切り替え</li>
              <li>• マウスホイールでズーム</li>
              <li>• 下部のブラシで期間選択</li>
              <li>• グラフにマウスオーバーで詳細データ表示</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- データ情報 -->
      <section class="mb-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">📋 表示データについて</h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-semibold text-gray-700 mb-2">ネットワークデータ</h4>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• ノード: {{ networkNodes.length }}個の地域・機関</li>
                <li>• リンク: {{ networkLinks.length }}個の関係性</li>
                <li>• カテゴリ: 市、町村、県機関</li>
              </ul>
            </div>
            <div>
              <h4 class="font-semibold text-gray-700 mb-2">時系列データ</h4>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• 期間: {{ timeSeriesData.length }}ヶ月分</li>
                <li>• 指標: 人口、出生数、死亡数</li>
                <li>• 更新: 月次データ</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- 選択したデータの詳細表示 -->
      <section v-if="selectedData.node || selectedData.period" class="mb-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">🔍 選択データ詳細</h3>
          
          <!-- ノード選択時 -->
          <div v-if="selectedData.node" class="mb-4">
            <h4 class="font-semibold text-blue-600 mb-2">選択されたノード</h4>
            <div class="bg-blue-50 p-4 rounded-lg">
              <p><strong>名前:</strong> {{ selectedData.node.name }}</p>
              <p><strong>カテゴリ:</strong> {{ selectedData.node.category }}</p>
              <p><strong>人口:</strong> {{ selectedData.node.population?.toLocaleString() }}人</p>
            </div>
          </div>

          <!-- 期間選択時 -->
          <div v-if="selectedData.period" class="mb-4">
            <h4 class="font-semibold text-green-600 mb-2">選択された期間</h4>
            <div class="bg-green-50 p-4 rounded-lg">
              <p><strong>開始:</strong> {{ formatDate(selectedData.period.start) }}</p>
              <p><strong>終了:</strong> {{ formatDate(selectedData.period.end) }}</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import NetworkVisualization from '@/components/d3/NetworkVisualization.vue'
import TimeSeriesAnalysis from '@/components/d3/TimeSeriesAnalysis.vue'
import CommonNavigation from '@/components/CommonNavigation.vue'

export default {
  name: 'D3Samples',
  components: {
    NetworkVisualization,
    TimeSeriesAnalysis,
    CommonNavigation
  },
  data() {
    return {
      selectedData: {
        node: null,
        period: null
      },
      networkNodes: [
        { id: 'tottori', name: '鳥取市', category: '市', population: 190000, value: 190 },
        { id: 'yonago', name: '米子市', category: '市', population: 150000, value: 150 },
        { id: 'kurayoshi', name: '倉吉市', category: '市', population: 50000, value: 50 },
        { id: 'sakaiminato', name: '境港市', category: '市', population: 35000, value: 35 },
        { id: 'iwami', name: '岩美町', category: '町村', population: 11000, value: 11 },
        { id: 'chizu', name: '智頭町', category: '町村', population: 7000, value: 7 },
        { id: 'wakasa', name: '若桜町', category: '町村', population: 3000, value: 3 },
        { id: 'yazu', name: '八頭町', category: '町村', population: 17000, value: 17 },
        { id: 'misasa', name: '三朝町', category: '町村', population: 7000, value: 7 },
        { id: 'yurihama', name: '湯梨浜町', category: '町村', population: 17000, value: 17 },
        { id: 'kotoura', name: '琴浦町', category: '町村', population: 18000, value: 18 },
        { id: 'hokuei', name: '北栄町', category: '町村', population: 15000, value: 15 },
        { id: 'daisen', name: '大山町', category: '町村', population: 17000, value: 17 },
        { id: 'nanbu', name: '南部町', category: '町村', population: 11000, value: 11 },
        { id: 'hiezu', name: '日吉津村', category: '町村', population: 3500, value: 4 },
        { id: 'hino', name: '日野町', category: '町村', population: 3500, value: 4 },
        { id: 'kofu', name: '江府町', category: '町村', population: 3000, value: 3 },
        { id: 'pref', name: '鳥取県庁', category: '県機関', population: null, value: 100 },
        { id: 'univ', name: '鳥取大学', category: '教育機関', population: null, value: 80 },
        { id: 'airport', name: '鳥取空港', category: 'インフラ', population: null, value: 60 }
      ],
      networkLinks: [
        // 県庁との関係
        { source: 'pref', target: 'tottori', value: 90 },
        { source: 'pref', target: 'yonago', value: 80 },
        { source: 'pref', target: 'kurayoshi', value: 70 },
        { source: 'pref', target: 'sakaiminato', value: 60 },
        
        // 市と町村の関係（地理的近接）
        { source: 'tottori', target: 'iwami', value: 40 },
        { source: 'tottori', target: 'chizu', value: 30 },
        { source: 'tottori', target: 'wakasa', value: 25 },
        { source: 'tottori', target: 'yazu', value: 45 },
        
        { source: 'kurayoshi', target: 'misasa', value: 35 },
        { source: 'kurayoshi', target: 'yurihama', value: 40 },
        { source: 'kurayoshi', target: 'kotoura', value: 35 },
        { source: 'kurayoshi', target: 'hokuei', value: 30 },
        
        { source: 'yonago', target: 'daisen', value: 45 },
        { source: 'yonago', target: 'nanbu', value: 35 },
        { source: 'yonago', target: 'hiezu', value: 50 },
        { source: 'sakaiminato', target: 'yonago', value: 80 },
        { source: 'sakaiminato', target: 'hiezu', value: 40 },
        
        { source: 'daisen', target: 'hino', value: 20 },
        { source: 'nanbu', target: 'hino', value: 25 },
        { source: 'hino', target: 'kofu', value: 30 },
        
        // 大学との関係
        { source: 'univ', target: 'tottori', value: 70 },
        { source: 'univ', target: 'yonago', value: 50 },
        { source: 'univ', target: 'kurayoshi', value: 30 },
        
        // 空港との関係
        { source: 'airport', target: 'tottori', value: 60 },
        { source: 'airport', target: 'yonago', value: 40 },
        
        // 市同士の関係
        { source: 'tottori', target: 'kurayoshi', value: 50 },
        { source: 'kurayoshi', target: 'yonago', value: 45 },
        { source: 'yonago', target: 'tottori', value: 40 }
      ],
      timeSeriesData: []
    }
  },
  mounted() {
    this.generateTimeSeriesData()
  },
  methods: {
    generateTimeSeriesData() {
      const startDate = new Date('2020-01-01')
      const months = 48 // 4年間
      const data = []
      
      let basePopulation = 570000
      
      for (let i = 0; i < months; i++) {
        const date = new Date(startDate)
        date.setMonth(date.getMonth() + i)
        
        // 季節変動を含む人口推移（減少傾向）
        const seasonality = Math.sin((i / 12) * 2 * Math.PI) * 500
        const trend = -i * 50 // 月50人ずつ減少
        const noise = (Math.random() - 0.5) * 200
        const population = Math.round(basePopulation + trend + seasonality + noise)
        
        // 出生数（春に多い傾向）
        const birthSeasonality = Math.sin(((i + 3) / 12) * 2 * Math.PI) * 200 + 400
        const birthNoise = (Math.random() - 0.5) * 100
        const births = Math.round(Math.max(0, birthSeasonality + birthNoise))
        
        // 死亡数（冬に多い傾向）
        const deathSeasonality = Math.sin(((i + 9) / 12) * 2 * Math.PI) * 300 + 500
        const deathNoise = (Math.random() - 0.5) * 150
        const deaths = Math.round(Math.max(0, deathSeasonality + deathNoise))
        
        data.push({
          date: date.toISOString().split('T')[0],
          population,
          births,
          deaths
        })
      }
      
      this.timeSeriesData = data
    },

    onNodeClick(node, event) {
      this.selectedData.node = node
      console.log('Node clicked:', node)
    },

    onLinkClick(link, event) {
      console.log('Link clicked:', link)
    },

    onPeriodSelected(period) {
      this.selectedData.period = period
      console.log('Period selected:', period)
    },

    formatDate(date) {
      if (!date) return ''
      return new Intl.DateTimeFormat('ja-JP').format(new Date(date))
    }
  }
}
</script>

<style scoped>
/* 追加のスタイルがあれば記述 */
</style>