<template>
  <nav class="bg-white shadow-lg border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- ロゴとブランド名 -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-3 group">
            <div class="text-2xl group-hover:scale-110 transition-transform duration-200">🏔️</div>
            <div>
              <span class="text-xl font-bold text-blue-600 group-hover:text-blue-700 transition-colors duration-200">すたっととっとり</span>
              <p class="text-xs text-gray-500 hidden sm:block">鳥取県住みやすさ向上プロジェクト</p>
            </div>
          </router-link>
        </div>

        <!-- デスクトップメニュー -->
        <div class="hidden lg:flex items-center space-x-1">
          <router-link
            v-for="route in navigationRoutes"
            :key="route.name"
            :to="{ name: route.name }"
            :class="[
              'px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2',
              isActiveRoute(route.name)
                ? 'bg-blue-100 text-blue-700 shadow-sm'
                : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
            ]"
          >
            <span class="text-lg">{{ route.meta.icon }}</span>
            <span>{{ route.meta.title }}</span>
          </router-link>
        </div>

        <!-- タブレット用メニュー -->
        <div class="hidden md:flex lg:hidden items-center space-x-1">
          <router-link
            v-for="route in navigationRoutes"
            :key="route.name"
            :to="{ name: route.name }"
            :class="[
              'px-2 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex flex-col items-center space-y-1',
              isActiveRoute(route.name)
                ? 'bg-blue-100 text-blue-700 shadow-sm'
                : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
            ]"
          >
            <span class="text-base">{{ route.meta.icon }}</span>
            <span class="text-xs">{{ getShortTitle(route.meta.title) }}</span>
          </router-link>
        </div>

        <!-- モバイル用ハンバーガーメニューボタン -->
        <div class="md:hidden flex items-center">
          <button
            @click="toggleMobileMenu"
            :class="[
              'inline-flex items-center justify-center p-2 rounded-lg transition-all duration-200',
              mobileMenuOpen
                ? 'text-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
            ]"
            :aria-expanded="mobileMenuOpen"
            aria-label="メニューを開く"
          >
            <svg class="h-6 w-6" :class="{ 'hidden': mobileMenuOpen }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg class="h-6 w-6" :class="{ 'hidden': !mobileMenuOpen }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- モバイルメニュー -->
    <div :class="[
      'md:hidden transition-all duration-300 ease-in-out overflow-hidden',
      mobileMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
    ]">
      <div class="px-2 pt-2 pb-3 space-y-1 bg-gray-50 border-t border-gray-200">
        <router-link
          v-for="route in navigationRoutes"
          :key="route.name"
          :to="{ name: route.name }"
          @click="closeMobileMenu"
          :class="[
            'flex items-center space-x-3 px-3 py-3 rounded-lg text-base font-medium transition-all duration-200',
            isActiveRoute(route.name)
              ? 'bg-blue-100 text-blue-700 shadow-sm'
              : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
          ]"
        >
          <span class="text-xl">{{ route.meta.icon }}</span>
          <span>{{ route.meta.title }}</span>
          <div v-if="isActiveRoute(route.name)" class="ml-auto">
            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
          </div>
        </router-link>
      </div>
    </div>

    <!-- 現在のページ情報（モバイル時の補助） -->
    <div v-if="currentRoute.meta" class="md:hidden bg-blue-50 border-t border-blue-100">
      <div class="px-4 py-2">
        <div class="flex items-center space-x-2 text-sm">
          <span class="text-blue-600">{{ currentRoute.meta.icon }}</span>
          <span class="text-blue-700 font-medium">{{ currentRoute.meta.title }}</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { useRoute, useRouter } from 'vue-router'
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'Navigation',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const mobileMenuOpen = ref(false)

    const navigationRoutes = computed(() => {
      return router.getRoutes().filter(r => r.meta?.title)
    })

    const currentRoute = computed(() => route)

    const isActiveRoute = (routeName) => {
      return route.name === routeName
    }

    const getShortTitle = (title) => {
      const shortTitles = {
        'リアルタイム生活情報': 'リアルタイム',
        '雇用・経済情報': '雇用・経済',
        '子育て・高齢者支援': '子育て・高齢者',
        '住みやすさ分析': '住みやすさ',
        '施策効果追跡': '施策追跡',
        'プロジェクトについて': 'About'
      }
      return shortTitles[title] || title
    }

    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
    }

    const closeMobileMenu = () => {
      mobileMenuOpen.value = false
    }

    // 画面サイズが変更された時にモバイルメニューを閉じる
    const handleResize = () => {
      if (window.innerWidth >= 768) { // md breakpoint
        mobileMenuOpen.value = false
      }
    }

    // ルート変更時にモバイルメニューを閉じる
    const unwatch = router.afterEach(() => {
      closeMobileMenu()
    })

    onMounted(() => {
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      unwatch()
    })

    return {
      navigationRoutes,
      currentRoute,
      mobileMenuOpen,
      isActiveRoute,
      getShortTitle,
      toggleMobileMenu,
      closeMobileMenu
    }
  }
}
</script>

<style scoped>
/* カスタムスタイル */
.router-link-exact-active {
  /* Vue Routerのデフォルトアクティブクラスを無効化 */
}

/* ホバーエフェクトのアニメーション */
.group:hover .transition-transform {
  transform: scale(1.1);
}

/* スムーズなトランジション */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* モバイルメニューのスムーズなアニメーション */
.max-h-0 {
  max-height: 0;
}

.max-h-96 {
  max-height: 24rem;
}
</style>