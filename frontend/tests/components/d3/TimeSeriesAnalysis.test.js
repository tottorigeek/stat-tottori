import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import TimeSeriesAnalysis from '@/components/d3/TimeSeriesAnalysis.vue'

describe('TimeSeriesAnalysis.vue', () => {
  let wrapper
  
  const mockData = [
    { date: '2023-01-01', population: 570000, births: 4000, deaths: 6500 },
    { date: '2023-02-01', population: 569500, births: 3800, deaths: 6200 },
    { date: '2023-03-01', population: 569000, births: 4200, deaths: 6400 }
  ]

  beforeEach(() => {
    wrapper = mount(TimeSeriesAnalysis, {
      props: {
        data: mockData,
        valueFields: ['population', 'births', 'deaths'],
        width: 800,
        height: 400,
        dateField: 'date'
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  it('コンポーネントが正しくレンダリングされる', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.time-series-analysis').exists()).toBe(true)
  })

  it('コントロールパネルが表示される', () => {
    const controls = wrapper.find('.controls')
    expect(controls.exists()).toBe(true)
    
    // 系列選択のチェックボックス
    const checkboxes = controls.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThan(0)
  })

  it('データが正しく処理される', () => {
    const timeSeriesData = wrapper.vm.timeSeriesData
    expect(timeSeriesData).toHaveLength(3)
    
    // 日付が正しくDateオブジェクトに変換される
    expect(timeSeriesData[0].date).toBeInstanceOf(Date)
  })

  it('利用可能な系列が正しく設定される', () => {
    expect(wrapper.vm.availableSeries).toHaveLength(3)
    expect(wrapper.vm.availableSeries[0].key).toBe('population')
    expect(wrapper.vm.availableSeries[1].key).toBe('births')
    expect(wrapper.vm.availableSeries[2].key).toBe('deaths')
  })

  it('可視系列の初期状態が正しい', () => {
    expect(wrapper.vm.visibleSeries).toEqual(['population', 'births', 'deaths'])
  })

  it('系列の表示/非表示が切り替えられる', async () => {
    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setChecked(false)
    
    expect(wrapper.vm.visibleSeries).not.toContain('population')
  })

  it('アニメーション設定が切り替えられる', async () => {
    const animationCheckbox = wrapper.find('input[type="checkbox"]:last-child')
    await animationCheckbox.setChecked(false)
    
    expect(wrapper.vm.enableAnimation).toBe(false)
  })

  it('ズームリセットボタンが存在する', () => {
    const resetButton = wrapper.find('button')
    expect(resetButton.exists()).toBe(true)
    expect(resetButton.text()).toContain('ズームリセット')
  })

  it('ブラシチャートが条件によって表示される', async () => {
    await wrapper.setProps({ showBrush: true })
    expect(wrapper.find('.brush-context').exists()).toBe(true)
  })

  it('選択期間の統計が計算される', async () => {
    // 期間を設定
    wrapper.vm.selectedPeriod.start = new Date('2023-01-01')
    wrapper.vm.selectedPeriod.end = new Date('2023-03-01')
    
    await wrapper.vm.$nextTick()
    
    const stats = wrapper.vm.periodStats
    expect(stats.length).toBeGreaterThan(0)
  })

  it('値のフォーマットが正しく動作する', () => {
    expect(wrapper.vm.formatValue(1234.56)).toBe('1,234.6')
    expect(wrapper.vm.formatValue(null)).toBe('N/A')
  })

  it('propsの変更でグラフが更新される', async () => {
    const newData = [...mockData, { date: '2023-04-01', population: 568500, births: 4100, deaths: 6300 }]
    
    await wrapper.setProps({ data: newData })
    
    expect(wrapper.vm.timeSeriesData).toHaveLength(4)
  })
})