<template>
  <div class="bg-white rounded-lg shadow-md p-6 border-l-4" :class="getBorderColor()">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center">
        <span class="text-2xl mr-3">{{ icon }}</span>
        <h3 class="text-lg font-bold text-gray-800">{{ title }}</h3>
      </div>
      <span :class="getPriorityColor()" class="px-2 py-1 text-xs font-semibold rounded">
        {{ priority }}
      </span>
    </div>
    
    <div class="space-y-3">
      <!-- 現状値 -->
      <div class="flex justify-between items-center">
        <span class="text-sm text-gray-600">現状</span>
        <span class="font-semibold text-gray-800">{{ metrics.current }}</span>
      </div>
      
      <!-- 傾向 -->
      <div class="flex justify-between items-center">
        <span class="text-sm text-gray-600">傾向</span>
        <span :class="getTrendColor()" class="text-sm font-medium">
          {{ getTrendIcon() }} {{ metrics.trend }}
        </span>
      </div>
      
      <!-- 予測 -->
      <div class="flex justify-between items-center">
        <span class="text-sm text-gray-600">予測</span>
        <span class="text-sm font-medium text-orange-600">{{ metrics.projection }}</span>
      </div>
    </div>

    <!-- 深刻度インジケーター -->
    <div class="mt-4">
      <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
        <span>深刻度</span>
        <span>{{ getSeverityText() }}</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div :class="getSeverityColor()" class="h-2 rounded-full" :style="{ width: getSeverityWidth() + '%' }"></div>
      </div>
    </div>

    <!-- アクションボタン -->
    <div class="mt-4">
      <button @click="$emit('analyze')" class="w-full bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded transition-colors duration-200">
        詳細分析を見る
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SocialIssueCard',
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    metrics: {
      type: Object,
      required: true
    },
    trend: {
      type: String,
      required: true,
      validator: value => ['decreasing', 'increasing', 'stagnant', 'widening', 'improving'].includes(value)
    },
    priority: {
      type: String,
      required: true,
      validator: value => ['高', '中', '低', '最高'].includes(value)
    }
  },
  emits: ['analyze'],
  methods: {
    getBorderColor() {
      switch(this.metrics.severity) {
        case 'critical': return 'border-red-500'
        case 'high': return 'border-orange-500'
        case 'medium': return 'border-yellow-500'
        case 'low': return 'border-green-500'
        default: return 'border-gray-500'
      }
    },
    getPriorityColor() {
      switch(this.priority) {
        case '最高': return 'bg-red-600 text-white'
        case '高': return 'bg-orange-500 text-white'
        case '中': return 'bg-yellow-500 text-white'
        case '低': return 'bg-green-500 text-white'
        default: return 'bg-gray-500 text-white'
      }
    },
    getTrendColor() {
      switch(this.trend) {
        case 'decreasing':
        case 'widening': return 'text-red-600'
        case 'increasing':
        case 'improving': return 'text-green-600'
        case 'stagnant': return 'text-yellow-600'
        default: return 'text-gray-600'
      }
    },
    getTrendIcon() {
      switch(this.trend) {
        case 'decreasing': return '↘️'
        case 'increasing': return '↗️'
        case 'stagnant': return '➡️'
        case 'widening': return '↔️'
        case 'improving': return '⬆️'
        default: return '➡️'
      }
    },
    getSeverityText() {
      switch(this.metrics.severity) {
        case 'critical': return '危機的'
        case 'high': return '深刻'
        case 'medium': return '注意'
        case 'low': return '軽微'
        default: return '不明'
      }
    },
    getSeverityColor() {
      switch(this.metrics.severity) {
        case 'critical': return 'bg-red-500'
        case 'high': return 'bg-orange-500'
        case 'medium': return 'bg-yellow-500'
        case 'low': return 'bg-green-500'
        default: return 'bg-gray-500'
      }
    },
    getSeverityWidth() {
      switch(this.metrics.severity) {
        case 'critical': return 100
        case 'high': return 80
        case 'medium': return 60
        case 'low': return 40
        default: return 20
      }
    }
  }
}
</script>

<style scoped>
/* カスタムスタイル */
</style>