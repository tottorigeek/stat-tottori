<template>
  <div class="container mx-auto px-4 py-8">
    <!-- ページヘッダー -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">⚖️ 住みやすさ指標配点システム</h1>
      <p class="text-gray-600">
        鳥取県の住みやすさを評価する指標の重み付けをカスタマイズし、あなたの価値観に合った評価を行います
      </p>
    </div>

    <!-- システム概要・利用方法 -->
    <div class="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h2 class="text-xl font-semibold text-blue-800 mb-4">💡 このシステムについて</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 class="font-semibold text-blue-700 mb-2">システムの目的</h3>
          <ul class="text-sm text-blue-700 space-y-1">
            <li>• 個人の価値観に応じた住みやすさ評価</li>
            <li>• 透明性のある評価基準の提供</li>
            <li>• 政策立案者への客観的データ提供</li>
            <li>• 住民参加型の地域評価システム</li>
          </ul>
        </div>
        <div>
          <h3 class="font-semibold text-blue-700 mb-2">利用方法</h3>
          <ol class="text-sm text-blue-700 space-y-1">
            <li>1. プリセット配点を選択または独自に設定</li>
            <li>2. 各カテゴリの重み付けを調整</li>
            <li>3. 詳細指標の重要度を微調整</li>
            <li>4. リアルタイムでスコア影響を確認</li>
            <li>5. 設定を保存して継続利用</li>
          </ol>
        </div>
      </div>
    </div>

    <!-- 配点設定コンポーネント -->
    <div class="mb-8">
      <LivabilityScoreConfiguration 
        @scoreUpdated="handleScoreUpdate"
        @configurationSaved="handleConfigurationSaved"
      />
    </div>

    <!-- リアルタイム評価結果 -->
    <div class="mb-8">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-6">📊 現在の設定による評価結果</h3>
        
        <!-- 鳥取県の総合スコア -->
        <div class="text-center mb-8 p-6 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
          <h4 class="text-2xl font-bold text-gray-800 mb-2">鳥取県 総合住みやすさスコア</h4>
          <div class="text-6xl font-bold text-blue-600 mb-2">{{ currentTotalScore }}</div>
          <div class="text-lg text-gray-600">{{ getScoreGrade(currentTotalScore) }}</div>
          <div class="mt-4 text-sm text-gray-500">
            前回設定時: {{ previousScore }}点 ({{ getScoreChange() }})
          </div>
        </div>

        <!-- カテゴリ別詳細スコア -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div v-for="category in categoryScores" :key="category.id" 
               class="p-4 border rounded-lg text-center hover:shadow-md transition-shadow">
            <div class="text-2xl mb-2">{{ category.icon }}</div>
            <h5 class="font-semibold text-gray-800 text-sm mb-1">{{ category.name }}</h5>
            <div class="text-2xl font-bold mb-1" :style="{ color: category.color }">
              {{ category.score }}
            </div>
            <div class="text-xs text-gray-500">重み: {{ category.weight }}%</div>
            <div class="text-xs text-gray-500">寄与度: {{ category.contribution }}pt</div>
          </div>
        </div>

        <!-- 改善ポイント分析 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h5 class="font-semibold text-green-800 mb-3">🚀 高評価項目 (重み付け後)</h5>
            <div class="space-y-2">
              <div v-for="strength in topStrengths" :key="strength.category" 
                   class="flex justify-between items-center">
                <span class="text-sm text-green-700">{{ strength.category }}</span>
                <div class="text-right">
                  <div class="text-sm font-semibold text-green-800">{{ strength.weightedScore }}pt</div>
                  <div class="text-xs text-green-600">(基礎: {{ strength.baseScore }}pt × {{ strength.weight }}%)</div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <h5 class="font-semibold text-orange-800 mb-3">📈 改善余地項目 (重み付け後)</h5>
            <div class="space-y-2">
              <div v-for="weakness in topWeaknesses" :key="weakness.category" 
                   class="flex justify-between items-center">
                <span class="text-sm text-orange-700">{{ weakness.category }}</span>
                <div class="text-right">
                  <div class="text-sm font-semibold text-orange-800">{{ weakness.weightedScore }}pt</div>
                  <div class="text-xs text-orange-600">(基礎: {{ weakness.baseScore }}pt × {{ weakness.weight }}%)</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 他の配点パターンとの比較 -->
    <div class="mb-8">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-6">🔄 異なる配点による比較</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="text-left py-3 px-2 font-semibold text-gray-800">配点パターン</th>
                <th class="text-center py-3 px-2 font-semibold text-gray-800">総合スコア</th>
                <th class="text-center py-3 px-2 font-semibold text-gray-800">評価</th>
                <th class="text-center py-3 px-2 font-semibold text-gray-800">順位変動</th>
                <th class="text-center py-3 px-2 font-semibold text-gray-800">主な差分</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="comparison in comparisonResults" :key="comparison.pattern"
                  :class="comparison.pattern === 'current' ? 'bg-blue-50 border-l-4 border-blue-500' : ''"
                  class="border-b border-gray-100">
                <td class="py-3 px-2">
                  <div class="flex items-center">
                    <span class="font-medium text-gray-800">{{ comparison.name }}</span>
                    <span v-if="comparison.pattern === 'current'" 
                          class="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">現在</span>
                  </div>
                </td>
                <td class="py-3 px-2 text-center">
                  <span :class="getScoreColor(comparison.score)" class="font-bold text-lg">
                    {{ comparison.score }}
                  </span>
                </td>
                <td class="py-3 px-2 text-center">
                  <span class="text-sm text-gray-600">{{ getScoreGrade(comparison.score) }}</span>
                </td>
                <td class="py-3 px-2 text-center">
                  <span :class="getRankChangeColor(comparison.rankChange)" class="font-semibold">
                    {{ comparison.rankChange > 0 ? '+' : '' }}{{ comparison.rankChange }}位
                  </span>
                </td>
                <td class="py-3 px-2 text-center text-xs text-gray-500">
                  {{ comparison.keyDifference }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 配点の妥当性・統計情報 -->
    <div class="mb-8">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-6">📈 配点統計・妥当性分析</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 配点分散度 -->
          <div class="p-4 border rounded-lg text-center">
            <h4 class="font-semibold text-gray-800 mb-2">配点バランス</h4>
            <div class="text-3xl font-bold text-blue-600 mb-2">{{ distributionScore }}</div>
            <div class="text-sm text-gray-600">{{ getDistributionGrade() }}</div>
            <div class="text-xs text-gray-500 mt-2">
              標準偏差: {{ standardDeviation.toFixed(1) }}%
            </div>
          </div>
          
          <!-- 住民志向一致度 -->
          <div class="p-4 border rounded-lg text-center">
            <h4 class="font-semibold text-gray-800 mb-2">住民志向一致度</h4>
            <div class="text-3xl font-bold text-green-600 mb-2">{{ residentAlignment }}%</div>
            <div class="text-sm text-gray-600">{{ getAlignmentGrade() }}</div>
            <div class="text-xs text-gray-500 mt-2">
              住民アンケート結果との相関
            </div>
          </div>
          
          <!-- 政策効果感度 -->
          <div class="p-4 border rounded-lg text-center">
            <h4 class="font-semibold text-gray-800 mb-2">政策効果感度</h4>
            <div class="text-3xl font-bold text-purple-600 mb-2">{{ policySensitivity }}</div>
            <div class="text-sm text-gray-600">{{ getSensitivityGrade() }}</div>
            <div class="text-xs text-gray-500 mt-2">
              政策変更時のスコア反応度
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- データ更新・フィードバック -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- データ更新情報 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">📅 データ更新情報</h3>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600">統計データ</span>
            <span class="text-sm font-semibold text-green-600">2024/12/15 更新済</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600">住民アンケート</span>
            <span class="text-sm font-semibold text-blue-600">2024/12/10 更新済</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600">政策効果データ</span>
            <span class="text-sm font-semibold text-orange-600">2024/12/08 更新中</span>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-200 text-center">
          <p class="text-xs text-gray-500">次回定期更新: 2024年12月末予定</p>
        </div>
      </div>

      <!-- フィードバック・改善提案 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">💭 フィードバック・改善提案</h3>
        <div class="space-y-4">
          <div class="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p class="text-sm text-yellow-800 mb-2">💡 配点提案</p>
            <p class="text-xs text-yellow-700">現在の設定では「経済・雇用」の重みが高めです。「教育・子育て」の重み付けを増やすことで、より住民志向に近い評価になります。</p>
          </div>
          
          <div class="p-3 bg-blue-50 border border-blue-200 rounded">
            <p class="text-sm text-blue-800 mb-2">📊 統計的洞察</p>
            <p class="text-xs text-blue-700">類似自治体と比較して、「自然・環境」分野で高いスコアを維持しています。この強みを活かした政策重点化が有効です。</p>
          </div>
          
          <button class="w-full mt-3 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded text-sm">
            詳細フィードバックを送信
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LivabilityScoreConfiguration from '@/components/LivabilityScoreConfiguration.vue'

export default {
  name: 'LivabilityConfiguration',
  components: {
    LivabilityScoreConfiguration
  },
  data() {
    return {
      currentTotalScore: 72.5,
      previousScore: 70.8,
      
      // カテゴリ別基礎スコア（鳥取県の実際の値）
      baseCategoryScores: {
        population: 65.2,
        economy: 68.8,
        education: 76.5,
        healthcare: 81.2,
        transportation: 62.1,
        housing: 74.8,
        environment: 89.3,
        culture: 69.7
      },
      
      // 現在の重み付け設定
      currentWeights: {
        population: 15,
        economy: 20,
        education: 15,
        healthcare: 15,
        transportation: 10,
        housing: 10,
        environment: 8,
        culture: 7
      },
      
      // 他の配点パターンとの比較結果
      comparisonResults: [
        { 
          pattern: 'current', 
          name: '現在の設定', 
          score: 72.5, 
          rankChange: 0, 
          keyDifference: '基準値' 
        },
        { 
          pattern: 'standard', 
          name: '標準配点', 
          score: 74.2, 
          rankChange: -2, 
          keyDifference: '全項目バランス重視' 
        },
        { 
          pattern: 'family', 
          name: '子育て重視', 
          score: 76.8, 
          rankChange: -5, 
          keyDifference: '教育・医療重視' 
        },
        { 
          pattern: 'senior', 
          name: 'シニア重視', 
          score: 78.1, 
          rankChange: -7, 
          keyDifference: '医療・交通重視' 
        },
        { 
          pattern: 'business', 
          name: 'ビジネス重視', 
          score: 69.3, 
          rankChange: 3, 
          keyDifference: '経済・交通重視' 
        }
      ],
      
      // 配点統計
      distributionScore: 85,
      standardDeviation: 4.2,
      residentAlignment: 78,
      policySensitivity: 92
    }
  },
  computed: {
    categoryScores() {
      const categories = [
        { id: 'population', name: '人口・世帯', icon: '👨‍👩‍👧‍👦', color: '#3B82F6' },
        { id: 'economy', name: '経済・雇用', icon: '💼', color: '#10B981' },
        { id: 'education', name: '教育・子育て', icon: '🎓', color: '#F59E0B' },
        { id: 'healthcare', name: '医療・福祉', icon: '🏥', color: '#EF4444' },
        { id: 'transportation', name: '交通・アクセス', icon: '🚌', color: '#8B5CF6' },
        { id: 'housing', name: '住環境', icon: '🏠', color: '#06B6D4' },
        { id: 'environment', name: '自然・環境', icon: '🌱', color: '#84CC16' },
        { id: 'culture', name: '文化・レジャー', icon: '🎭', color: '#EC4899' }
      ]
      
      return categories.map(cat => ({
        ...cat,
        score: this.baseCategoryScores[cat.id],
        weight: this.currentWeights[cat.id],
        contribution: ((this.baseCategoryScores[cat.id] * this.currentWeights[cat.id]) / 100).toFixed(1)
      }))
    },
    topStrengths() {
      return this.categoryScores
        .map(cat => ({
          category: cat.name,
          baseScore: cat.score,
          weight: cat.weight,
          weightedScore: cat.contribution
        }))
        .sort((a, b) => parseFloat(b.weightedScore) - parseFloat(a.weightedScore))
        .slice(0, 3)
    },
    topWeaknesses() {
      return this.categoryScores
        .map(cat => ({
          category: cat.name,
          baseScore: cat.score,
          weight: cat.weight,
          weightedScore: cat.contribution
        }))
        .sort((a, b) => parseFloat(a.weightedScore) - parseFloat(b.weightedScore))
        .slice(0, 3)
    }
  },
  methods: {
    handleScoreUpdate(newScore, weights) {
      this.currentTotalScore = newScore
      this.currentWeights = { ...weights }
    },
    handleConfigurationSaved(configName) {
      // 設定保存後の処理
      console.log('Configuration saved:', configName)
    },
    getScoreChange() {
      const diff = this.currentTotalScore - this.previousScore
      if (diff > 0) return `+${diff.toFixed(1)}pt`
      return `${diff.toFixed(1)}pt`
    },
    getScoreGrade(score) {
      if (score >= 90) return 'S (優秀)'
      if (score >= 80) return 'A (良好)'
      if (score >= 70) return 'B (標準)'
      if (score >= 60) return 'C (改善余地)'
      return 'D (要改善)'
    },
    getScoreColor(score) {
      if (score >= 80) return 'text-green-600'
      if (score >= 70) return 'text-blue-600'
      if (score >= 60) return 'text-orange-600'
      return 'text-red-600'
    },
    getRankChangeColor(change) {
      if (change > 0) return 'text-red-600'
      if (change < 0) return 'text-green-600'
      return 'text-gray-600'
    },
    getDistributionGrade() {
      if (this.distributionScore >= 80) return 'バランス良好'
      if (this.distributionScore >= 60) return 'やや偏り'
      return '偏りが大きい'
    },
    getAlignmentGrade() {
      if (this.residentAlignment >= 80) return '高い一致'
      if (this.residentAlignment >= 60) return '中程度の一致'
      return '一致度が低い'
    },
    getSensitivityGrade() {
      if (this.policySensitivity >= 80) return '高感度'
      if (this.policySensitivity >= 60) return '中感度'
      return '低感度'
    }
  }
}
</script>