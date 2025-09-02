<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
      🚌 交通・移動情報
    </h3>
    
    <!-- バス運行状況 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">路線バス運行状況</h4>
      <div class="space-y-3">
        <div v-for="bus in busRoutes" :key="bus.route" class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div>
            <p class="font-medium text-gray-800">{{ bus.route }}</p>
            <p class="text-sm text-gray-600">{{ bus.direction }}</p>
          </div>
          <div class="text-right">
            <div class="flex items-center">
              <div :class="getDelayColor(bus.status)" class="w-3 h-3 rounded-full mr-2"></div>
              <span class="text-sm font-medium">{{ bus.status }}</span>
            </div>
            <p class="text-xs text-gray-500">次のバス: {{ bus.nextBus }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- JR運行情報 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">JR山陰本線</h4>
      <div class="space-y-3">
        <div v-for="train in trains" :key="train.direction" class="p-3 bg-blue-50 rounded border border-blue-200">
          <div class="flex justify-between items-center">
            <span class="font-medium text-gray-800">{{ train.direction }}</span>
            <div class="flex items-center">
              <div :class="getTrainStatusColor(train.status)" class="w-3 h-3 rounded-full mr-2"></div>
              <span class="text-sm">{{ train.status }}</span>
            </div>
          </div>
          <p class="text-sm text-gray-600 mt-1">{{ train.message }}</p>
          <p class="text-xs text-gray-500 mt-1">次の電車: {{ train.nextTrain }}</p>
        </div>
      </div>
    </div>

    <!-- 道路交通情報 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">道路交通情報</h4>
      <div class="space-y-2">
        <div v-for="road in roadInfo" :key="road.route" class="p-3 rounded border" :class="getRoadInfoClass(road.type)">
          <div class="flex justify-between items-start">
            <div>
              <span class="font-medium text-gray-800">{{ road.route }}</span>
              <span :class="getRoadTypeColor(road.type)" class="ml-2 px-2 py-1 text-xs rounded">{{ road.type }}</span>
            </div>
            <span class="text-xs text-gray-500">{{ road.time }}</span>
          </div>
          <p class="text-sm text-gray-600 mt-1">{{ road.message }}</p>
        </div>
      </div>
    </div>

    <!-- 災害・天気による影響 -->
    <div v-if="weatherImpacts.length > 0">
      <h4 class="text-lg font-semibold text-gray-700 mb-3">天気・災害による交通影響</h4>
      <div class="space-y-2">
        <div v-for="impact in weatherImpacts" :key="impact.id" class="p-3 bg-yellow-50 rounded border border-yellow-200">
          <div class="flex items-start">
            <span class="text-yellow-600 mr-2">⚠️</span>
            <div>
              <p class="text-sm font-medium text-gray-800">{{ impact.title }}</p>
              <p class="text-sm text-gray-600 mt-1">{{ impact.description }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ impact.affectedArea }}</p>
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
  name: 'TransportInfo',
  data() {
    return {
      lastUpdated: '',
      busRoutes: [
        {
          route: '100系統 鳥取駅〜砂丘線',
          direction: '鳥取砂丘方面',
          status: '正常運行',
          nextBus: '15:45'
        },
        {
          route: '200系統 鳥取駅〜岩美線',
          direction: '岩美町方面',
          status: '5分遅れ',
          nextBus: '15:52'
        },
        {
          route: '300系統 市内循環線',
          direction: '市役所経由',
          status: '正常運行',
          nextBus: '15:38'
        },
        {
          route: '400系統 鳥取駅〜河原線',
          direction: '河原町方面',
          status: '正常運行',
          nextBus: '16:05'
        }
      ],
      trains: [
        {
          direction: '鳥取→米子方面',
          status: '正常運行',
          message: '定刻通り運行しています',
          nextTrain: '15:42'
        },
        {
          direction: '鳥取→京都方面',
          status: '10分遅れ',
          message: '強風の影響により遅れが発生しています',
          nextTrain: '15:58'
        }
      ],
      roadInfo: [
        {
          route: '国道9号線',
          type: '工事',
          message: '鳥取市内で舗装工事のため片側通行中（〜17:00）',
          time: '14:30'
        },
        {
          route: '国道53号線',
          type: '渋滞',
          message: '津ノ井バイパス付近で渋滞が発生中',
          time: '15:15'
        },
        {
          route: '県道31号線',
          type: '通行止',
          message: '落石により通行止め。迂回路をご利用ください',
          time: '13:45'
        }
      ],
      weatherImpacts: [
        {
          id: 1,
          title: '強風による交通影響',
          description: 'JR山陰本線で一部区間の運転を見合わせ',
          affectedArea: '鳥取〜倉吉間'
        }
      ]
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 180000) // 3分ごとに更新
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.lastUpdated = now.toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getDelayColor(status) {
      if (status.includes('遅れ')) return 'bg-red-500'
      if (status === '正常運行') return 'bg-green-500'
      return 'bg-yellow-500'
    },
    getTrainStatusColor(status) {
      if (status.includes('遅れ')) return 'bg-red-500'
      if (status === '正常運行') return 'bg-green-500'
      return 'bg-yellow-500'
    },
    getRoadInfoClass(type) {
      switch(type) {
        case '工事': return 'bg-yellow-50 border-yellow-200'
        case '渋滞': return 'bg-orange-50 border-orange-200'
        case '通行止': return 'bg-red-50 border-red-200'
        default: return 'bg-gray-50 border-gray-200'
      }
    },
    getRoadTypeColor(type) {
      switch(type) {
        case '工事': return 'bg-yellow-500 text-white'
        case '渋滞': return 'bg-orange-500 text-white'
        case '通行止': return 'bg-red-500 text-white'
        default: return 'bg-gray-500 text-white'
      }
    }
  }
}
</script>

<style scoped>
/* カスタムスタイルがあれば追加 */
</style>