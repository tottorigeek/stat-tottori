<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- ヘッダー -->
      <div class="text-center">
        <h1 class="text-4xl font-bold text-blue-600">🏔️</h1>
        <h2 class="mt-4 text-3xl font-bold text-gray-900">
          アカウント作成
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          鳥取県統計分析プラットフォームへの新規登録
        </p>
      </div>

      <!-- 登録フォーム -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <!-- ユーザー名 -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              ユーザー名 <span class="text-red-500">*</span>
            </label>
            <div class="mt-1">
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="英数字、アンダースコア、ハイフンが使用可能"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- メールアドレス -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              メールアドレス <span class="text-red-500">*</span>
            </label>
            <div class="mt-1">
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="your-email@example.com"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- パスワード -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              パスワード <span class="text-red-500">*</span>
            </label>
            <div class="mt-1 relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="8文字以上の複雑なパスワード"
                :disabled="isLoading"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                :disabled="isLoading"
              >
                <svg
                  class="h-5 w-5 text-gray-400 hover:text-gray-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    v-if="showPassword"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
                  />
                  <path
                    v-else
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    v-if="!showPassword"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </button>
            </div>
            <div class="mt-1">
              <div class="text-xs text-gray-500 space-y-1">
                <p :class="{ 'text-green-600': passwordChecks.length, 'text-gray-500': !passwordChecks.length }">
                  ✓ 8文字以上
                </p>
                <p :class="{ 'text-green-600': passwordChecks.uppercase, 'text-gray-500': !passwordChecks.uppercase }">
                  ✓ 大文字を含む
                </p>
                <p :class="{ 'text-green-600': passwordChecks.lowercase, 'text-gray-500': !passwordChecks.lowercase }">
                  ✓ 小文字を含む
                </p>
                <p :class="{ 'text-green-600': passwordChecks.number, 'text-gray-500': !passwordChecks.number }">
                  ✓ 数字を含む
                </p>
              </div>
            </div>
          </div>

          <!-- 氏名 -->
          <div>
            <label for="fullName" class="block text-sm font-medium text-gray-700">
              氏名
            </label>
            <div class="mt-1">
              <input
                id="fullName"
                v-model="form.fullName"
                type="text"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="山田太郎"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- 所属部署 -->
          <div>
            <label for="department" class="block text-sm font-medium text-gray-700">
              所属部署
            </label>
            <div class="mt-1">
              <input
                id="department"
                v-model="form.department"
                type="text"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="政策企画部"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- 所属組織 -->
          <div>
            <label for="organization" class="block text-sm font-medium text-gray-700">
              所属組織
            </label>
            <div class="mt-1">
              <input
                id="organization"
                v-model="form.organization"
                type="text"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="鳥取県庁"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- エラーメッセージ -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- 成功メッセージ -->
          <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-green-700">{{ successMessage }}</p>
              </div>
            </div>
          </div>

          <!-- 登録ボタン -->
          <div>
            <button
              type="submit"
              :disabled="isLoading || !isFormValid"
              class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <span v-if="isLoading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                登録中...
              </span>
              <span v-else>
                アカウント作成
              </span>
            </button>
          </div>

          <!-- ログインリンク -->
          <div class="text-center">
            <p class="text-sm text-gray-600">
              既にアカウントをお持ちの方は
              <router-link
                to="/login"
                class="font-medium text-blue-600 hover:text-blue-500"
              >
                ログイン
              </router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    // フォームデータ
    const form = ref({
      username: '',
      email: '',
      password: '',
      fullName: '',
      department: '',
      organization: ''
    })

    const showPassword = ref(false)
    const isLoading = ref(false)
    const error = ref('')
    const successMessage = ref('')

    // パスワード強度チェック
    const passwordChecks = computed(() => ({
      length: form.value.password.length >= 8,
      uppercase: /[A-Z]/.test(form.value.password),
      lowercase: /[a-z]/.test(form.value.password),
      number: /\d/.test(form.value.password)
    }))

    // フォームバリデーション
    const isFormValid = computed(() => {
      return (
        form.value.username.trim() &&
        form.value.email.trim() &&
        form.value.password &&
        passwordChecks.value.length &&
        passwordChecks.value.uppercase &&
        passwordChecks.value.lowercase &&
        passwordChecks.value.number
      )
    })

    // エラーをクリア（入力時）
    watch(() => form.value, () => {
      if (error.value) {
        error.value = ''
      }
    }, { deep: true })

    // 登録処理
    const handleRegister = async () => {
      if (!isFormValid.value) {
        error.value = 'すべての必須項目を正しく入力してください'
        return
      }

      error.value = ''
      successMessage.value = ''
      isLoading.value = true

      try {
        const result = await authStore.register({
          username: form.value.username.trim(),
          email: form.value.email.trim(),
          password: form.value.password,
          full_name: form.value.fullName.trim() || null,
          department: form.value.department.trim() || null,
          organization: form.value.organization.trim() || null
        })

        if (result.success) {
          successMessage.value = result.message
          // 3秒後にログインページへリダイレクト
          setTimeout(() => {
            router.push('/login')
          }, 3000)
        } else {
          error.value = result.error
        }
      } catch (err) {
        error.value = 'ユーザー登録に失敗しました。再度お試しください。'
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      showPassword,
      isLoading,
      error,
      successMessage,
      passwordChecks,
      isFormValid,
      handleRegister
    }
  }
}
</script>

<style scoped>
/* カスタムスタイルが必要な場合はここに追加 */
</style>