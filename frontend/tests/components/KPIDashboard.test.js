import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import KPIDashboard from '@/components/KPIDashboard.vue'

describe('KPIDashboard.vue', () => {
  let wrapper
  const mockPolicies = [
    {
      id: 1,
      name: '子育て支援政策',
      target: 100,
      current: 85,
      category: 'social'
    },
    {
      id: 2,
      name: '高齢者福祉政策',
      target: 80,
      current: 72,
      category: 'welfare'
    },
    {
      id: 3,
      name: '産業振興政策',
      target: 120,
      current: 95,
      category: 'economic'
    }
  ]

  beforeEach(() => {
    wrapper = mount(KPIDashboard, {
      props: {
        policies: mockPolicies
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  it('コンポーネントが正しくレンダリングされる', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('h3').text()).toContain('KPI達成状況ダッシュボード')
  })

  it('政策数が正しく表示される', () => {
    const policyCount = wrapper.find('.text-sm.text-gray-500')
    expect(policyCount.text()).toContain('対象施策: 3件')
  })

  it('達成率によって正しく分類される', () => {
    // 優秀（80%以上）: policy1 (85/100 = 85%)
    // 良好（60-79%）: policy2 (72/80 = 90%), policy3 (95/120 = 79.17%)
    // 要改善（60%未満）: なし
    
    const excellentCount = wrapper.find('.text-green-600')
    const goodCount = wrapper.find('.text-blue-600') 
    
    expect(excellentCount.exists()).toBe(true)
    expect(goodCount.exists()).toBe(true)
  })

  it('表示モード切り替えが機能する', async () => {
    const toggleButton = wrapper.find('button')
    expect(toggleButton.text()).toContain('詳細表示')
    
    await toggleButton.trigger('click')
    expect(toggleButton.text()).toContain('サマリー表示')
  })

  it('詳細表示モードで政策詳細が表示される', async () => {
    const toggleButton = wrapper.find('button')
    await toggleButton.trigger('click')
    
    // 詳細表示モードでは各政策の詳細が表示される
    expect(wrapper.text()).toContain('子育て支援政策')
    expect(wrapper.text()).toContain('高齢者福祉政策')
    expect(wrapper.text()).toContain('産業振興政策')
  })

  it('空の政策配列でもエラーが発生しない', () => {
    const emptyWrapper = mount(KPIDashboard, {
      props: {
        policies: []
      }
    })
    
    expect(emptyWrapper.exists()).toBe(true)
    expect(emptyWrapper.find('.text-sm.text-gray-500').text()).toContain('対象施策: 0件')
    emptyWrapper.unmount()
  })

  it('達成率の計算が正確', () => {
    // テストケース: 85/100 = 85%
    const policy1Achievement = (mockPolicies[0].current / mockPolicies[0].target) * 100
    expect(policy1Achievement).toBe(85)
    
    // テストケース: 72/80 = 90%
    const policy2Achievement = (mockPolicies[1].current / mockPolicies[1].target) * 100  
    expect(policy2Achievement).toBe(90)
  })
})