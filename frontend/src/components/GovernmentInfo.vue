<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
      🏛️ 行政サービス情報
    </h3>
    
    <!-- 役所窓口混雑状況 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">役所窓口混雑状況</h4>
      <div class="space-y-3">
        <div v-for="office in offices" :key="office.name" class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div>
            <p class="font-medium text-gray-800">{{ office.name }}</p>
            <p class="text-sm text-gray-600">{{ office.department }}</p>
          </div>
          <div class="text-right">
            <div class="flex items-center">
              <div :class="getCrowdingColor(office.crowding)" class="w-3 h-3 rounded-full mr-2"></div>
              <span class="text-sm font-medium">{{ office.crowding }}</span>
            </div>
            <p class="text-xs text-gray-500">待ち時間: {{ office.waitTime }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 公共施設利用状況 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">公共施設利用状況</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div v-for="facility in facilities" :key="facility.name" class="p-3 bg-blue-50 rounded border border-blue-200">
          <div class="flex justify-between items-center">
            <span class="font-medium text-gray-800 text-sm">{{ facility.name }}</span>
            <div class="flex items-center">
              <div :class="facility.open ? 'bg-green-400' : 'bg-red-400'" class="w-2 h-2 rounded-full mr-2"></div>
              <span class="text-xs">{{ facility.open ? '開館中' : '閉館中' }}</span>
            </div>
          </div>
          <p class="text-xs text-gray-600 mt-1">{{ facility.hours }}</p>
          <div class="flex justify-between items-center mt-2">
            <span class="text-xs text-gray-600">混雑度:</span>
            <div class="flex items-center">
              <div class="w-16 bg-gray-200 rounded-full h-1 mr-2">
                <div :class="getCrowdingBarColor(facility.crowdingLevel)" class="h-1 rounded-full" :style="{ width: facility.crowdingLevel + '%' }"></div>
              </div>
              <span class="text-xs">{{ facility.crowdingLevel }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- オンライン手続き -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">オンライン手続き対応状況</h4>
      <div class="space-y-2">
        <div v-for="procedure in onlineProcedures" :key="procedure.name" class="p-3 rounded border" :class="getProcedureClass(procedure.status)">
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-gray-800">{{ procedure.name }}</span>
            <span :class="getProcedureStatusColor(procedure.status)" class="px-2 py-1 text-xs rounded">
              {{ procedure.status }}
            </span>
          </div>
          <p class="text-xs text-gray-600 mt-1">{{ procedure.description }}</p>
          <div v-if="procedure.link" class="mt-2">
            <a href="#" class="text-xs text-blue-600 hover:text-blue-800 underline">{{ procedure.link }}</a>
          </div>
        </div>
      </div>
    </div>

    <!-- 緊急情報・お知らせ -->
    <div v-if="announcements.length > 0">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">お知らせ・緊急情報</h4>
      <div class="space-y-2">
        <div v-for="announcement in announcements" :key="announcement.id" class="p-3 rounded border" :class="getAnnouncementClass(announcement.priority)">
          <div class="flex items-start">
            <span :class="getAnnouncementIcon(announcement.priority)" class="mr-2 mt-0.5">
              {{ getAnnouncementIconText(announcement.priority) }}
            </span>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-800">{{ announcement.title }}</p>
              <p class="text-sm text-gray-600 mt-1">{{ announcement.content }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ announcement.date }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 更新時刻 -->
    <div class="mt-4 pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500">最終更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GovernmentInfo',
  data() {
    return {
      lastUpdated: '',
      offices: [
        {
          name: '鳥取市役所本庁舎',
          department: '市民課・税務課',
          crowding: '普通',
          waitTime: '約20分'
        },
        {
          name: '鳥取市役所駅南庁舎',
          department: '福祉課・健康課',
          crowding: '空いている',
          waitTime: '約10分'
        },
        {
          name: '鳥取県庁',
          department: '県民課・生活環境課',
          crowding: '混雑',
          waitTime: '約45分'
        },
        {
          name: '東部県民局',
          department: '各種証明書発行',
          crowding: '普通',
          waitTime: '約15分'
        }
      ],
      facilities: [
        {
          name: '中央図書館',
          hours: '9:00-20:00',
          open: true,
          crowdingLevel: 65
        },
        {
          name: '市民体育館',
          hours: '9:00-21:00',
          open: true,
          crowdingLevel: 80
        },
        {
          name: '文化センター',
          hours: '9:00-22:00',
          open: true,
          crowdingLevel: 30
        },
        {
          name: '中央公民館',
          hours: '9:00-17:00',
          open: false,
          crowdingLevel: 0
        }
      ],
      onlineProcedures: [
        {
          name: '住民票の写し交付申請',
          status: 'オンライン可',
          description: 'マイナポータルから24時間申請可能',
          link: 'マイナポータルへ'
        },
        {
          name: '印鑑登録証明書交付申請',
          status: 'オンライン可',
          description: 'コンビニ交付サービス利用可能',
          link: 'サービス案内を見る'
        },
        {
          name: '転入・転出届',
          status: '一部オンライン可',
          description: '転出届のみオンライン対応',
          link: 'オンライン転出届へ'
        },
        {
          name: '戸籍謄本・抄本交付申請',
          status: '窓口のみ',
          description: '窓口または郵送での手続きが必要',
          link: ''
        },
        {
          name: '各種税証明書交付申請',
          status: 'オンライン可',
          description: 'eLTAXポータルから申請可能',
          link: 'eLTAXへ'
        }
      ],
      announcements: [
        {
          id: 1,
          title: 'マイナンバーカード休日交付',
          content: '1月12日(日)にマイナンバーカードの休日交付を実施します',
          date: '2025-01-02',
          priority: 'info'
        },
        {
          id: 2,
          title: '市役所本庁舎システムメンテナンス',
          content: '1月15日(水)17:00-19:00の間、一部手続きが停止します',
          date: '2025-01-02',
          priority: 'warning'
        }
      ]
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 300000) // 5分ごとに更新
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.lastUpdated = now.toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getCrowdingColor(level) {
      switch(level) {
        case '混雑': return 'bg-red-500'
        case '普通': return 'bg-yellow-500'
        case '空いている': return 'bg-green-500'
        default: return 'bg-gray-500'
      }
    },
    getCrowdingBarColor(level) {
      if (level >= 80) return 'bg-red-500'
      if (level >= 50) return 'bg-yellow-500'
      return 'bg-green-500'
    },
    getProcedureClass(status) {
      switch(status) {
        case 'オンライン可': return 'bg-green-50 border-green-200'
        case '一部オンライン可': return 'bg-yellow-50 border-yellow-200'
        case '窓口のみ': return 'bg-gray-50 border-gray-200'
        default: return 'bg-gray-50 border-gray-200'
      }
    },
    getProcedureStatusColor(status) {
      switch(status) {
        case 'オンライン可': return 'bg-green-500 text-white'
        case '一部オンライン可': return 'bg-yellow-500 text-white'
        case '窓口のみ': return 'bg-gray-500 text-white'
        default: return 'bg-gray-500 text-white'
      }
    },
    getAnnouncementClass(priority) {
      switch(priority) {
        case 'urgent': return 'bg-red-50 border-red-200'
        case 'warning': return 'bg-yellow-50 border-yellow-200'
        case 'info': return 'bg-blue-50 border-blue-200'
        default: return 'bg-gray-50 border-gray-200'
      }
    },
    getAnnouncementIcon(priority) {
      switch(priority) {
        case 'urgent': return 'text-red-600'
        case 'warning': return 'text-yellow-600'
        case 'info': return 'text-blue-600'
        default: return 'text-gray-600'
      }
    },
    getAnnouncementIconText(priority) {
      switch(priority) {
        case 'urgent': return '🚨'
        case 'warning': return '⚠️'
        case 'info': return 'ℹ️'
        default: return '📢'
      }
    }
  }
}
</script>

<style scoped>
/* カスタムスタイルがあれば追加 */
</style>