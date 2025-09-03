import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'

// ルーターのセットアップ
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard }
  ]
})

describe('Dashboard.vue', () => {
  let wrapper

  beforeEach(async () => {
    await router.push('/')
    await router.isReady()
    
    wrapper = mount(Dashboard, {
      global: {
        plugins: [router]
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  it('ページが正しくレンダリングされる', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('ヘッダー要素が正しく表示される', () => {
    const header = wrapper.find('header')
    expect(header.exists()).toBe(true)
    expect(header.text()).toContain('すたっととっとり')
    expect(header.text()).toContain('鳥取県の住みやすさ向上と人口増加をサポートする情報ダッシュボード')
  })

  it('ページタイトルが正しく表示される', () => {
    const pageTitle = wrapper.find('h1')
    expect(pageTitle.exists()).toBe(true)
    expect(pageTitle.text()).toContain('すたっととっとり')
  })

  it('リアルタイム更新ステータスが表示される', () => {
    const statusIndicator = wrapper.find('.bg-green-400')
    expect(statusIndicator.exists()).toBe(true)
    
    const statusText = wrapper.find('.text-green-200')
    expect(statusText.exists()).toBe(true)
    expect(statusText.text()).toContain('リアルタイム更新中')
  })

  it('最終更新時刻が表示される', () => {
    const lastUpdated = wrapper.find('.text-blue-100')
    expect(lastUpdated.exists()).toBe(true)
    expect(lastUpdated.text()).toContain('鳥取県の住みやすさ向上')
  })

  it('共通ナビゲーションが含まれている', () => {
    const navigation = wrapper.findComponent({ name: 'CommonNavigation' })
    expect(navigation.exists()).toBe(true)
  })

  it('ページの説明文が表示される', () => {
    const description = wrapper.find('.text-gray-600')
    expect(description.exists()).toBe(true)
    expect(description.text()).toContain('鳥取県の主要な社会課題を統計データで俯瞰し、解決策の優先順位を分析します')
  })

  it('メインコンテンツエリアが存在する', () => {
    const mainContent = wrapper.find('main')
    expect(mainContent.exists()).toBe(true)
    expect(mainContent.classes()).toContain('container')
  })

  it('Tailwind CSSクラスが適用されている', () => {
    const header = wrapper.find('header')
    expect(header.classes()).toContain('bg-blue-600')
    expect(header.classes()).toContain('text-white')
    expect(header.classes()).toContain('shadow-lg')
  })

  it('レスポンシブ対応クラスが適用されている', () => {
    const container = wrapper.find('.container')
    expect(container.exists()).toBe(true)
    expect(container.classes()).toContain('mx-auto')
  })
})