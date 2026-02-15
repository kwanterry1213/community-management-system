import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi, membershipApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
    // 狀態
    const token = ref(localStorage.getItem('token') || '')
    const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
    const membership = ref(null)
    const loading = ref(false)

    // 計算屬性
    const isLoggedIn = computed(() => !!token.value && !!user.value)
    const currentUser = computed(() => user.value)
    const userId = computed(() => user.value?.id)

    // 用戶級別（根據 membership role 映射）
    const userLevel = computed(() => {
        if (!membership.value) return 'friend'
        const role = membership.value.role
        if (role === 'admin') return 'admin'
        if (role === 'staff') return 'committee'
        if (role === 'member') return 'citizen'
        return 'friend'
    })

    const levelInfo = computed(() => {
        const levels = {
            admin: { name: '系統管理員', icon: '👑', color: '#e53e3e' },
            committee: { name: '未來街坊圈圈委', icon: '⭐⭐⭐', color: '#d69e2e' },
            citizen: { name: '未來街坊圈圈民', icon: '⭐⭐', color: '#3182ce' },
            friend: { name: '未來街坊圈圈友', icon: '⭐', color: '#718096' },
        }
        return levels[userLevel.value]
    })

    // 權限控制
    const isAdmin = computed(() => userLevel.value === 'admin')
    const isCommitteeOrAbove = computed(() => ['admin', 'committee'].includes(userLevel.value))

    // Helper to extract error message
    function getErrorMessage(err, defaultMsg) {
        const detail = err.response?.data?.detail
        if (typeof detail === 'string') return detail
        if (Array.isArray(detail)) {
            // Handle FastAPI 422 validation errors
            return detail.map(e => e.msg).join(', ')
        }
        if (detail && typeof detail === 'object') {
            return JSON.stringify(detail)
        }
        return defaultMsg
    }

    // 登入
    async function login(identifier, password) {
        loading.value = true
        try {
            const res = await authApi.login(identifier, password)
            token.value = res.access_token
            user.value = res.user_info
            localStorage.setItem('token', res.access_token)
            localStorage.setItem('user', JSON.stringify(res.user_info))
            // 嘗試獲取會籍
            await fetchMembership()
            return { success: true }
        } catch (err) {
            console.error('Login error:', err)
            return { success: false, message: getErrorMessage(err, '登入失敗') }
        } finally {
            loading.value = false
        }
    }

    // 註冊
    async function register(data) {
        loading.value = true
        try {
            await authApi.register(data)
            // 註冊成功後自動登入
            await login(data.email || data.username, data.password) // Use email or username for login
            return { success: true }
        } catch (err) {
            console.error('Register error:', err)
            return { success: false, message: getErrorMessage(err, '註冊失敗') }
        } finally {
            loading.value = false
        }
    }

    // 登出
    function logout() {
        token.value = ''
        user.value = null
        membership.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
    }

    // 獲取用戶資訊
    async function fetchProfile() {
        if (!user.value?.id) return
        try {
            const res = await userApi.getProfile(user.value.id)
            user.value = { ...user.value, ...res }
            localStorage.setItem('user', JSON.stringify(user.value))
        } catch (err) {
            console.error('獲取用戶資訊失敗', err)
        }
    }

    // 獲取會籍
    async function fetchMembership() {
        if (!user.value?.id) return
        try {
            const list = await membershipApi.list({ user_id: user.value.id })
            membership.value = list.length > 0 ? list[0] : null
        } catch (err) {
            console.error('獲取會籍失敗', err)
        }
    }

    // 更新個人資料
    async function updateProfile(data) {
        if (!user.value?.id) return
        try {
            const res = await userApi.updateProfile(user.value.id, data)
            user.value = { ...user.value, ...res }
            localStorage.setItem('user', JSON.stringify(user.value))
            return { success: true }
        } catch (err) {
            return { success: false, message: getErrorMessage(err, '更新失敗') }
        }
    }

    return {
        token,
        user,
        membership,
        loading,
        isLoggedIn,
        currentUser,
        userId,
        userLevel,
        levelInfo,
        isAdmin,
        isCommitteeOrAbove,
        login,
        register,
        logout,
        fetchProfile,
        fetchMembership,
        updateProfile,
    }
})
