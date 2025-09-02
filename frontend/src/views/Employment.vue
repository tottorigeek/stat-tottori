<template>
  <div class="container mx-auto px-4 py-8">
    <!-- ページヘッダー -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">💼 エリア別雇用・求人情報</h1>
      <p class="text-gray-600">鳥取県内の地域別求人・求職状況を分析し、人材マッチングの課題を可視化します</p>
    </div>

    <!-- エリア選択タブ -->
    <div class="mb-8">
      <nav class="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button 
          v-for="area in areas" 
          :key="area.id"
          @click="selectedArea = area.id"
          :class="[
            'flex-1 py-2 px-4 text-sm font-medium rounded-lg transition-all duration-200',
            selectedArea === area.id
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-blue-600 hover:bg-white/50'
          ]"
        >
          <span class="mr-2">{{ area.icon }}</span>
          {{ area.name }}
        </button>
      </nav>
    </div>

    <!-- 選択エリアの主要指標 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">求人倍率</h3>
        <p class="text-3xl font-bold text-blue-600">{{ getAreaData(selectedArea).jobRatio }}倍</p>
        <p class="text-sm text-gray-500 mt-2">県平均: 1.25倍</p>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">新規求人数</h3>
        <p class="text-3xl font-bold text-green-600">{{ getAreaData(selectedArea).newJobs }}件</p>
        <p class="text-sm text-gray-500 mt-2">前月比: {{ getAreaData(selectedArea).jobsChange > 0 ? '+' : '' }}{{ getAreaData(selectedArea).jobsChange }}件</p>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">求職者数</h3>
        <p class="text-3xl font-bold text-purple-600">{{ getAreaData(selectedArea).jobSeekers }}人</p>
        <p class="text-sm text-gray-500 mt-2">前月比: {{ getAreaData(selectedArea).seekersChange > 0 ? '+' : '' }}{{ getAreaData(selectedArea).seekersChange }}人</p>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">マッチング率</h3>
        <p class="text-3xl font-bold text-orange-600">{{ getAreaData(selectedArea).matchingRate }}%</p>
        <p class="text-sm text-gray-500 mt-2">県平均: 58%</p>
      </div>
    </div>

    <!-- メインコンテンツエリア -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
      <!-- エリア別求人情報 -->
      <div class="lg:col-span-2">
        <AreaJobListings :area="selectedArea" :jobs="getAreaJobs(selectedArea)" />
      </div>

      <!-- 求職者スキル分析 -->
      <div>
        <JobSeekerAnalysis :area="selectedArea" :data="getJobSeekerData(selectedArea)" />
      </div>
    </div>

    <!-- エリア間人材マッチング分析 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- スキルギャップ分析 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">{{ getAreaName(selectedArea) }}のスキルギャップ分析</h3>
        <div class="space-y-4">
          <div v-for="skill in getSkillGaps(selectedArea)" :key="skill.name" class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-800">{{ skill.name }}</p>
              <p class="text-sm text-gray-600">需要: {{ skill.demand }}件 | 供給: {{ skill.supply }}人</p>
            </div>
            <div class="text-right">
              <span :class="getGapColor(skill.gap)" class="px-2 py-1 text-xs font-semibold rounded">
                {{ skill.gap > 0 ? '不足' : '過剰' }} {{ Math.abs(skill.gap) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 他エリアとのマッチング可能性 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">他エリアとのマッチング可能性</h3>
        <div class="space-y-3">
          <div v-for="match in getCrossAreaMatches(selectedArea)" :key="match.area" class="p-3 bg-gray-50 rounded">
            <div class="flex justify-between items-center">
              <span class="font-medium text-gray-800">{{ match.area }}</span>
              <span class="text-lg font-bold text-blue-600">{{ match.matches }}件</span>
            </div>
            <p class="text-sm text-gray-600 mt-1">{{ match.topSkill }}の需要が高い</p>
            <p class="text-xs text-gray-500 mt-1">平均通勤時間: {{ match.commuteTime }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 産業分析セクション -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-8">
      <h3 class="text-xl font-bold text-gray-800 mb-4">産業別分析</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="(industry, index) in industries" :key="index" class="text-center p-4 bg-gray-50 rounded-lg">
          <div class="text-2xl mb-2">{{ industry.icon }}</div>
          <h4 class="text-lg font-semibold text-gray-700 mb-2">{{ industry.name }}</h4>
          <p class="text-2xl font-bold text-blue-600">{{ industry.workers.toLocaleString() }}人</p>
          <p class="text-sm text-gray-500 mt-1">就業者数</p>
          <div class="mt-3">
            <p class="text-sm text-gray-600">成長率: 
              <span :class="industry.growth >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium">
                {{ industry.growth > 0 ? '+' : '' }}{{ industry.growth }}%
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 求人検索・マッチング機能の案内 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h3 class="text-xl font-bold text-blue-800 mb-2">🔍 求人検索・マッチング機能</h3>
      <p class="text-blue-700 mb-4">あなたに最適な求人情報を見つけるためのツールを準備中です。</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 class="font-semibold text-blue-800 mb-2">予定機能</h4>
          <ul class="text-sm text-blue-700 space-y-1">
            <li>• 職種・エリア別詳細検索</li>
            <li>• 給与シミュレーター</li>
            <li>• スキルマッチング機能</li>
            <li>• 企業情報詳細表示</li>
          </ul>
        </div>
        <div>
          <h4 class="font-semibold text-blue-800 mb-2">現在利用可能</h4>
          <div class="space-y-2">
            <a href="#" class="block text-blue-600 hover:text-blue-800 underline text-sm">ハローワーク鳥取</a>
            <a href="#" class="block text-blue-600 hover:text-blue-800 underline text-sm">とっとり就活応援団</a>
            <a href="#" class="block text-blue-600 hover:text-blue-800 underline text-sm">UIJターン支援センター</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AreaJobListings from '@/components/AreaJobListings.vue'
import JobSeekerAnalysis from '@/components/JobSeekerAnalysis.vue'

export default {
  name: 'Employment',
  components: {
    AreaJobListings,
    JobSeekerAnalysis
  },
  data() {
    return {
      selectedArea: 'east',
      areas: [
        { id: 'all', name: '全県', icon: '🗾' },
        { id: 'east', name: '東部（鳥取市周辺）', icon: '🏙️' },
        { id: 'central', name: '中部（倉吉市周辺）', icon: '🏘️' },
        { id: 'west', name: '西部（米子市周辺）', icon: '🏞️' }
      ],
      areaData: {
        all: { jobRatio: 1.25, newJobs: 1245, jobsChange: 89, jobSeekers: 995, seekersChange: -23, matchingRate: 58 },
        east: { jobRatio: 1.45, newJobs: 680, jobsChange: 52, jobSeekers: 470, seekersChange: -15, matchingRate: 68 },
        central: { jobRatio: 0.89, newJobs: 245, jobsChange: 18, jobSeekers: 275, seekersChange: 8, matchingRate: 45 },
        west: { jobRatio: 1.12, newJobs: 320, jobsChange: 19, jobSeekers: 286, seekersChange: -16, matchingRate: 52 }
      },
      supportPrograms: [
        {
          name: 'UIJターン起業支援補助金',
          type: '起業支援',
          description: 'Uターン・Iターン・Jターンによる起業を支援',
          amount: '最大200万円',
          deadline: '2025年3月31日'
        },
        {
          name: '職業訓練受講給付金',
          type: 'スキルアップ',
          description: '職業訓練受講中の生活費を支援',
          amount: '月額10万円',
          deadline: '随時受付'
        },
        {
          name: '事業承継支援補助金',
          type: '事業承継',
          description: '事業承継に伴う設備投資等を支援',
          amount: '最大500万円',
          deadline: '2025年2月28日'
        },
        {
          name: '若者就職応援奨励金',
          type: '就職支援',
          description: '35歳未満の県内就職者への奨励金',
          amount: '10万円',
          deadline: '随時受付'
        }
      ],
      industries: [
        { name: '農業・林業', icon: '🌾', workers: 15420, growth: -2.3 },
        { name: '漁業', icon: '🎣', workers: 3280, growth: -1.8 },
        { name: '製造業', icon: '🏭', workers: 45680, growth: 1.2 },
        { name: '建設業', icon: '🏗️', workers: 28950, growth: 0.8 },
        { name: 'サービス業', icon: '🏪', workers: 67230, growth: 2.1 },
        { name: '医療・福祉', icon: '🏥', workers: 38470, growth: 3.5 }
      ],
      skillGaps: {
        east: [
          { name: 'IT・プログラミング', demand: 145, supply: 78, gap: 67 },
          { name: '営業・販売', demand: 89, supply: 120, gap: -31 },
          { name: '製造技術', demand: 156, supply: 145, gap: 11 },
          { name: '医療・介護', demand: 234, supply: 198, gap: 36 }
        ],
        central: [
          { name: '農業技術', demand: 45, supply: 23, gap: 22 },
          { name: '観光・サービス', demand: 67, supply: 89, gap: -22 },
          { name: '製造・技術', demand: 78, supply: 65, gap: 13 },
          { name: '事務・管理', demand: 34, supply: 45, gap: -11 }
        ],
        west: [
          { name: '医療・福祉', demand: 123, supply: 89, gap: 34 },
          { name: '物流・運送', demand: 67, supply: 45, gap: 22 },
          { name: '製造業', demand: 89, supply: 98, gap: -9 },
          { name: 'サービス業', demand: 78, supply: 92, gap: -14 }
        ]
      },
      crossAreaMatches: {
        east: [
          { area: '中部エリア', matches: 23, topSkill: 'IT技術', commuteTime: '45分' },
          { area: '西部エリア', matches: 18, topSkill: '製造技術', commuteTime: '90分' }
        ],
        central: [
          { area: '東部エリア', matches: 31, topSkill: '農業技術', commuteTime: '45分' },
          { area: '西部エリア', matches: 12, topSkill: '観光サービス', commuteTime: '60分' }
        ],
        west: [
          { area: '東部エリア', matches: 27, topSkill: '医療技術', commuteTime: '90分' },
          { area: '中部エリア', matches: 15, topSkill: '物流管理', commuteTime: '60分' }
        ]
      }
    }
  },
  methods: {
    getAreaData(areaId) {
      return this.areaData[areaId] || this.areaData.all
    },
    getAreaName(areaId) {
      const area = this.areas.find(a => a.id === areaId)
      return area ? area.name : '全県'
    },
    getAreaJobs(areaId) {
      return []
    },
    getJobSeekerData(areaId) {
      return {}
    },
    getSkillGaps(areaId) {
      return this.skillGaps[areaId] || []
    },
    getCrossAreaMatches(areaId) {
      return this.crossAreaMatches[areaId] || []
    },
    getGapColor(gap) {
      if (gap > 30) return 'bg-red-100 text-red-800'
      if (gap > 10) return 'bg-orange-100 text-orange-800'
      if (gap > -10) return 'bg-yellow-100 text-yellow-800'
      return 'bg-blue-100 text-blue-800'
    }
  }
}
</script>