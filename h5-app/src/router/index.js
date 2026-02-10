import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
    // 會員端路由 (預設)
    {
        path: '/m',
        component: () => import('@/layouts/MemberLayout.vue'),
        children: [
            {
                path: '',
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

    // 管理後台路由
    {
        path: '/admin',
        component: () => import('@/layouts/AdminLayout.vue'),
        children: [
            {
                path: '',
                name: 'AdminHome',
                component: () => import('@/views/Home.vue'),
                meta: { title: '儀表板' }
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

// 設置頁面標題
router.beforeEach((to, from, next) => {
    document.title = to.meta.title ? `${to.meta.title} - 未來街坊` : '未來街坊'
    next()
})

export default router
