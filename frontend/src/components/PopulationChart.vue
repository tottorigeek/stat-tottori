<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-xl font-bold text-gray-800 mb-4">{{ title }}</h3>
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">表示期間</label>
      <select v-model="selectedPeriod" @change="updateChart" class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-tottori-500 focus:border-tottori-500">
        <option value="12">過去12ヶ月</option>
        <option value="24">過去24ヶ月</option>
        <option value="36">過去36ヶ月</option>
      </select>
    </div>
    <canvas ref="chartCanvas" class="w-full h-64"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  name: 'PopulationChart',
  props: {
    title: {
      type: String,
      required: true
    },
    data: {
      type: Object,
      required: true
    },
    type: {
      type: String,
      default: 'line' // 'line', 'bar', 'pie'
    }
  },
  data() {
    return {
      selectedPeriod: '12',
      chart: null
    }
  },
  mounted() {
    this.createChart()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy()
    }
  },
  methods: {
    createChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d')
      
      this.chart = new Chart(ctx, {
        type: this.type,
        data: this.getChartData(),
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: true,
              text: this.title
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: '人口数'
              }
            },
            x: {
              title: {
                display: true,
                text: '月'
              }
            }
          }
        }
      })
    },
    getChartData() {
      const months = this.getMonths()
      const datasets = []
      
      if (this.type === 'line' || this.type === 'bar') {
        // 年齢別データの場合
        if (this.data.ageGroups) {
          Object.keys(this.data.ageGroups).forEach(ageGroup => {
            datasets.push({
              label: ageGroup,
              data: months.map(month => this.data.ageGroups[ageGroup][month] || 0),
              borderColor: this.getRandomColor(),
              backgroundColor: this.getRandomColor(0.2),
              tension: 0.1
            })
          })
        }
        // 市区町村別データの場合
        else if (this.data.municipalities) {
          Object.keys(this.data.municipalities).forEach(municipality => {
            datasets.push({
              label: municipality,
              data: months.map(month => this.data.municipalities[municipality][month] || 0),
              borderColor: this.getRandomColor(),
              backgroundColor: this.getRandomColor(0.2),
              tension: 0.1
            })
          })
        }
      }
      
      return {
        labels: months,
        datasets: datasets
      }
    },
    getMonths() {
      const months = []
      const today = new Date()
      const period = parseInt(this.selectedPeriod)
      
      for (let i = period - 1; i >= 0; i--) {
        const date = new Date(today.getFullYear(), today.getMonth() - i, 1)
        months.push(date.toLocaleDateString('ja-JP', { year: 'numeric', month: 'short' }))
      }
      
      return months
    },
    getRandomColor(alpha = 1) {
      const colors = [
        '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
        '#06B6D4', '#F97316', '#84CC16', '#EC4899', '#6366F1'
      ]
      const color = colors[Math.floor(Math.random() * colors.length)]
      return alpha < 1 ? color + Math.floor(alpha * 255).toString(16).padStart(2, '0') : color
    },
    updateChart() {
      if (this.chart) {
        this.chart.data = this.getChartData()
        this.chart.update()
      }
    }
  },
  watch: {
    data: {
      handler() {
        this.updateChart()
      },
      deep: true
    }
  }
}
</script>
