import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
    // 登入頁
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { title: '登入', public: true }
    },
    {
        path: '/admin/scanner',
        name: 'AdminScanner',
        component: () => import('@/views/admin/Scanner.vue'),
        meta: { title: '掃碼簽到', requiresAuth: true, requiresCommittee: true }
    },
    {
        path: '/admin/event/create',
        name: 'EventCreate',
        component: () => import('@/views/admin/EventEdit.vue'),
        meta: { title: '新增活動', requiresAuth: true, requiresAdmin: true }
    },
    {
        path: '/admin/event/edit/:id',
        name: 'EventEdit',
        component: () => import('@/views/admin/EventEdit.vue'),
        meta: { title: '編輯活動', requiresAuth: true, requiresAdmin: true }
    },

    // 會員端路由 (預設)
    {
        path: '/m',
        component: () => import('@/layouts/MemberLayout.vue'),
        redirect: '/m/home',
        children: [
            {
                path: 'home',
                name: 'MemberHome',
                component: () => import('@/views/member/MemberHome.vue'),
                meta: { title: '首頁' }
            },
            {
                path: 'events',
                name: 'Events',
                component: () => import('@/views/member/Events.vue'),
                meta: { title: '活動' }
            },
            {
                path: 'membership',
                name: 'MyMembership',
                component: () => import('@/views/member/MyMembership.vue'),
                meta: { title: '我的會籍' }
            },
            {
                path: 'profile',
                name: 'MemberProfile',
                component: () => import('@/views/member/MemberProfile.vue'),
                meta: { title: '我的' }
            }
        ]
    },

    // 管理後台路由（僅管理員可訪問）
    {
        path: '/admin',
        component: () => import('@/layouts/AdminLayout.vue'),
        meta: { requiresAdmin: true },
        redirect: '/admin/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'AdminHome',
                component: () => import('@/views/Home.vue'),
                meta: { title: '儀表板' }
            },
            {
                path: 'scanner',
                name: 'AdminScanner',
                component: () => import('@/views/admin/Scanner.vue'),
                meta: { title: '掃碼簽到' }
            },
            {
                path: 'members',
                name: 'Members',
                component: () => import('@/views/Members.vue'),
                meta: { title: '會員管理' }
            },
            {
                path: 'member/:id',
                name: 'MemberDetail',
                component: () => import('@/views/MemberDetail.vue'),
                meta: { title: '會員詳情' }
            },
            {
                path: 'payments',
                name: 'Payments',
                component: () => import('@/views/Payments.vue'),
                meta: { title: '繳費管理' }
            },
            {
                path: 'profile',
                name: 'AdminProfile',
                component: () => import('@/views/Profile.vue'),
                meta: { title: '個人中心' }
            }
        ]
    },

    // 重定向首頁到會員端
    {
        path: '/',
        redirect: '/m'
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 路由守衛 - 未登入跳轉登入頁，後台需要管理員權限
router.beforeEach(async (to, from, next) => {
    document.title = to.meta.title ? `${to.meta.title} - 未來街坊` : '未來街坊'

    // 公開頁面不需要認證
    if (to.meta.public) {
        next()
        return
    }

    // 檢查是否已登入
    const token = localStorage.getItem('token')
    if (!token) {
        next({ path: '/login', replace: true })
        return
    }

    // 檢查管理員權限
    if (to.matched.some(r => r.meta.requiresAdmin)) {
        const { useAuthStore } = await import('@/stores/auth')
        // 嘗試獲取 store（如果 pinia 已安裝）
        try {
            const authStore = useAuthStore()
            // 確保已載入會籍資訊
            if (!authStore.membership) {
                await authStore.fetchMembership()
            }
            if (!authStore.isAdmin) {
                next({ path: '/m/home', replace: true })
                return
            }
        } catch {
            // pinia 未安裝時允許通過
        }
    }

    // 檢查圈委權限
    if (to.matched.some(r => r.meta.requiresCommittee)) {
        const { useAuthStore } = await import('@/stores/auth')
        try {
            const authStore = useAuthStore()
            if (!authStore.membership) {
                await authStore.fetchMembership()
            }
            if (!authStore.isCommitteeOrAbove) {
                next({ path: '/m/home', replace: true })
                return
            }
        } catch {
        }
    }

    next()
})

export default router
