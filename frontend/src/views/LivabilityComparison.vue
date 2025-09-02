<template>
  <div class="min-h-screen bg-gray-50">
    <!-- ヘッダー -->
    <header class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">🏠 住みやすさ比較</h1>
            <p class="text-blue-100 mt-2">すたっととっとり - 鳥取県と他地域の住みやすさを比較分析</p>
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
      <!-- 地域選択セクション -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">比較地域の選択</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="region in availableRegions" :key="region.id" class="flex items-center">
            <input 
              :id="region.id" 
              type="checkbox" 
              :value="region.id" 
              v-model="selectedRegions"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            >
            <label :for="region.id" class="ml-2 text-sm font-medium text-gray-700 cursor-pointer">
              {{ region.name }}
            </label>
          </div>
        </div>
        <div class="mt-4">
          <button @click="updateComparison" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
            比較を更新
          </button>
        </div>
      </div>

      <!-- 住みやすさ評価指標の説明 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">住みやすさ評価指標</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="(indicator, key) in livabilityIndicators" :key="key" class="border-l-4 border-blue-500 pl-4">
            <h4 class="font-semibold text-gray-800">{{ indicator.name }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ indicator.description }}</p>
            <p class="text-xs text-gray-500 mt-2">重み: {{ indicator.weight }}%</p>
          </div>
        </div>
      </div>

      <!-- 総合住みやすさスコア比較 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">総合住みやすさスコア比較</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">地域</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">総合スコア</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ランキング</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">前年比</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">詳細</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(score, index) in sortedScores" :key="score.region" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span class="text-sm font-medium text-blue-800">{{ score.region.charAt(0) }}</span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ score.region }}</div>
                      <div class="text-sm text-gray-500">{{ score.prefecture }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-24 bg-gray-200 rounded-full h-2 mr-3">
                      <div class="bg-blue-500 h-2 rounded-full" :style="{ width: score.totalScore + '%' }"></div>
                    </div>
                    <span class="text-sm font-semibold text-gray-800">{{ score.totalScore.toFixed(1) }}点</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                        :class="getRankingClass(index + 1)">
                    {{ index + 1 }}位
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm" :class="score.yearChange >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ score.yearChange > 0 ? '+' : '' }}{{ score.yearChange.toFixed(1) }}点
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <button @click="showDetail(score.region)" class="text-blue-600 hover:text-blue-800">
                    詳細を見る
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 指標別比較グラフ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">基本生活インフラ比較</h3>
          <div class="space-y-3">
            <div v-for="region in selectedRegions" :key="region" class="flex items-center justify-between">
              <span class="text-sm text-gray-700">{{ getRegionName(region) }}</span>
              <div class="flex items-center">
                <div class="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div class="bg-green-500 h-2 rounded-full" :style="{ width: getRegionScore(region, 'infrastructure') + '%' }"></div>
                </div>
                <span class="text-sm font-semibold text-gray-800">{{ getRegionScore(region, 'infrastructure') }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">生活環境比較</h3>
          <div class="space-y-3">
            <div v-for="region in selectedRegions" :key="region" class="flex items-center justify-between">
              <span class="text-sm text-gray-700">{{ getRegionName(region) }}</span>
              <div class="flex items-center">
                <div class="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div class="bg-blue-500 h-2 rounded-full" :style="{ width: getRegionScore(region, 'environment') + '%' }"></div>
                </div>
                <span class="text-sm font-semibold text-gray-800">{{ getRegionScore(region, 'environment') }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 詳細分析セクション -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">詳細分析</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-semibold text-gray-700 mb-3">鳥取県の強み</h4>
            <ul class="text-sm text-gray-600 space-y-2">
              <li v-for="strength in tottoriStrengths" :key="strength" class="flex items-start">
                <span class="text-green-500 mr-2">✓</span>
                {{ strength }}
              </li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold text-gray-700 mb-3">改善が必要な分野</h4>
            <ul class="text-sm text-gray-600 space-y-2">
              <li v-for="improvement in tottoriImprovements" :key="improvement" class="flex items-start">
                <span class="text-orange-500 mr-2">⚠</span>
                {{ improvement }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- アクションプラン提案 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">住みやすさ向上のためのアクションプラン</h3>
        <div class="space-y-4">
          <div v-for="(plan, index) in actionPlans" :key="index" class="border-l-4 border-blue-500 pl-4">
            <h4 class="font-semibold text-gray-800">{{ plan.title }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ plan.description }}</p>
            <div class="mt-2">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                優先度: {{ plan.priority }}
              </span>
              <span class="ml-2 text-xs text-gray-500">予想効果: {{ plan.expectedEffect }}</span>
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
import CommonNavigation from '../components/CommonNavigation.vue'

export default {
  name: 'LivabilityComparison',
  components: {
    CommonNavigation
  },
  data() {
    return {
      lastUpdated: '',
      selectedRegions: ['tottori', 'shimane', 'okayama'],
      availableRegions: [
        { id: 'tottori', name: '鳥取県', prefecture: '鳥取県' },
        { id: 'shimane', name: '島根県', prefecture: '島根県' },
        { id: 'okayama', name: '岡山県', prefecture: '岡山県' },
        { id: 'hyogo', name: '兵庫県', prefecture: '兵庫県' },
        { id: 'kyoto', name: '京都府', prefecture: '京都府' },
        { id: 'osaka', name: '大阪府', prefecture: '大阪府' },
        { id: 'nara', name: '奈良県', prefecture: '奈良県' },
        { id: 'wakayama', name: '和歌山県', prefecture: '和歌山県' }
      ],
      livabilityIndicators: {
        infrastructure: {
          name: '基本生活インフラ',
          description: '医療・教育・交通・通信インフラの充実度',
          weight: 25
        },
        environment: {
          name: '生活環境',
          description: '自然環境・安全性・清潔さ・静けさ',
          weight: 20
        },
        economy: {
          name: '経済・雇用',
          description: '就業機会・所得水準・物価・経済安定性',
          weight: 25
        },
        community: {
          name: 'コミュニティ・社会関係',
          description: '地域コミュニティ・社会参加・文化・レジャー',
          weight: 15
        },
        accessibility: {
          name: 'アクセシビリティ',
          description: '都市部へのアクセス・移動の利便性',
          weight: 15
        }
      },
      regionScores: {
        tottori: {
          region: '鳥取県',
          prefecture: '鳥取県',
          totalScore: 72.5,
          yearChange: 1.2,
          scores: {
            infrastructure: 75,
            environment: 85,
            economy: 65,
            community: 70,
            accessibility: 70
          }
        },
        shimane: {
          region: '島根県',
          prefecture: '島根県',
          totalScore: 74.8,
          yearChange: 0.8,
          scores: {
            infrastructure: 78,
            environment: 88,
            economy: 68,
            community: 75,
            accessibility: 68
          }
        },
        okayama: {
          region: '岡山県',
          prefecture: '岡山県',
          totalScore: 78.2,
          yearChange: 1.5,
          scores: {
            infrastructure: 82,
            environment: 80,
            economy: 78,
            community: 78,
            accessibility: 75
          }
        },
        hyogo: {
          region: '兵庫県',
          prefecture: '兵庫県',
          totalScore: 76.5,
          yearChange: 0.9,
          scores: {
            infrastructure: 80,
            environment: 75,
            economy: 80,
            community: 75,
            accessibility: 75
          }
        },
        kyoto: {
          region: '京都府',
          prefecture: '京都府',
          totalScore: 79.8,
          yearChange: 1.1,
          scores: {
            infrastructure: 85,
            environment: 82,
            economy: 78,
            community: 82,
            accessibility: 78
          }
        },
        osaka: {
          region: '大阪府',
          prefecture: '大阪府',
          totalScore: 75.2,
          yearChange: 0.7,
          scores: {
            infrastructure: 88,
            environment: 65,
            economy: 85,
            community: 70,
            accessibility: 85
          }
        },
        nara: {
          region: '奈良県',
          prefecture: '奈良県',
          totalScore: 77.5,
          yearChange: 1.3,
          scores: {
            infrastructure: 78,
            environment: 85,
            economy: 75,
            community: 80,
            accessibility: 72
          }
        },
        wakayama: {
          region: '和歌山県',
          prefecture: '和歌山県',
          totalScore: 73.8,
          yearChange: 0.6,
          scores: {
            infrastructure: 72,
            environment: 88,
            economy: 68,
            community: 75,
            accessibility: 68
          }
        }
      },
      tottoriStrengths: [
        '豊かな自然環境と美しい景観',
        '安全で安心な生活環境',
        '医療・福祉サービスの充実',
        '地域コミュニティの強さ',
        '物価の安さと生活コストの低さ'
      ],
      tottoriImprovements: [
        '就業機会の拡大と所得向上',
        '交通アクセスの改善',
        '教育・文化施設の充実',
        '若年層の定住促進',
        'IT・デジタル化の推進'
      ],
      actionPlans: [
        {
          title: '地域産業の活性化',
          description: '観光・農業・製造業の連携による新産業創出と雇用創出',
          priority: '高',
          expectedEffect: '就業率向上、所得増加'
        },
        {
          title: '交通インフラの整備',
          description: '高速道路・鉄道・空港の利便性向上と地域間連携強化',
          priority: '高',
          expectedEffect: 'アクセシビリティ向上、交流促進'
        },
        {
          title: '教育・文化環境の充実',
          description: '大学・専門学校の誘致、文化施設の整備、生涯学習の推進',
          priority: '中',
          expectedEffect: '若年層定住、文化レベル向上'
        },
        {
          title: 'デジタル化の推進',
          description: 'スマートシティ化、リモートワーク環境整備、デジタルサービス充実',
          priority: '中',
          expectedEffect: '働き方改革、生活利便性向上'
        }
      ]
    }
  },
  computed: {
    sortedScores() {
      return Object.values(this.regionScores)
        .filter(score => this.selectedRegions.includes(this.getRegionId(score.region)))
        .sort((a, b) => b.totalScore - a.totalScore)
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
    updateComparison() {
      // 比較データの更新処理
      console.log('比較データを更新しました')
    },
    getRegionName(regionId) {
      const region = this.availableRegions.find(r => r.id === regionId)
      return region ? region.name : regionId
    },
    getRegionId(regionName) {
      const region = this.availableRegions.find(r => r.name === regionName)
      return region ? region.id : regionName
    },
    getRegionScore(regionId, indicator) {
      const region = this.regionScores[regionId]
      return region ? region.scores[indicator] : 0
    },
    getRankingClass(rank) {
      if (rank === 1) return 'bg-yellow-100 text-yellow-800'
      if (rank === 2) return 'bg-gray-100 text-gray-800'
      if (rank === 3) return 'bg-orange-100 text-orange-800'
      return 'bg-blue-100 text-blue-800'
    },
    showDetail(regionName) {
      // 詳細表示の処理
      console.log(`${regionName}の詳細を表示します`)
    }
  }
}
</script>
