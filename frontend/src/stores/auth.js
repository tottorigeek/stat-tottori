import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 状態
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const isLoading = ref(false)
  const error = ref(null)

  // 計算プロパティ
  const isAuthenticated = computed(() => {
    return !!token.value && !!user.value
  })

  const isAdmin = computed(() => {
    return user.value?.role === 'admin'
  })

  const isAnalyst = computed(() => {
    return user.value?.role === 'analyst' || isAdmin.value
  })

  const isPolicyMaker = computed(() => {
    return user.value?.role === 'policy_maker' || isAdmin.value
  })

  // アクション
  const login = async (credentials) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'ログインに失敗しました')
      }

      // トークンを保存
      token.value = data.access_token
      refreshToken.value = data.refresh_token
      user.value = data.user

      // ローカルストレージに保存
      localStorage.setItem('token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refreshToken', data.refresh_token)
      }

      return { success: true }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'ユーザー登録に失敗しました')
      }

      return { success: true, message: data.message }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    isLoading.value = true

    try {
      if (token.value) {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token.value}`
          }
        })
      }
    } catch (err) {
      console.warn('ログアウト時のエラー:', err)
    } finally {
      // ローカル状態をクリア
      user.value = null
      token.value = null
      refreshToken.value = null
      error.value = null

      // ローカルストレージをクリア
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')

      isLoading.value = false
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('リフレッシュトークンがありません')
    }

    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          refresh_token: refreshToken.value
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error('トークンの更新に失敗しました')
      }

      token.value = data.access_token
      localStorage.setItem('token', data.access_token)

      return data.access_token

    } catch (err) {
      // リフレッシュトークンが無効な場合はログアウト
      await logout()
      throw err
    }
  }

  const getCurrentUser = async () => {
    if (!token.value) {
      return null
    }

    try {
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })

      if (!response.ok) {
        if (response.status === 401) {
          // トークンが無効な場合はリフレッシュを試行
          if (refreshToken.value) {
            await refreshAccessToken()
            return getCurrentUser() // 再帰呼び出し
          } else {
            await logout()
            return null
          }
        }
        throw new Error('ユーザー情報の取得に失敗しました')
      }

      const userData = await response.json()
      user.value = userData

      return userData

    } catch (err) {
      console.error('ユーザー情報取得エラー:', err)
      await logout()
      return null
    }
  }

  const updateProfile = async (profileData) => {
    if (!token.value) {
      throw new Error('認証が必要です')
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/v1/auth/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token.value}`
        },
        body: JSON.stringify(profileData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'プロフィール更新に失敗しました')
      }

      user.value = data
      return { success: true }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (passwordData) => {
    if (!token.value) {
      throw new Error('認証が必要です')
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token.value}`
        },
        body: JSON.stringify(passwordData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'パスワード変更に失敗しました')
      }

      // パスワード変更後は再ログインが必要
      await logout()

      return { success: true, message: data.message }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const requestPasswordReset = async (email) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/v1/auth/request-password-reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'パスワードリセット要求に失敗しました')
      }

      return { success: true, message: data.message }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const resetPassword = async (token, newPassword) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/v1/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          token,
          new_password: newPassword
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'パスワードリセットに失敗しました')
      }

      return { success: true, message: data.message }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const verifyEmail = async (token) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/v1/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'メール認証に失敗しました')
      }

      return { success: true, message: data.message }

    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  // 初期化時にトークンがあれば ユーザー情報を取得
  const initializeAuth = async () => {
    if (token.value) {
      try {
        await getCurrentUser()
      } catch (err) {
        console.error('認証初期化エラー:', err)
        // トークンが無効な場合はクリア
        await logout()
      }
    }
  }

  return {
    // 状態
    user,
    token,
    isLoading,
    error,

    // 計算プロパティ
    isAuthenticated,
    isAdmin,
    isAnalyst,
    isPolicyMaker,

    // アクション
    login,
    register,
    logout,
    refreshAccessToken,
    getCurrentUser,
    updateProfile,
    changePassword,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    initializeAuth
  }
})