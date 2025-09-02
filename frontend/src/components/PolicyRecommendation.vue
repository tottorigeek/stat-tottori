<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-xl font-bold text-gray-800 mb-6">💡 政策改善提案</h3>
    
    <!-- 改善提案カテゴリ -->
    <div class="space-y-6">
      <!-- 短期改善提案 -->
      <div class="border-l-4 border-blue-500 pl-4">
        <h4 class="font-semibold text-blue-800 mb-3">🚀 短期改善提案（3ヶ月以内）</h4>
        <div class="space-y-3">
          <div v-for="(proposal, index) in shortTermProposals" :key="index" class="bg-blue-50 rounded-lg p-3">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h5 class="font-medium text-blue-800">{{ proposal.title }}</h5>
                <p class="text-sm text-blue-600 mt-1">{{ proposal.description }}</p>
                <div class="flex items-center mt-2 space-x-4 text-xs text-blue-600">
                  <span>予算: {{ proposal.budget }}万円</span>
                  <span>期間: {{ proposal.duration }}</span>
                  <span>優先度: {{ proposal.priority }}</span>
                </div>
              </div>
              <button class="ml-2 text-blue-600 hover:text-blue-800">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 中期改善提案 -->
      <div class="border-l-4 border-green-500 pl-4">
        <h4 class="font-semibold text-green-800 mb-3">📈 中期改善提案（6ヶ月-1年）</h4>
        <div class="space-y-3">
          <div v-for="(proposal, index) in mediumTermProposals" :key="index" class="bg-green-50 rounded-lg p-3">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h5 class="font-medium text-green-800">{{ proposal.title }}</h5>
                <p class="text-sm text-green-600 mt-1">{{ proposal.description }}</p>
                <div class="flex items-center mt-2 space-x-4 text-xs text-green-600">
                  <span>予算: {{ proposal.budget }}万円</span>
                  <span>期間: {{ proposal.duration }}</span>
                  <span>優先度: {{ proposal.priority }}</span>
                </div>
              </div>
              <button class="ml-2 text-green-600 hover:text-green-800">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 長期改善提案 -->
      <div class="border-l-4 border-purple-500 pl-4">
        <h4 class="font-semibold text-purple-800 mb-3">🎯 長期改善提案（1-3年）</h4>
        <div class="space-y-3">
          <div v-for="(proposal, index) in longTermProposals" :key="index" class="bg-purple-50 rounded-lg p-3">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h5 class="font-medium text-purple-800">{{ proposal.title }}</h5>
                <p class="text-sm text-purple-600 mt-1">{{ proposal.description }}</p>
                <div class="flex items-center mt-2 space-x-4 text-xs text-purple-600">
                  <span>予算: {{ proposal.budget }}万円</span>
                  <span>期間: {{ proposal.duration }}</span>
                  <span>優先度: {{ proposal.priority }}</span>
                </div>
              </div>
              <button class="ml-2 text-purple-600 hover:text-purple-800">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 実装優先度マトリックス -->
    <div class="mt-8">
      <h4 class="font-semibold text-gray-800 mb-4">📊 実装優先度マトリックス</h4>
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="grid grid-cols-3 gap-4 text-center text-sm">
          <div class="text-gray-500">低コスト</div>
          <div class="text-gray-500">中コスト</div>
          <div class="text-gray-500">高コスト</div>
        </div>
        <div class="grid grid-rows-3 gap-2 mt-2">
          <div class="grid grid-cols-3 gap-2">
            <div class="bg-green-100 text-green-800 p-2 rounded text-xs font-medium">即座に実装</div>
            <div class="bg-yellow-100 text-yellow-800 p-2 rounded text-xs font-medium">計画して実装</div>
            <div class="bg-orange-100 text-orange-800 p-2 rounded text-xs font-medium">検討して実装</div>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div class="bg-yellow-100 text-yellow-800 p-2 rounded text-xs font-medium">計画して実装</div>
            <div class="bg-orange-100 text-orange-800 p-2 rounded text-xs font-medium">検討して実装</div>
            <div class="bg-red-100 text-red-800 p-2 rounded text-xs font-medium">慎重に検討</div>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div class="bg-orange-100 text-orange-800 p-2 rounded text-xs font-medium">検討して実装</div>
            <div class="bg-red-100 text-red-800 p-2 rounded text-xs font-medium">慎重に検討</div>
            <div class="bg-gray-100 text-gray-800 p-2 rounded text-xs font-medium">見直し検討</div>
          </div>
        </div>
        <div class="text-center mt-2">
          <span class="text-xs text-gray-500">縦軸: 効果の高さ、横軸: コスト</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PolicyRecommendation',
  data() {
    return {
      shortTermProposals: [
        {
          title: 'KPI測定精度向上',
          description: '現在のKPI測定方法を改善し、より正確なデータ収集を実現',
          budget: 200,
          duration: '2ヶ月',
          priority: '高'
        },
        {
          title: '関係者研修実施',
          description: '政策担当者向けの効果測定と改善手法の研修を実施',
          budget: 150,
          duration: '3ヶ月',
          priority: '中'
        }
      ],
      mediumTermProposals: [
        {
          title: 'データ分析基盤強化',
          description: '政策効果を定量的に分析するためのデータ分析ツールを導入',
          budget: 800,
          duration: '8ヶ月',
          priority: '高'
        },
        {
          title: 'ステークホルダー連携強化',
          description: '民間企業やNPOとの連携体制を構築し、政策効果を最大化',
          budget: 500,
          duration: '1年',
          priority: '中'
        }
      ],
      longTermProposals: [
        {
          title: 'AI活用政策最適化',
          description: '機械学習を活用して政策効果を予測し、最適な政策設計を実現',
          budget: 2000,
          duration: '2年',
          priority: '高'
        },
        {
          title: '地域特性対応システム',
          description: '各地域の特性に応じた政策カスタマイズシステムを構築',
          budget: 1500,
          duration: '2.5年',
          priority: '中'
        }
      ]
    }
  }
}
</script>

<style scoped>
/* 必要に応じてカスタムスタイルを追加 */
</style>
