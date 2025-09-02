<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-xl font-bold text-gray-800 mb-4">{{ getAreaName() }}の求職者分析</h3>

    <!-- 求職者統計サマリー -->
    <div class="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
      <div class="text-center">
        <p class="text-sm text-gray-600">求職者数</p>
        <p class="text-lg font-bold text-purple-600">{{ totalJobSeekers }}人</p>
      </div>
      <div class="text-center">
        <p class="text-sm text-gray-600">就職決定率</p>
        <p class="text-lg font-bold text-green-600">{{ jobPlacementRate }}%</p>
      </div>
    </div>

    <!-- 年齢層別分析 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-3">年齢層別求職者</h4>
      <div class="space-y-3">
        <div v-for="age in ageGroups" :key="age.range" class="flex items-center justify-between">
          <span class="text-gray-700">{{ age.range }}</span>
          <div class="flex items-center">
            <div class="w-32 bg-gray-200 rounded-full h-2 mr-3">
              <div class="bg-purple-500 h-2 rounded-full" :style="{ width: (age.count / maxAge * 100) + '%' }"></div>
            </div>
            <span class="text-sm font-semibold text-gray-800 w-16">{{ age.count }}人</span>
          </div>
        </div>
      </div>
    </div>

    <!-- スキル別分析 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-3">保有スキル分析</h4>
      <div class="space-y-2">
        <div v-for="skill in skillDistribution" :key="skill.name" class="flex items-center justify-between p-2 bg-gray-50 rounded">
          <div>
            <span class="text-sm font-medium text-gray-800">{{ skill.name }}</span>
            <span :class="getSkillLevelColor(skill.level)" class="ml-2 px-2 py-1 text-xs rounded">
              {{ skill.level }}
            </span>
          </div>
          <span class="text-sm font-bold text-blue-600">{{ skill.count }}人</span>
        </div>
      </div>
    </div>

    <!-- 希望条件分析 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-3">希望条件</h4>
      <div class="grid grid-cols-2 gap-3">
        <!-- 希望職種 -->
        <div>
          <h5 class="text-sm font-medium text-gray-700 mb-2">希望職種 TOP5</h5>
          <div class="space-y-1">
            <div v-for="(job, index) in topDesiredJobs" :key="job.name" class="flex justify-between text-sm">
              <span class="text-gray-600">{{ index + 1 }}. {{ job.name }}</span>
              <span class="font-medium text-blue-600">{{ job.count }}人</span>
            </div>
          </div>
        </div>

        <!-- 希望給与 -->
        <div>
          <h5 class="text-sm font-medium text-gray-700 mb-2">希望給与分布</h5>
          <div class="space-y-1">
            <div v-for="salary in salaryExpectations" :key="salary.range" class="flex justify-between text-sm">
              <span class="text-gray-600">{{ salary.range }}</span>
              <span class="font-medium text-green-600">{{ salary.percentage }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 就職活動状況 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-3">就職活動状況</h4>
      <div class="grid grid-cols-3 gap-3">
        <div class="text-center p-3 bg-blue-50 rounded">
          <p class="text-sm text-blue-700">活動中</p>
          <p class="text-lg font-bold text-blue-600">{{ activeJobSeekers }}人</p>
        </div>
        <div class="text-center p-3 bg-green-50 rounded">
          <p class="text-sm text-green-700">面接予定</p>
          <p class="text-lg font-bold text-green-600">{{ interviewScheduled }}人</p>
        </div>
        <div class="text-center p-3 bg-orange-50 rounded">
          <p class="text-sm text-orange-700">内定待ち</p>
          <p class="text-lg font-bold text-orange-600">{{ awaitingOffer }}人</p>
        </div>
      </div>
    </div>

    <!-- 課題・ニーズ分析 -->
    <div class="mb-4">
      <h4 class="text-lg font-semibold text-gray-800 mb-3">主な課題・ニーズ</h4>
      <div class="space-y-2">
        <div v-for="issue in mainIssues" :key="issue.name" class="flex items-center justify-between p-3 border rounded" :class="getIssueClass(issue.severity)">
          <div>
            <span class="font-medium text-gray-800">{{ issue.name }}</span>
            <p class="text-sm text-gray-600 mt-1">{{ issue.description }}</p>
          </div>
          <div class="text-right">
            <span :class="getSeverityColor(issue.severity)" class="px-2 py-1 text-xs font-semibold rounded">
              {{ issue.severity }}
            </span>
            <p class="text-sm text-gray-500 mt-1">{{ issue.affected }}人</p>
          </div>
        </div>
      </div>
    </div>

    <!-- データ更新時刻 -->
    <div class="pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500">データ更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'JobSeekerAnalysis',
  props: {
    area: {
      type: String,
      required: true
    },
    data: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      lastUpdated: '',
      // サンプルデータ（実際はpropsから受け取る）
      totalJobSeekers: 470,
      jobPlacementRate: 68,
      ageGroups: [
        { range: '20-29歳', count: 145 },
        { range: '30-39歳', count: 128 },
        { range: '40-49歳', count: 98 },
        { range: '50-59歳', count: 67 },
        { range: '60歳以上', count: 32 }
      ],
      skillDistribution: [
        { name: 'PCスキル', level: '中級', count: 234 },
        { name: '営業経験', level: '初級', count: 189 },
        { name: 'コミュニケーション', level: '上級', count: 312 },
        { name: '専門資格', level: '中級', count: 145 },
        { name: '語学スキル', level: '初級', count: 89 }
      ],
      topDesiredJobs: [
        { name: '事務・管理', count: 98 },
        { name: '営業・販売', count: 76 },
        { name: 'サービス業', count: 65 },
        { name: '製造・技術', count: 54 },
        { name: '医療・介護', count: 43 }
      ],
      salaryExpectations: [
        { range: '20万円未満', percentage: 15 },
        { range: '20-25万円', percentage: 32 },
        { range: '25-30万円', percentage: 28 },
        { range: '30-35万円', percentage: 18 },
        { range: '35万円以上', percentage: 7 }
      ],
      activeJobSeekers: 312,
      interviewScheduled: 45,
      awaitingOffer: 23,
      mainIssues: [
        {
          name: 'スキル不足',
          description: 'IT関連スキルの習得ニーズが高い',
          severity: '高',
          affected: 167
        },
        {
          name: '経験不足',
          description: '実務経験を積む機会の不足',
          severity: '中',
          affected: 134
        },
        {
          name: '情報不足',
          description: '求人情報へのアクセスが限定的',
          severity: '中',
          affected: 98
        },
        {
          name: '通勤距離',
          description: '希望勤務地との距離が問題',
          severity: '低',
          affected: 76
        }
      ]
    }
  },
  computed: {
    maxAge() {
      return Math.max(...this.ageGroups.map(age => age.count))
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
    getSkillLevelColor(level) {
      switch(level) {
        case '上級': return 'bg-green-100 text-green-800'
        case '中級': return 'bg-yellow-100 text-yellow-800'
        case '初級': return 'bg-blue-100 text-blue-800'
        default: return 'bg-gray-100 text-gray-800'
      }
    },
    getIssueClass(severity) {
      switch(severity) {
        case '高': return 'bg-red-50 border-red-200'
        case '中': return 'bg-yellow-50 border-yellow-200'
        case '低': return 'bg-blue-50 border-blue-200'
        default: return 'bg-gray-50 border-gray-200'
      }
    },
    getSeverityColor(severity) {
      switch(severity) {
        case '高': return 'bg-red-500 text-white'
        case '中': return 'bg-yellow-500 text-white'
        case '低': return 'bg-blue-500 text-white'
        default: return 'bg-gray-500 text-white'
      }
    }
  }
}
</script>

<style scoped>
/* カスタムスタイルがあれば追加 */
</style>