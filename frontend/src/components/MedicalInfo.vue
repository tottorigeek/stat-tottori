<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
      🏥 医療・健康情報
    </h3>
    
    <!-- 医療機関混雑状況 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">医療機関混雑状況</h4>
      <div class="space-y-3">
        <div v-for="hospital in hospitals" :key="hospital.name" class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div>
            <p class="font-medium text-gray-800">{{ hospital.name }}</p>
            <p class="text-sm text-gray-600">{{ hospital.department }}</p>
          </div>
          <div class="text-right">
            <div class="flex items-center">
              <div :class="getCrowdingColor(hospital.crowding)" class="w-3 h-3 rounded-full mr-2"></div>
              <span class="text-sm font-medium">{{ hospital.crowding }}</span>
            </div>
            <p class="text-xs text-gray-500">{{ hospital.waitTime }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 薬局情報 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">薬局・在庫状況</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div v-for="pharmacy in pharmacies" :key="pharmacy.name" class="p-3 bg-blue-50 rounded border border-blue-200">
          <p class="font-medium text-gray-800 text-sm">{{ pharmacy.name }}</p>
          <div class="flex items-center mt-1">
            <span class="text-xs text-gray-600 mr-2">営業時間:</span>
            <span class="text-xs text-gray-700">{{ pharmacy.hours }}</span>
          </div>
          <div class="flex items-center mt-1">
            <div :class="pharmacy.available ? 'bg-green-400' : 'bg-red-400'" class="w-2 h-2 rounded-full mr-2"></div>
            <span class="text-xs">{{ pharmacy.available ? '営業中' : '営業時間外' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 健康診断・予防接種 -->
    <div>
      <h4 class="text-lg font-semibold text-gray-700 mb-3">健康診断・予防接種</h4>
      <div class="space-y-2">
        <div v-for="service in healthServices" :key="service.name" class="p-3 bg-green-50 rounded border border-green-200">
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-gray-800">{{ service.name }}</span>
            <span :class="service.available ? 'text-green-600' : 'text-red-600'" class="text-xs font-medium">
              {{ service.available ? '予約可能' : '満員' }}
            </span>
          </div>
          <p class="text-xs text-gray-600 mt-1">{{ service.location }} | {{ service.nextDate }}</p>
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
  name: 'MedicalInfo',
  data() {
    return {
      lastUpdated: '',
      hospitals: [
        {
          name: '鳥取県立中央病院',
          department: '内科・外科',
          crowding: '混雑',
          waitTime: '約60分'
        },
        {
          name: '鳥取市立病院',
          department: '総合診療',
          crowding: '普通',
          waitTime: '約30分'
        },
        {
          name: '鳥取赤十字病院',
          department: '救急外来',
          crowding: '空いている',
          waitTime: '約15分'
        },
        {
          name: 'まつだ小児科',
          department: '小児科',
          crowding: '普通',
          waitTime: '約25分'
        }
      ],
      pharmacies: [
        {
          name: 'アイン薬局駅前店',
          hours: '9:00-19:00',
          available: true
        },
        {
          name: 'さくら薬局鳥取店',
          hours: '9:00-18:00',
          available: true
        },
        {
          name: 'コスモ薬局',
          hours: '9:00-17:30',
          available: false
        },
        {
          name: 'みどり薬局',
          hours: '8:30-18:30',
          available: true
        }
      ],
      healthServices: [
        {
          name: '成人健康診断',
          location: '鳥取市保健所',
          nextDate: '1月15日(水)',
          available: true
        },
        {
          name: 'インフルエンザ予防接種',
          location: '各医療機関',
          nextDate: '随時受付中',
          available: true
        },
        {
          name: '子宮がん検診',
          location: '県立中央病院',
          nextDate: '2月3日(月)',
          available: false
        },
        {
          name: '乳幼児健診',
          location: '各市町村保健センター',
          nextDate: '1月20日(月)',
          available: true
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
    }
  }
}
</script>

<style scoped>
/* カスタムスタイルがあれば追加 */
</style>