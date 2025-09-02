<template>
  <nav class="bg-blue-700 shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- ロゴ・サービス名 -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-2 text-white hover:text-blue-200 transition-colors duration-200">
            <span class="text-2xl">🏔️</span>
            <span class="text-xl font-bold">すたっととっとり</span>
          </router-link>
        </div>

        <!-- ナビゲーションメニュー -->
        <div class="hidden md:flex space-x-1">
          <router-link 
            to="/" 
            class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            active-class="bg-blue-800 text-white"
          >
            🏠 ホーム
          </router-link>
          <router-link 
            to="/population" 
            class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            active-class="bg-blue-800 text-white"
          >
            📊 人口推移
          </router-link>
          <router-link 
            to="/livability-comparison" 
            class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            active-class="bg-blue-800 text-white"
          >
            🏠 住みやすさ比較
          </router-link>
          <router-link 
            to="/population-detail" 
            class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            active-class="bg-blue-800 text-white"
          >
            📈 人口詳細
          </router-link>
        </div>

        <!-- モバイルメニューボタン -->
        <div class="md:hidden">
          <button 
            @click="toggleMobileMenu" 
            class="text-white hover:text-blue-200 focus:outline-none focus:text-blue-200"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- モバイルメニュー -->
      <div v-if="isMobileMenuOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1 bg-blue-800 rounded-b-lg">
          <router-link 
            to="/" 
            class="text-white hover:text-blue-200 block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
            active-class="bg-blue-900 text-white"
            @click="closeMobileMenu"
          >
            🏠 ホーム
          </router-link>
          <router-link 
            to="/population" 
            class="text-white hover:text-blue-200 block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
            active-class="bg-blue-900 text-white"
            @click="closeMobileMenu"
          >
            📊 人口推移
          </router-link>
          <router-link 
            to="/livability-comparison" 
            class="text-white hover:text-blue-200 block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
            active-class="bg-blue-900 text-white"
            @click="closeMobileMenu"
          >
            🏠 住みやすさ比較
          </router-link>
          <router-link 
            to="/population-detail" 
            class="text-white hover:text-blue-200 block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
            active-class="bg-blue-900 text-white"
            @click="closeMobileMenu"
          >
            📈 人口詳細
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'CommonNavigation',
  data() {
    return {
      isMobileMenuOpen: false
    }
  },
  methods: {
    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },
    closeMobileMenu() {
      this.isMobileMenuOpen = false
    }
  },
  watch: {
    $route() {
      // ルートが変更されたらモバイルメニューを閉じる
      this.closeMobileMenu()
    }
  }
}
</script>

<style scoped>
/* 必要に応じてカスタムスタイルを追加 */
</style>
