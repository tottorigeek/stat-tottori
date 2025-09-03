<template>
  <div class="policy-prediction-container">
    <!-- ヘッダー -->
    <div class="bg-white shadow-sm border-b">
      <div class="px-6 py-4">
        <h1 class="text-2xl font-bold text-gray-900">政策効果予測AI</h1>
        <p class="text-gray-600 mt-1">機械学習による政策効果の定量的予測・最適化</p>
      </div>
    </div>

    <div class="p-6 max-w-7xl mx-auto">
      <!-- ナビゲーションタブ -->
      <div class="mb-6">
        <nav class="flex space-x-4">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === tab.key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- 政策シナリオ設定 -->
      <div v-show="activeTab === 'scenario'" class="space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">政策シナリオ設定</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="(policy, key) in policyScenario" :key="key" class="space-y-3">
              <label class="block text-sm font-medium text-gray-700">
                {{ getPolicyLabel(key) }}
              </label>
              <div class="space-y-2">
                <input
                  v-model.number="policyScenario[key]"
                  type="range"
                  :min="0"
                  :max="getPolicyMax(key)"
                  :step="0.1"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div class="flex justify-between text-xs text-gray-500">
                  <span>0</span>
                  <span class="font-medium text-blue-600">{{ policyScenario[key] }}</span>
                  <span>{{ getPolicyMax(key) }}</span>
                </div>
                <p class="text-xs text-gray-500">
                  {{ getPolicyDescription(key) }}
                </p>
              </div>
            </div>
          </div>

          <div class="mt-6 flex space-x-4">
            <button
              @click="runPrediction"
              :disabled="isLoading"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isLoading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                予測実行中...
              </span>
              <span v-else>予測実行</span>
            </button>
            
            <button
              @click="optimizePolicies"
              :disabled="isLoading"
              class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              政策最適化
            </button>
            
            <button
              @click="resetScenario"
              class="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              リセット
            </button>
          </div>
        </div>
      </div>

      <!-- 人口予測結果 -->
      <div v-show="activeTab === 'population'" class="space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">人口動態予測結果</h2>
          
          <div v-if="populationPrediction" class="space-y-4">
            <!-- 予測チャート -->
            <div class="h-96">
              <canvas ref="populationChart"></canvas>
            </div>
            
            <!-- 予測サマリー -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-blue-50 p-4 rounded-lg">
                <h3 class="font-medium text-blue-900">10年後人口予測</h3>
                <p class="text-2xl font-bold text-blue-600">
                  {{ formatNumber(populationPrediction.forecast[populationPrediction.forecast.length - 1]) }}人
                </p>
              </div>
              
              <div class="bg-green-50 p-4 rounded-lg">
                <h3 class="font-medium text-green-900">人口変化率</h3>
                <p class="text-2xl font-bold text-green-600">
                  {{ calculateGrowthRate() }}%
                </p>
              </div>
              
              <div class="bg-purple-50 p-4 rounded-lg">
                <h3 class="font-medium text-purple-900">政策効果</h3>
                <p class="text-2xl font-bold text-purple-600">
                  {{ populationPrediction.policy_effect_factor ? ((populationPrediction.policy_effect_factor - 1) * 100).toFixed(1) : 0 }}%
                </p>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            政策シナリオを設定して予測を実行してください
          </div>
        </div>
      </div>

      <!-- 経済効果予測結果 -->
      <div v-show="activeTab === 'economic'" class="space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">経済効果予測結果</h2>
          
          <div v-if="economicPrediction" class="space-y-6">
            <!-- 主要指標 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="bg-blue-50 p-4 rounded-lg">
                <h3 class="font-medium text-blue-900">GDP影響</h3>
                <p class="text-xl font-bold text-blue-600">
                  {{ formatNumber(economicPrediction.economic_impact.gdp_impact) }}億円
                </p>
              </div>
              
              <div class="bg-green-50 p-4 rounded-lg">
                <h3 class="font-medium text-green-900">雇用創出</h3>
                <p class="text-xl font-bold text-green-600">
                  {{ formatNumber(economicPrediction.economic_impact.employment_impact) }}人
                </p>
              </div>
              
              <div class="bg-yellow-50 p-4 rounded-lg">
                <h3 class="font-medium text-yellow-900">税収増</h3>
                <p class="text-xl font-bold text-yellow-600">
                  {{ formatNumber(economicPrediction.economic_impact.tax_revenue_impact) }}億円
                </p>
              </div>
              
              <div class="bg-purple-50 p-4 rounded-lg">
                <h3 class="font-medium text-purple-900">投資収益率</h3>
                <p class="text-xl font-bold text-purple-600">
                  {{ economicPrediction.roi_analysis.roi_percent.toFixed(1) }}%
                </p>
              </div>
            </div>

            <!-- 時系列チャート -->
            <div class="h-96">
              <canvas ref="economicChart"></canvas>
            </div>
            
            <!-- 産業別内訳 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div v-for="(value, industry) in economicPrediction.industry_breakdown" :key="industry" class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-medium text-gray-700 capitalize">{{ getIndustryLabel(industry) }}</h4>
                <p class="text-lg font-bold text-gray-900">{{ formatNumber(value) }}億円</p>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            政策シナリオを設定して予測を実行してください
          </div>
        </div>
      </div>

      <!-- 政策最適化結果 -->
      <div v-show="activeTab === 'optimization'" class="space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">政策配分最適化結果</h2>
          
          <div v-if="optimizationResult" class="space-y-6">
            <!-- 最適配分 -->
            <div class="space-y-4">
              <h3 class="font-medium">最適政策配分</h3>
              <div class="space-y-2">
                <div v-for="(value, policy) in optimizationResult.optimal_allocation" :key="policy" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span class="font-medium">{{ getPolicyLabel(policy) }}</span>
                  <div class="flex items-center space-x-2">
                    <div class="w-32 bg-gray-200 rounded-full h-2">
                      <div class="bg-blue-600 h-2 rounded-full" :style="{width: (value / getPolicyMax(policy) * 100) + '%'}"></div>
                    </div>
                    <span class="text-sm font-medium w-12 text-right">{{ value.toFixed(1) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 最適化結果サマリー -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-blue-50 p-4 rounded-lg">
                <h4 class="font-medium text-blue-900">総効果</h4>
                <p class="text-xl font-bold text-blue-600">
                  {{ optimizationResult.optimization_results.total_objective_value.toFixed(3) }}
                </p>
              </div>
              
              <div class="bg-green-50 p-4 rounded-lg">
                <h4 class="font-medium text-green-900">予算使用率</h4>
                <p class="text-xl font-bold text-green-600">
                  {{ optimizationResult.optimization_results.budget_utilization.toFixed(1) }}%
                </p>
              </div>
              
              <div class="bg-purple-50 p-4 rounded-lg">
                <h4 class="font-medium text-purple-900">実行可能性</h4>
                <p class="text-xl font-bold text-purple-600">
                  {{ optimizationResult.optimization_results.is_feasible ? '○' : '×' }}
                </p>
              </div>
            </div>

            <!-- 実装スケジュール -->
            <div v-if="optimizationResult.implementation_schedule">
              <h3 class="font-medium mb-3">実装スケジュール</h3>
              <div class="space-y-2">
                <div v-for="(schedule, policy) in optimizationResult.implementation_schedule" :key="policy" class="p-3 bg-gray-50 rounded-lg">
                  <div class="flex justify-between items-start">
                    <div>
                      <span class="font-medium">{{ getPolicyLabel(policy) }}</span>
                      <p class="text-sm text-gray-600">
                        {{ schedule.start_year + 1 }}年目 ～ {{ schedule.end_year + 1 }}年目
                        (年間 {{ formatNumber(schedule.annual_cost) }}億円)
                      </p>
                    </div>
                    <div class="text-right">
                      <span class="text-sm font-medium">効率性: {{ schedule.efficiency.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            政策最適化を実行してください
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'PolicyPrediction',
  data() {
    return {
      activeTab: 'scenario',
      isLoading: false,
      policyScenario: {
        childcare_support: 0,
        migration_support: 0,
        economic_development: 0,
        infrastructure_improvement: 0,
        education_enhancement: 0,
        healthcare_improvement: 0
      },
      populationPrediction: null,
      economicPrediction: null,
      optimizationResult: null,
      tabs: [
        { key: 'scenario', label: 'シナリオ設定' },
        { key: 'population', label: '人口予測' },
        { key: 'economic', label: '経済効果' },
        { key: 'optimization', label: '最適化' }
      ],
      populationChart: null,
      economicChart: null
    }
  },
  methods: {
    getPolicyLabel(key) {
      const labels = {
        childcare_support: '子育て支援',
        migration_support: '移住支援',
        economic_development: '経済活性化',
        infrastructure_improvement: 'インフラ整備',
        education_enhancement: '教育環境改善',
        healthcare_improvement: '医療環境改善'
      }
      return labels[key] || key
    },
    
    getPolicyMax(key) {
      const maxValues = {
        childcare_support: 10,
        migration_support: 8,
        economic_development: 15,
        infrastructure_improvement: 20,
        education_enhancement: 12,
        healthcare_improvement: 10
      }
      return maxValues[key] || 10
    },
    
    getPolicyDescription(key) {
      const descriptions = {
        childcare_support: '保育施設整備・子育て支援制度拡充',
        migration_support: 'UI/Uターン促進・住宅支援',
        economic_development: '企業誘致・起業支援・産業振興',
        infrastructure_improvement: '道路・交通・デジタルインフラ整備',
        education_enhancement: '学校設備・教育プログラム充実',
        healthcare_improvement: '医療施設・介護サービス拡充'
      }
      return descriptions[key] || ''
    },
    
    getIndustryLabel(industry) {
      const labels = {
        agriculture: '農業',
        manufacturing: '製造業',
        services: 'サービス業'
      }
      return labels[industry] || industry
    },
    
    async runPrediction() {
      this.isLoading = true
      
      try {
        // 人口予測
        const populationResponse = await fetch('/api/v1/prediction/population', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model_type: 'ensemble',
            years_ahead: 10,
            policy_scenario: this.policyScenario
          })
        })
        
        if (populationResponse.ok) {
          this.populationPrediction = await populationResponse.json()
          this.$nextTick(() => this.renderPopulationChart())
        }
        
        // 経済効果予測
        const economicResponse = await fetch('/api/v1/prediction/economic-impact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            policy_scenario: this.policyScenario,
            population_change: 0.02,
            years_ahead: 5
          })
        })
        
        if (economicResponse.ok) {
          this.economicPrediction = await economicResponse.json()
          this.$nextTick(() => this.renderEconomicChart())
        }
        
      } catch (error) {
        console.error('予測実行エラー:', error)
        alert('予測実行に失敗しました')
      } finally {
        this.isLoading = false
      }
    },
    
    async optimizePolicies() {
      this.isLoading = true
      
      try {
        const response = await fetch('/api/v1/prediction/policy-optimization', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            objective: 'total_benefit',
            budget_constraint: 100.0,
            optimization_method: 'linear_programming'
          })
        })
        
        if (response.ok) {
          this.optimizationResult = await response.json()
          // 最適化結果を現在のシナリオに反映
          this.policyScenario = { ...this.optimizationResult.optimal_allocation }
        }
        
      } catch (error) {
        console.error('最適化エラー:', error)
        alert('政策最適化に失敗しました')
      } finally {
        this.isLoading = false
      }
    },
    
    resetScenario() {
      Object.keys(this.policyScenario).forEach(key => {
        this.policyScenario[key] = 0
      })
      this.populationPrediction = null
      this.economicPrediction = null
      this.optimizationResult = null
    },
    
    renderPopulationChart() {
      if (!this.populationPrediction || !this.$refs.populationChart) return
      
      if (this.populationChart) {
        this.populationChart.destroy()
      }
      
      const ctx = this.$refs.populationChart.getContext('2d')
      
      this.populationChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.populationPrediction.dates.map(date => new Date(date).getFullYear()),
          datasets: [
            {
              label: '人口予測',
              data: this.populationPrediction.forecast,
              borderColor: 'rgb(59, 130, 246)',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              fill: true,
              tension: 0.4
            },
            {
              label: '信頼区間上限',
              data: this.populationPrediction.confidence_intervals.upper,
              borderColor: 'rgba(59, 130, 246, 0.3)',
              borderDash: [5, 5],
              fill: false
            },
            {
              label: '信頼区間下限',
              data: this.populationPrediction.confidence_intervals.lower,
              borderColor: 'rgba(59, 130, 246, 0.3)',
              borderDash: [5, 5],
              fill: false
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: false,
              title: {
                display: true,
                text: '人口（人）'
              }
            },
            x: {
              title: {
                display: true,
                text: '年'
              }
            }
          }
        }
      })
    },
    
    renderEconomicChart() {
      if (!this.economicPrediction || !this.$refs.economicChart) return
      
      if (this.economicChart) {
        this.economicChart.destroy()
      }
      
      const ctx = this.$refs.economicChart.getContext('2d')
      
      this.economicChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.economicPrediction.years,
          datasets: [
            {
              label: 'GDP影響（億円）',
              data: this.economicPrediction.time_series_projections.gdp_annual,
              backgroundColor: 'rgba(59, 130, 246, 0.8)',
              yAxisID: 'y'
            },
            {
              label: '雇用創出（人）',
              data: this.economicPrediction.time_series_projections.employment_annual,
              backgroundColor: 'rgba(34, 197, 94, 0.8)',
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: 'GDP影響（億円）'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: '雇用創出（人）'
              },
              grid: {
                drawOnChartArea: false,
              },
            },
            x: {
              title: {
                display: true,
                text: '年次'
              }
            }
          }
        }
      })
    },
    
    formatNumber(value) {
      if (typeof value !== 'number') return '0'
      return new Intl.NumberFormat('ja-JP').format(Math.round(value))
    },
    
    calculateGrowthRate() {
      if (!this.populationPrediction || !this.populationPrediction.forecast.length) return '0.0'
      
      const initial = this.populationPrediction.forecast[0]
      const final = this.populationPrediction.forecast[this.populationPrediction.forecast.length - 1]
      const rate = ((final - initial) / initial * 100)
      
      return rate.toFixed(1)
    }
  },
  
  beforeUnmount() {
    if (this.populationChart) {
      this.populationChart.destroy()
    }
    if (this.economicChart) {
      this.economicChart.destroy()
    }
  }
}
</script>

<style scoped>
.policy-prediction-container {
  min-height: 100vh;
  background-color: #f9fafb;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
</style>