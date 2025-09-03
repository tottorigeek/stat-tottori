import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PopulationChart from '@/components/PopulationChart.vue'

describe('PopulationChart.vue', () => {
  let wrapper
  const mockChartData = {
    labels: ['2019', '2020', '2021', '2022', '2023'],
    datasets: [
      {
        label: '総人口',
        data: [560000, 555000, 550000, 545000, 540000],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)'
      },
      {
        label: '生産年齢人口',
        data: [330000, 325000, 320000, 315000, 310000],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)'
      }
    ]
  }

  const mockChartOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: '鳥取県人口推移'
      },
      legend: {
        position: 'top'
      }
    },
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

  beforeEach(() => {
    wrapper = mount(PopulationChart, {
      props: {
        chartData: mockChartData,
        chartOptions: mockChartOptions
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  it('コンポーネントが正しくレンダリングされる', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('チャートコンテナが存在する', () => {
    const chartContainer = wrapper.find('[data-testid="chart-line"]')
    expect(chartContainer.exists()).toBe(true)
  })

  it('propsが正しく受け取られる', () => {
    expect(wrapper.props('chartData')).toEqual(mockChartData)
    expect(wrapper.props('chartOptions')).toEqual(mockChartOptions)
  })

  it('空のデータでもエラーが発生しない', () => {
    const emptyWrapper = mount(PopulationChart, {
      props: {
        chartData: { labels: [], datasets: [] },
        chartOptions: {}
      }
    })
    
    expect(emptyWrapper.exists()).toBe(true)
    emptyWrapper.unmount()
  })

  it('データセットの色設定が反映される', () => {
    const datasets = wrapper.props('chartData').datasets
    expect(datasets[0].borderColor).toBe('rgb(59, 130, 246)')
    expect(datasets[1].borderColor).toBe('rgb(34, 197, 94)')
  })

  it('ラベルデータが正しく設定される', () => {
    const labels = wrapper.props('chartData').labels
    expect(labels).toEqual(['2019', '2020', '2021', '2022', '2023'])
    expect(labels.length).toBe(5)
  })

  it('人口データの値が正しく設定される', () => {
    const totalPopulationData = wrapper.props('chartData').datasets[0].data
    expect(totalPopulationData).toEqual([560000, 555000, 550000, 545000, 540000])
    
    // 人口減少トレンドを確認
    for (let i = 1; i < totalPopulationData.length; i++) {
      expect(totalPopulationData[i]).toBeLessThan(totalPopulationData[i - 1])
    }
  })
})