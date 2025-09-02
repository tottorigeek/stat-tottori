<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- ヘッダー -->
    <header class="bg-tottori-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">鳥取県住みやすさ創出プロジェクト</h1>
            <p class="text-tottori-100 mt-2">人口増加のための住みやすさ向上施策分析</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-tottori-100">最終更新: {{ currentDate }}</p>
          </div>
        </div>
      </div>
    </header>

    <!-- メインコンテンツ -->
    <main class="container mx-auto px-4 py-8">
      <!-- ダッシュボード概要 -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">人口追跡ダッシュボード</h2>
        <p class="text-gray-600">鳥取県の人口動態と住みやすさ指標を可視化し、施策効果を追跡します</p>
      </div>

      <!-- 主要指標カード -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">総人口</h3>
          <p class="text-3xl font-bold text-blue-600">{{ population.total.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ population.change > 0 ? '+' : '' }}{{ population.change }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">転入者数</h3>
          <p class="text-3xl font-bold text-green-600">{{ population.inflow.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ population.inflowChange > 0 ? '+' : '' }}{{ population.inflowChange }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">転出者数</h3>
          <p class="text-3xl font-bold text-red-600">{{ population.outflow.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-2">前年比: {{ population.outflowChange > 0 ? '+' : '' }}{{ population.outflowChange }}人</p>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">自然増減</h3>
          <p class="text-3xl font-bold text-purple-600">{{ population.naturalChange > 0 ? '+' : '' }}{{ population.naturalChange }}人</p>
          <p class="text-sm text-gray-500 mt-2">出生 - 死亡</p>
        </div>
      </div>

      <!-- 住みやすさ指標 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">住みやすさ指標</h3>
          <div class="space-y-4">
            <div v-for="(score, category) in livabilityScores" :key="category" class="flex items-center justify-between">
              <span class="text-gray-700">{{ category }}</span>
              <div class="flex items-center">
                <div class="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div class="bg-tottori-500 h-2 rounded-full" :style="{ width: score + '%' }"></div>
                </div>
                <span class="text-sm font-semibold text-gray-800">{{ score }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">施策進捗状況</h3>
          <div class="space-y-4">
            <div v-for="(progress, policy) in policyProgress" :key="policy" class="flex items-center justify-between">
              <span class="text-gray-700">{{ policy }}</span>
              <div class="flex items-center">
                <div class="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div class="bg-green-500 h-2 rounded-full" :style="{ width: progress + '%' }"></div>
                </div>
                <span class="text-sm font-semibold text-gray-800">{{ progress }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- アクションボタン -->
      <div class="text-center">
        <button @click="showDetails = !showDetails" class="bg-tottori-600 hover:bg-tottori-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200">
          {{ showDetails ? '詳細を隠す' : '詳細を見る' }}
        </button>
      </div>

      <!-- 詳細情報 -->
      <div v-if="showDetails" class="mt-8 bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">プロジェクト詳細</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">短期目標（3ヶ月以内）</h4>
            <ul class="text-sm text-gray-600 space-y-1">
              <li>• 鳥取県の住みやすさ現状の体系的可視化</li>
              <li>• 住みやすさ指標データベース構築（100+指標）</li>
              <li>• 科学的分析手法の実装・評価指標の確立</li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">中期目標（6ヶ月以内）</h4>
            <ul class="text-sm text-gray-600 space-y-1">
              <li>• 施策優先順位ランキング（Top 20）の策定</li>
              <li>• 各施策の投資対効果（ROI）の定量化</li>
              <li>• 施策効果予測モデルの構築</li>
            </ul>
          </div>
        </div>
      </div>
    </main>

    <!-- フッター -->
    <footer class="bg-gray-800 text-white py-6 mt-12">
      <div class="container mx-auto px-4 text-center">
        <p>&copy; 2024 鳥取県住みやすさ創出プロジェクト. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      currentDate: new Date().toLocaleDateString('ja-JP'),
      showDetails: false,
      population: {
        total: 550000,
        change: -1500,
        inflow: 8500,
        inflowChange: 200,
        outflow: 10000,
        outflowChange: -300,
        naturalChange: -200
      },
      livabilityScores: {
        '基本生活インフラ': 75,
        '生活環境': 85,
        '経済・雇用': 65,
        'コミュニティ・社会関係': 80
      },
      policyProgress: {
        'データ収集・整理': 60,
        '他県事例調査': 40,
        '住民アンケート': 30,
        '分析手法開発': 25,
        '施策優先順位分析': 15
      }
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