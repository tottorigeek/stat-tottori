import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NetworkVisualization from '@/components/d3/NetworkVisualization.vue'

describe('NetworkVisualization.vue', () => {
  let wrapper
  
  const mockNodes = [
    { id: '1', name: '鳥取市', category: '市', value: 100 },
    { id: '2', name: '米子市', category: '市', value: 80 },
    { id: '3', name: '倉吉市', category: '市', value: 60 }
  ]
  
  const mockLinks = [
    { source: '1', target: '2', value: 50 },
    { source: '2', target: '3', value: 30 }
  ]

  beforeEach(() => {
    wrapper = mount(NetworkVisualization, {
      props: {
        nodes: mockNodes,
        links: mockLinks,
        width: 800,
        height: 600
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  it('コンポーネントが正しくレンダリングされる', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.network-visualization').exists()).toBe(true)
  })

  it('コントロールパネルが表示される', () => {
    const controls = wrapper.find('.controls')
    expect(controls.exists()).toBe(true)
    
    // Force強度のスライダー
    expect(controls.find('input[type="range"]').exists()).toBe(true)
    
    // ボタン類
    expect(controls.find('button').exists()).toBe(true)
  })

  it('ノードデータが正しく受け取られる', () => {
    expect(wrapper.vm.nodes).toEqual(mockNodes)
    expect(wrapper.vm.links).toEqual(mockLinks)
  })

  it('networkDataが正しく計算される', () => {
    const networkData = wrapper.vm.networkData
    expect(networkData.nodes).toHaveLength(3)
    expect(networkData.links).toHaveLength(2)
  })

  it('Force強度の変更が反映される', async () => {
    const forceSlider = wrapper.find('input[type="range"]')
    await forceSlider.setValue(50)
    
    expect(wrapper.vm.forceStrength).toBe(50)
  })

  it('レジェンドが表示される', () => {
    const legend = wrapper.find('.legend')
    expect(legend.exists()).toBe(true)
    expect(legend.find('h4').text()).toContain('凡例')
  })

  it('ツールチップが存在する', () => {
    const tooltip = wrapper.find('.tooltip')
    expect(tooltip.exists()).toBe(true)
  })

  it('ボタンクリックイベントが動作する', async () => {
    const restartButton = wrapper.find('button')
    await restartButton.trigger('click')
    
    // エラーが発生しないことを確認
    expect(wrapper.emitted()).toBeDefined()
  })

  it('propsの変更で再描画される', async () => {
    const newNodes = [...mockNodes, { id: '4', name: '境港市', category: '市', value: 40 }]
    
    await wrapper.setProps({ nodes: newNodes })
    
    expect(wrapper.vm.networkData.nodes).toHaveLength(4)
  })
})