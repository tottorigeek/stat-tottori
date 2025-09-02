<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-800">⚖️ 住みやすさ指標配点設定</h3>
      <div class="flex items-center space-x-3">
        <select v-model="selectedPreset" @change="applyPreset" class="border rounded px-3 py-2 text-sm">
          <option value="">カスタム配点</option>
          <option value="standard">標準配点</option>
          <option value="family">子育て重視</option>
          <option value="senior">シニア重視</option>
          <option value="business">ビジネス重視</option>
          <option value="student">学生・若年層重視</option>
        </select>
        <button @click="saveConfiguration" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm">
          設定保存
        </button>
        <button @click="resetToDefault" class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded text-sm">
          リセット
        </button>
      </div>
    </div>

    <!-- 配点設定セクション -->
    <div class="space-y-6 mb-8">
      <div v-for="category in categories" :key="category.id" class="border rounded-lg p-4">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <span class="text-2xl mr-3">{{ category.icon }}</span>
            <div>
              <h4 class="font-semibold text-gray-800">{{ category.name }}</h4>
              <p class="text-sm text-gray-600">{{ category.description }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <span class="text-lg font-bold text-blue-600">{{ category.weight }}%</span>
            <button @click="expandCategory(category.id)" 
                    class="text-gray-500 hover:text-gray-700">
              <svg :class="{ 'rotate-180': expandedCategories.includes(category.id) }" 
                   class="w-4 h-4 transition-transform" 
                   fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 重み付けスライダー -->
        <div class="mb-4">
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm text-gray-600">配点の重み</label>
            <span class="text-sm text-gray-500">{{ category.weight }}% ({{ calculateActualWeight(category.weight) }}ポイント)</span>
          </div>
          <div class="relative">
            <input 
              type="range" 
              v-model="category.weight" 
              @input="updateWeights"
              min="0" 
              max="50" 
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>25%</span>
              <span>50%</span>
            </div>
          </div>
        </div>

        <!-- カテゴリ詳細（展開時） -->
        <div v-if="expandedCategories.includes(category.id)" class="space-y-3 pt-4 border-t border-gray-200">
          <div v-for="indicator in category.indicators" :key="indicator.id" class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">{{ indicator.name }}</span>
                <div class="flex items-center space-x-2">
                  <span class="text-xs text-gray-500">{{ indicator.unit }}</span>
                  <span class="text-sm font-semibold text-gray-800">{{ indicator.subWeight }}%</span>
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ indicator.description }}</p>
              
              <!-- サブ指標の重み付け -->
              <div class="mt-2">
                <input 
                  type="range" 
                  v-model="indicator.subWeight" 
                  @input="normalizeSubWeights(category.id)"
                  min="0" 
                  max="100" 
                  class="w-full h-1 bg-gray-200 rounded appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 総配点確認 -->
    <div class="mb-6 p-4 bg-gray-50 rounded-lg">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-semibold text-gray-800">配点合計確認</h4>
        <span :class="getTotalWeightColor()" class="text-lg font-bold">{{ totalWeight }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div :class="getTotalWeightBarColor()" 
             class="h-3 rounded-full transition-all duration-500" 
             :style="{ width: Math.min(totalWeight, 100) + '%' }">
        </div>
      </div>
      <p class="text-xs text-gray-600 mt-2">
        <span v-if="totalWeight === 100" class="text-green-600">✓ 配点設定が完了しました</span>
        <span v-else-if="totalWeight > 100" class="text-red-600">⚠ 合計が100%を超えています ({{ totalWeight - 100 }}%)</span>
        <span v-else class="text-orange-600">⚠ 合計が100%未満です (残り{{ 100 - totalWeight }}%)</span>
      </p>
    </div>

    <!-- 配点結果プレビュー -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-4">配点結果プレビュー</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- スコア分布チャート -->
        <div class="p-4 border rounded-lg">
          <h5 class="font-medium text-gray-700 mb-3">カテゴリ別重み分布</h5>
          <div class="space-y-2">
            <div v-for="category in categories" :key="category.id" class="flex items-center">
              <div class="w-4 h-4 rounded mr-2" :style="{ backgroundColor: category.color }"></div>
              <span class="text-sm text-gray-600 flex-1">{{ category.name }}</span>
              <span class="text-sm font-semibold text-gray-800">{{ category.weight }}%</span>
            </div>
          </div>
        </div>

        <!-- 影響度シミュレーション -->
        <div class="p-4 border rounded-lg">
          <h5 class="font-medium text-gray-700 mb-3">改善影響度シミュレーション</h5>
          <div class="space-y-3">
            <div v-for="simulation in simulationResults" :key="simulation.category" class="text-sm">
              <div class="flex justify-between items-center mb-1">
                <span class="text-gray-600">{{ simulation.category }}が10%改善した場合</span>
                <span :class="getImpactColor(simulation.impact)" class="font-semibold">
                  +{{ simulation.impact.toFixed(1) }}pt
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1">
                <div class="bg-blue-500 h-1 rounded-full" 
                     :style="{ width: (simulation.impact / maxImpact * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存された設定一覧 -->
    <div v-if="savedConfigurations.length > 0">
      <h4 class="text-lg font-semibold text-gray-800 mb-4">保存済み設定</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="config in savedConfigurations" :key="config.id" 
             class="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
             @click="loadConfiguration(config)">
          <div class="flex items-start justify-between">
            <div>
              <h5 class="font-medium text-gray-800">{{ config.name }}</h5>
              <p class="text-xs text-gray-500">{{ formatDate(config.createdAt) }}</p>
            </div>
            <div class="flex space-x-1">
              <button @click.stop="loadConfiguration(config)" 
                      class="text-blue-600 hover:text-blue-800 text-xs">
                読込
              </button>
              <button @click.stop="deleteConfiguration(config.id)" 
                      class="text-red-600 hover:text-red-800 text-xs">
                削除
              </button>
            </div>
          </div>
          <div class="mt-2">
            <div class="flex text-xs text-gray-600">
              <span>人口: {{ config.weights.population }}%</span>
              <span class="ml-2">経済: {{ config.weights.economy }}%</span>
              <span class="ml-2">教育: {{ config.weights.education }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- データ更新時刻 -->
    <div class="mt-6 pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500">設定更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LivabilityScoreConfiguration',
  data() {
    return {
      selectedPreset: '',
      expandedCategories: [],
      lastUpdated: '',
      
      // 配点カテゴリ設定
      categories: [
        {
          id: 'population',
          name: '人口・世帯',
          icon: '👨‍👩‍👧‍👦',
          description: '人口動態、年齢構成、世帯数の推移',
          weight: 15,
          color: '#3B82F6',
          indicators: [
            { id: 'pop_growth', name: '人口増減率', unit: '%/年', subWeight: 40, description: '前年比人口増減率' },
            { id: 'age_structure', name: '年齢構成バランス', unit: '指数', subWeight: 30, description: '生産年齢人口比率' },
            { id: 'household', name: '世帯数推移', unit: '世帯/年', subWeight: 30, description: '新規世帯形成数' }
          ]
        },
        {
          id: 'economy',
          name: '経済・雇用',
          icon: '💼',
          description: '就業環境、所得水準、産業の多様性',
          weight: 20,
          color: '#10B981',
          indicators: [
            { id: 'employment', name: '就業率', unit: '%', subWeight: 35, description: '15-64歳就業率' },
            { id: 'income', name: '平均所得', unit: '万円', subWeight: 35, description: '世帯平均所得' },
            { id: 'industry', name: '産業多様性', unit: '指数', subWeight: 30, description: '産業別就業者バランス' }
          ]
        },
        {
          id: 'education',
          name: '教育・子育て',
          icon: '🎓',
          description: '教育環境、保育施設、子育て支援の充実度',
          weight: 15,
          color: '#F59E0B',
          indicators: [
            { id: 'schools', name: '教育機関充実度', unit: '校/人', subWeight: 30, description: '人口当たり学校数' },
            { id: 'childcare', name: '保育環境', unit: '施設/人', subWeight: 40, description: '待機児童ゼロ達成度' },
            { id: 'support', name: '子育て支援制度', unit: '指数', subWeight: 30, description: '支援制度の充実度' }
          ]
        },
        {
          id: 'healthcare',
          name: '医療・福祉',
          icon: '🏥',
          description: '医療機関、医師数、福祉サービスの充実度',
          weight: 15,
          color: '#EF4444',
          indicators: [
            { id: 'hospitals', name: '医療機関密度', unit: '施設/人', subWeight: 40, description: '人口当たり医療機関数' },
            { id: 'doctors', name: '医師充足度', unit: '人/人', subWeight: 35, description: '人口当たり医師数' },
            { id: 'welfare', name: '福祉サービス', unit: '指数', subWeight: 25, description: '高齢者・障がい者支援充実度' }
          ]
        },
        {
          id: 'transportation',
          name: '交通・アクセス',
          icon: '🚌',
          description: '公共交通、道路整備、アクセス利便性',
          weight: 10,
          color: '#8B5CF6',
          indicators: [
            { id: 'public_transport', name: '公共交通利便性', unit: '指数', subWeight: 40, description: 'バス・電車の運行頻度' },
            { id: 'roads', name: '道路整備状況', unit: '%', subWeight: 30, description: '道路舗装率・渋滞状況' },
            { id: 'access', name: '広域アクセス', unit: '分', subWeight: 30, description: '空港・主要都市への所要時間' }
          ]
        },
        {
          id: 'housing',
          name: '住環境',
          icon: '🏠',
          description: '住宅価格、土地価格、住宅供給、治安状況',
          weight: 10,
          color: '#06B6D4',
          indicators: [
            { id: 'house_price', name: '住宅価格適正性', unit: '指数', subWeight: 35, description: '所得比住宅価格' },
            { id: 'safety', name: '治安・安全性', unit: '件/人', subWeight: 35, description: '人口当たり犯罪発生率' },
            { id: 'housing_supply', name: '住宅供給', unit: '戸/年', subWeight: 30, description: '新規住宅供給数' }
          ]
        },
        {
          id: 'environment',
          name: '自然・環境',
          icon: '🌱',
          description: '自然環境、公園・緑地、環境保全の取り組み',
          weight: 8,
          color: '#84CC16',
          indicators: [
            { id: 'nature', name: '自然環境豊かさ', unit: '指数', subWeight: 40, description: '森林率・海岸線・山岳' },
            { id: 'parks', name: '公園・緑地面積', unit: 'm²/人', subWeight: 35, description: '人口当たり公園面積' },
            { id: 'environment', name: '環境保全度', unit: '指数', subWeight: 25, description: '大気・水質・騒音レベル' }
          ]
        },
        {
          id: 'culture',
          name: '文化・レジャー',
          icon: '🎭',
          description: '文化施設、スポーツ施設、観光・レジャー資源',
          weight: 7,
          color: '#EC4899',
          indicators: [
            { id: 'cultural_facilities', name: '文化施設充実度', unit: '施設/人', subWeight: 35, description: '美術館・図書館・ホール数' },
            { id: 'sports', name: 'スポーツ環境', unit: '施設/人', subWeight: 30, description: 'スポーツ施設・設備充実度' },
            { id: 'tourism', name: '観光・レジャー', unit: '指数', subWeight: 35, description: '観光地・イベント・名所' }
          ]
        }
      ],
      
      // プリセット配点パターン
      presets: {
        standard: {
          population: 15, economy: 20, education: 15, healthcare: 15,
          transportation: 10, housing: 10, environment: 8, culture: 7
        },
        family: {
          population: 10, economy: 15, education: 25, healthcare: 20,
          transportation: 12, housing: 12, environment: 4, culture: 2
        },
        senior: {
          population: 8, economy: 10, education: 5, healthcare: 30,
          transportation: 15, housing: 15, environment: 10, culture: 7
        },
        business: {
          population: 12, economy: 35, education: 8, healthcare: 10,
          transportation: 20, housing: 8, environment: 4, culture: 3
        },
        student: {
          population: 20, economy: 15, education: 20, healthcare: 8,
          transportation: 15, housing: 15, environment: 5, culture: 2
        }
      },
      
      // 保存された設定
      savedConfigurations: [
        {
          id: 1,
          name: '子育て世帯向け配点',
          createdAt: new Date('2024-12-15'),
          weights: { population: 10, economy: 15, education: 25, healthcare: 20 }
        },
        {
          id: 2,
          name: '企業誘致重視配点',
          createdAt: new Date('2024-12-10'),
          weights: { population: 12, economy: 35, education: 8, healthcare: 10 }
        }
      ]
    }
  },
  computed: {
    totalWeight() {
      return this.categories.reduce((sum, cat) => sum + parseInt(cat.weight), 0)
    },
    simulationResults() {
      return this.categories.map(cat => ({
        category: cat.name,
        impact: (cat.weight / 100) * 10 // 10%改善時のスコア影響度
      }))
    },
    maxImpact() {
      return Math.max(...this.simulationResults.map(s => s.impact))
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
    updateWeights() {
      // 配点合計が100%を超える場合の自動調整ロジック
      if (this.totalWeight > 100) {
        const excess = this.totalWeight - 100
        const nonZeroCategories = this.categories.filter(cat => cat.weight > 0)
        const reductionPerCategory = excess / nonZeroCategories.length
        
        nonZeroCategories.forEach(cat => {
          cat.weight = Math.max(0, cat.weight - reductionPerCategory)
        })
      }
    },
    expandCategory(categoryId) {
      const index = this.expandedCategories.indexOf(categoryId)
      if (index > -1) {
        this.expandedCategories.splice(index, 1)
      } else {
        this.expandedCategories.push(categoryId)
      }
    },
    normalizeSubWeights(categoryId) {
      const category = this.categories.find(cat => cat.id === categoryId)
      if (category) {
        const totalSubWeight = category.indicators.reduce((sum, ind) => sum + parseInt(ind.subWeight), 0)
        if (totalSubWeight !== 100) {
          // サブ重みを100%に正規化
          const factor = 100 / totalSubWeight
          category.indicators.forEach(ind => {
            ind.subWeight = Math.round(ind.subWeight * factor)
          })
        }
      }
    },
    applyPreset() {
      if (this.selectedPreset && this.presets[this.selectedPreset]) {
        const preset = this.presets[this.selectedPreset]
        this.categories.forEach(cat => {
          cat.weight = preset[cat.id] || 0
        })
      }
    },
    resetToDefault() {
      this.selectedPreset = 'standard'
      this.applyPreset()
    },
    saveConfiguration() {
      const name = prompt('設定名を入力してください:')
      if (name) {
        const config = {
          id: Date.now(),
          name: name,
          createdAt: new Date(),
          weights: {}
        }
        this.categories.forEach(cat => {
          config.weights[cat.id] = cat.weight
        })
        this.savedConfigurations.push(config)
        alert('設定を保存しました')
      }
    },
    loadConfiguration(config) {
      this.categories.forEach(cat => {
        cat.weight = config.weights[cat.id] || 0
      })
      this.selectedPreset = ''
    },
    deleteConfiguration(configId) {
      if (confirm('この設定を削除しますか？')) {
        this.savedConfigurations = this.savedConfigurations.filter(c => c.id !== configId)
      }
    },
    getTotalWeightColor() {
      if (this.totalWeight === 100) return 'text-green-600'
      if (this.totalWeight > 100) return 'text-red-600'
      return 'text-orange-600'
    },
    getTotalWeightBarColor() {
      if (this.totalWeight === 100) return 'bg-green-500'
      if (this.totalWeight > 100) return 'bg-red-500'
      return 'bg-orange-500'
    },
    getImpactColor(impact) {
      if (impact > 1.5) return 'text-red-600'
      if (impact > 1.0) return 'text-orange-600'
      return 'text-blue-600'
    },
    calculateActualWeight(weight) {
      return (weight * 100 / this.totalWeight).toFixed(1)
    },
    formatDate(date) {
      return date.toLocaleDateString('ja-JP', { 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.2);
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.2);
}
</style>