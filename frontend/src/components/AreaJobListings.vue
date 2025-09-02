<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-xl font-bold text-gray-800">{{ getAreaName() }}の求人情報</h3>
      <select v-model="selectedCategory" class="text-sm border rounded px-3 py-1">
        <option value="">全職種</option>
        <option v-for="category in jobCategories" :key="category" :value="category">
          {{ category }}
        </option>
      </select>
    </div>

    <!-- 求人統計サマリー -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
      <div class="text-center">
        <p class="text-sm text-gray-600">総求人数</p>
        <p class="text-lg font-bold text-blue-600">{{ filteredJobs.length }}件</p>
      </div>
      <div class="text-center">
        <p class="text-sm text-gray-600">平均給与</p>
        <p class="text-lg font-bold text-green-600">{{ averageSalary }}万円</p>
      </div>
      <div class="text-center">
        <p class="text-sm text-gray-600">正社員率</p>
        <p class="text-lg font-bold text-purple-600">{{ fullTimeRate }}%</p>
      </div>
      <div class="text-center">
        <p class="text-sm text-gray-600">新規登録</p>
        <p class="text-lg font-bold text-orange-600">{{ newJobsThisWeek }}件</p>
      </div>
    </div>

    <!-- 職種別求人数 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-3">職種別求人数</h4>
      <div class="space-y-3">
        <div v-for="category in jobCategoryStats" :key="category.name" class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div>
            <p class="font-medium text-gray-800">{{ category.name }}</p>
            <p class="text-sm text-gray-600">平均給与: {{ category.avgSalary }}万円</p>
          </div>
          <div class="text-right">
            <p class="text-lg font-bold text-blue-600">{{ category.count }}件</p>
            <p class="text-xs" :class="category.trend > 0 ? 'text-green-600' : 'text-red-600'">
              {{ category.trend > 0 ? '↗' : '↘' }} {{ Math.abs(category.trend) }}%
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 注目求人 -->
    <div>
      <h4 class="text-lg font-semibold text-gray-800 mb-3">注目の求人</h4>
      <div class="space-y-3 max-h-96 overflow-y-auto">
        <div v-for="job in highlightedJobs" :key="job.id" class="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
          <div class="flex justify-between items-start mb-2">
            <div>
              <h5 class="font-semibold text-gray-800">{{ job.title }}</h5>
              <p class="text-sm text-gray-600">{{ job.company }}</p>
            </div>
            <div class="text-right">
              <span :class="getJobTypeColor(job.type)" class="px-2 py-1 text-xs rounded">{{ job.type }}</span>
              <p class="text-sm font-bold text-blue-600 mt-1">{{ job.salary }}</p>
            </div>
          </div>
          <div class="text-sm text-gray-600 space-y-1">
            <p>📍 {{ job.location }}</p>
            <p>🕒 {{ job.schedule }}</p>
            <div class="flex flex-wrap gap-1 mt-2">
              <span v-for="skill in job.requiredSkills" :key="skill" 
                    class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                {{ skill }}
              </span>
            </div>
          </div>
          <div class="flex justify-between items-center mt-3">
            <span class="text-xs text-gray-500">{{ job.posted }}</span>
            <button class="bg-blue-500 hover:bg-blue-600 text-white text-xs px-3 py-1 rounded transition-colors">
              詳細を見る
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- データ更新時刻 -->
    <div class="mt-4 pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500">データ更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AreaJobListings',
  props: {
    area: {
      type: String,
      required: true
    },
    jobs: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedCategory: '',
      lastUpdated: '',
      jobCategories: [
        'IT・技術', '営業・販売', '事務・管理', '製造・技術',
        '医療・介護', '教育・研究', 'サービス業', '農業・漁業'
      ],
      // サンプルデータ
      sampleJobs: [
        {
          id: 1,
          title: 'Webエンジニア',
          company: '株式会社テックトットリ',
          category: 'IT・技術',
          type: '正社員',
          salary: '月給28～35万円',
          location: '鳥取市',
          schedule: '9:00-18:00',
          requiredSkills: ['Vue.js', 'PHP', 'MySQL'],
          posted: '2025-01-01'
        },
        {
          id: 2,
          title: '介護士',
          company: 'ケアホームさくら',
          category: '医療・介護',
          type: '正社員',
          salary: '月給22～28万円',
          location: '鳥取市',
          schedule: 'シフト制',
          requiredSkills: ['介護福祉士', 'コミュニケーション'],
          posted: '2024-12-28'
        },
        {
          id: 3,
          title: '営業スタッフ',
          company: '鳥取商事株式会社',
          category: '営業・販売',
          type: 'パート',
          salary: '時給1,200～1,500円',
          location: '鳥取市',
          schedule: '10:00-16:00',
          requiredSkills: ['営業経験', '普通自動車免許'],
          posted: '2025-01-02'
        },
        {
          id: 4,
          title: '製造技術者',
          company: '山陰製作所',
          category: '製造・技術',
          type: '正社員',
          salary: '月給25～32万円',
          location: '鳥取市',
          schedule: '8:00-17:00',
          requiredSkills: ['機械操作', '品質管理'],
          posted: '2024-12-30'
        }
      ]
    }
  },
  computed: {
    filteredJobs() {
      if (!this.selectedCategory) return this.sampleJobs
      return this.sampleJobs.filter(job => job.category === this.selectedCategory)
    },
    averageSalary() {
      // 簡易計算（実際はより複雑な処理が必要）
      return 28.5
    },
    fullTimeRate() {
      const fullTimeJobs = this.sampleJobs.filter(job => job.type === '正社員')
      return Math.round((fullTimeJobs.length / this.sampleJobs.length) * 100)
    },
    newJobsThisWeek() {
      return 12
    },
    jobCategoryStats() {
      const stats = {}
      this.sampleJobs.forEach(job => {
        if (!stats[job.category]) {
          stats[job.category] = { count: 0, totalSalary: 0, trend: 0 }
        }
        stats[job.category].count++
        stats[job.category].totalSalary += 28.5 // サンプル値
      })

      return Object.keys(stats).map(category => ({
        name: category,
        count: stats[category].count,
        avgSalary: Math.round(stats[category].totalSalary / stats[category].count),
        trend: Math.floor(Math.random() * 20) - 10 // サンプル値（-10～+10%）
      }))
    },
    highlightedJobs() {
      return this.filteredJobs.slice(0, 5)
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 300000) // 5分ごとに更新
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
    getAreaName() {
      const areaNames = {
        'all': '全県',
        'east': '東部エリア',
        'central': '中部エリア',
        'west': '西部エリア'
      }
      return areaNames[this.area] || '選択エリア'
    },
    getJobTypeColor(type) {
      switch(type) {
        case '正社員': return 'bg-green-100 text-green-800'
        case 'パート': return 'bg-blue-100 text-blue-800'
        case '契約社員': return 'bg-yellow-100 text-yellow-800'
        case 'アルバイト': return 'bg-gray-100 text-gray-800'
        default: return 'bg-gray-100 text-gray-800'
      }
    }
  }
}
</script>

<style scoped>
/* カスタムスタイルがあれば追加 */
</style>