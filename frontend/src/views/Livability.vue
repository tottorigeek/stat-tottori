<template>
  <div class="container mx-auto px-4 py-8">
    <!-- ページヘッダー -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">🏔️ 住みやすさ分析</h1>
      <p class="text-gray-600">データで見る鳥取県の魅力と住みやすさを分析・可視化しています</p>
    </div>

    <!-- 総合スコア -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-8">
      <h3 class="text-xl font-bold text-gray-800 mb-4">住みやすさ総合スコア</h3>
      <div class="flex items-center justify-center mb-6">
        <div class="relative w-32 h-32">
          <svg class="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="16" fill="transparent" class="stroke-current text-gray-300" stroke-width="3"/>
            <circle cx="18" cy="18" r="16" fill="transparent" class="stroke-current text-blue-600" stroke-width="3"
                    :stroke-dasharray="`${overallScore}, 100`" stroke-linecap="round"/>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-3xl font-bold text-blue-600">{{ overallScore }}</span>
          </div>
        </div>
      </div>
      <p class="text-center text-gray-600 mb-4">全国47都道府県中 <span class="font-bold text-blue-600">12位</span></p>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center">
          <p class="text-sm text-gray-600">物価水準</p>
          <p class="text-lg font-bold text-green-600">A+</p>
        </div>
        <div class="text-center">
          <p class="text-sm text-gray-600">自然環境</p>
          <p class="text-lg font-bold text-green-600">A+</p>
        </div>
        <div class="text-center">
          <p class="text-sm text-gray-600">交通利便性</p>
          <p class="text-lg font-bold text-yellow-600">B</p>
        </div>
        <div class="text-center">
          <p class="text-sm text-gray-600">就業機会</p>
          <p class="text-lg font-bold text-orange-600">C+</p>
        </div>
      </div>
    </div>

    <!-- 詳細指標 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- 生活コスト比較 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">生活コスト比較（全国平均=100）</h3>
        <div class="space-y-4">
          <div v-for="(cost, category) in livingCosts" :key="category" class="flex items-center justify-between">
            <span class="text-gray-700">{{ category }}</span>
            <div class="flex items-center">
              <div class="w-32 bg-gray-200 rounded-full h-2 mr-3">
                <div :class="getCostColor(cost)" class="h-2 rounded-full" :style="{ width: Math.min(cost, 120) + '%' }"></div>
              </div>
              <span class="text-sm font-semibold text-gray-800 w-8">{{ cost }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 環境・安全性指標 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">環境・安全性指標</h3>
        <div class="space-y-4">
          <div v-for="(score, indicator) in safetyIndicators" :key="indicator" class="flex items-center justify-between">
            <span class="text-gray-700">{{ indicator }}</span>
            <div class="flex items-center">
              <div class="w-32 bg-gray-200 rounded-full h-2 mr-3">
                <div class="bg-green-500 h-2 rounded-full" :style="{ width: score + '%' }"></div>
              </div>
              <span class="text-sm font-semibold text-gray-800">{{ score }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 他県比較 -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-8">
      <h3 class="text-xl font-bold text-gray-800 mb-4">類似県との比較</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full table-auto">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">都道府県</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">人口</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">物価</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">住みやすさ</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">転入率</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="prefecture in prefectureComparison" :key="prefecture.name" 
                :class="prefecture.name === '鳥取県' ? 'bg-blue-50' : ''">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="font-medium text-gray-900">{{ prefecture.name }}</span>
                  <span v-if="prefecture.name === '鳥取県'" class="ml-2 px-2 py-1 text-xs bg-blue-500 text-white rounded">当県</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ prefecture.population }}万人</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getPriceColor(prefecture.price)" class="px-2 py-1 text-xs font-semibold rounded">
                  {{ prefecture.price }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ prefecture.livability }}位</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="prefecture.migrationRate > 0 ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ prefecture.migrationRate > 0 ? '+' : '' }}{{ prefecture.migrationRate }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 魅力ポイント -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <div v-for="attraction in attractions" :key="attraction.title" class="bg-white rounded-lg shadow-md p-6">
        <div class="text-3xl mb-3">{{ attraction.icon }}</div>
        <h4 class="text-lg font-bold text-gray-800 mb-2">{{ attraction.title }}</h4>
        <p class="text-gray-600 text-sm mb-3">{{ attraction.description }}</p>
        <div class="space-y-1">
          <div v-for="(data, key) in attraction.data" :key="key" class="flex justify-between text-sm">
            <span class="text-gray-600">{{ key }}:</span>
            <span class="font-medium text-blue-600">{{ data }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ライフステージ別シミュレーター -->
    <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
      <h3 class="text-xl font-bold text-gray-800 mb-4">🎯 ライフステージ別住みやすさ診断</h3>
      <p class="text-gray-600 mb-6">あなたのライフステージに合わせた鳥取県の住みやすさをチェックできます</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="lifestage in lifestages" :key="lifestage.name" class="bg-white rounded-lg p-4 text-center hover:shadow-md transition-shadow duration-200">
          <div class="text-2xl mb-2">{{ lifestage.icon }}</div>
          <h4 class="font-semibold text-gray-800 mb-2">{{ lifestage.name }}</h4>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span>総合:</span>
              <span :class="getScoreColor(lifestage.score)" class="font-bold">{{ lifestage.score }}/5</span>
            </div>
          </div>
          <button class="mt-3 bg-blue-500 hover:bg-blue-600 text-white text-xs px-3 py-1 rounded transition-colors duration-200">
            詳細診断
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Livability',
  data() {
    return {
      overallScore: 78,
      livingCosts: {
        '住居費': 72,
        '食費': 88,
        '交通費': 95,
        '教育費': 89,
        '医療費': 91,
        '光熱費': 105
      },
      safetyIndicators: {
        '治安の良さ': 92,
        '災害リスクの低さ': 88,
        '大気質': 95,
        '水質': 98,
        '騒音レベル': 85
      },
      prefectureComparison: [
        { name: '島根県', population: 67, price: '安い', livability: 8, migrationRate: -0.8 },
        { name: '鳥取県', population: 55, price: '安い', livability: 12, migrationRate: -0.6 },
        { name: '高知県', population: 69, price: '普通', livability: 15, migrationRate: -1.2 },
        { name: '徳島県', population: 73, price: '普通', livability: 18, migrationRate: -1.0 },
        { name: '佐賀県', population: 81, price: '安い', livability: 20, migrationRate: -0.4 }
      ],
      attractions: [
        {
          title: '豊かな自然環境',
          icon: '🏔️',
          description: '鳥取砂丘や大山など、美しい自然に囲まれた環境',
          data: {
            '森林率': '74%',
            '公園面積': '15.2㎡/人',
            '海岸線長': '129km'
          }
        },
        {
          title: '新鮮な食材',
          icon: '🦀',
          description: '松葉ガニ、梨、和牛など豊富で新鮮な地産地消',
          data: {
            '梨生産量': '全国1位',
            '水産物': '年間2.8万t',
            '和牛飼育頭数': '2.1万頭'
          }
        },
        {
          title: 'コンパクトシティ',
          icon: '🏙️',
          description: '短い通勤時間と充実した都市機能',
          data: {
            '平均通勤時間': '23分',
            '渋滞少ない': '全国5位',
            '人口密度': '159人/k㎡'
          }
        },
        {
          title: '子育て環境',
          icon: '👨‍👩‍👧‍👦',
          description: '充実した子育て支援と教育環境',
          data: {
            '待機児童数': '0人',
            '医療費助成': '18歳まで',
            '学級人数': '24.8人'
          }
        },
        {
          title: '温泉・健康',
          icon: '♨️',
          description: '豊富な温泉と健康長寿の地域',
          data: {
            '温泉地数': '15箇所',
            '平均寿命': '男性81.2歳',
            '医師数': '269人/10万人'
          }
        },
        {
          title: 'コミュニティ',
          icon: '🤝',
          description: '地域の結びつきが強く、温かい人間関係',
          data: {
            '犯罪発生率': '全国最少',
            'ボランティア率': '28%',
            '近所付き合い': '良好85%'
          }
        }
      ],
      lifestages: [
        { name: '単身者', icon: '👤', score: 3.8 },
        { name: '新婚・夫婦', icon: '💑', score: 4.2 },
        { name: '子育て世代', icon: '👨‍👩‍👧‍👦', score: 4.5 },
        { name: 'シニア世代', icon: '👵', score: 4.3 }
      ]
    }
  },
  methods: {
    getCostColor(cost) {
      if (cost < 85) return 'bg-green-500'
      if (cost < 100) return 'bg-yellow-500'
      return 'bg-red-500'
    },
    getPriceColor(price) {
      switch(price) {
        case '安い': return 'bg-green-100 text-green-800'
        case '普通': return 'bg-yellow-100 text-yellow-800'
        case '高い': return 'bg-red-100 text-red-800'
        default: return 'bg-gray-100 text-gray-800'
      }
    },
    getScoreColor(score) {
      if (score >= 4.5) return 'text-green-600'
      if (score >= 4.0) return 'text-blue-600'
      if (score >= 3.5) return 'text-yellow-600'
      return 'text-red-600'
    }
  }
}
</script>

<style scoped>
/* カスタムスタイル */
</style>