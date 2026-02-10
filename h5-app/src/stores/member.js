import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMemberStore = defineStore('member', () => {
    // 模擬會員數據
    const members = ref([
        {
            id: 'M-2024-0158',
            name: '陳大明',
            phone: '0912-345-678',
            email: 'daming.chen@email.com',
            company: '大明科技股份有限公司',
            title: '總經理',
            membershipType: 'gold',
            status: 'active',
            expiryDate: '2026-06-30',
            joinDate: '2022-06-15',
            avatar: 'https://ui-avatars.com/api/?name=陳大明&background=3182ce&color=fff'
        },
        {
            id: 'M-2024-0159',
            name: '林小華',
            phone: '0923-456-789',
            email: 'xiaohua.lin@email.com',
            company: '華創投資有限公司',
            title: '財務經理',
            membershipType: 'silver',
            status: 'pending',
            expiryDate: null,
            joinDate: '2026-02-09',
            avatar: 'https://ui-avatars.com/api/?name=林小華&background=38a169&color=fff'
        },
        {
            id: 'M-2024-0160',
            name: '王建國',
            phone: '0934-567-890',
            email: 'jianguo.wang@email.com',
            company: '建國貿易公司',
            title: '業務總監',
            membershipType: 'normal',
            status: 'expired',
            expiryDate: '2026-01-15',
            joinDate: '2023-01-15',
            avatar: 'https://ui-avatars.com/api/?name=王建國&background=e53e3e&color=fff'
        },
        {
            id: 'M-2024-0161',
            name: '張美玲',
            phone: '0945-678-901',
            email: 'meiling.zhang@email.com',
            company: '美玲設計工作室',
            title: '創辦人',
            membershipType: 'gold',
            status: 'active',
            expiryDate: '2026-12-31',
            joinDate: '2021-12-01',
            avatar: 'https://ui-avatars.com/api/?name=張美玲&background=d69e2e&color=fff'
        },
        {
            id: 'M-2024-0162',
            name: '李志明',
            phone: '0956-789-012',
            email: 'zhiming.li@email.com',
            company: '志明企業集團',
            title: '董事長',
            membershipType: 'enterprise',
            status: 'active',
            expiryDate: '2026-09-30',
            joinDate: '2020-09-01',
            avatar: 'https://ui-avatars.com/api/?name=李志明&background=718096&color=fff'
        }
    ])

    // 統計數據
    const stats = computed(() => ({
        total: members.value.length,
        active: members.value.filter(m => m.status === 'active').length,
        pending: members.value.filter(m => m.status === 'pending').length,
        expired: members.value.filter(m => m.status === 'expired').length
    }))

    // 根據 ID 獲取會員
    const getMemberById = (id) => {
        return members.value.find(m => m.id === id)
    }

    // 會籍類型映射
    const membershipTypes = {
        normal: { label: '普通會員', color: '#718096', icon: 'user-o' },
        silver: { label: '銀級會員', color: '#5a6a7e', icon: 'medal-o' },
        gold: { label: '金級會員', color: '#d69e2e', icon: 'diamond-o' },
        enterprise: { label: '企業會員', color: '#3182ce', icon: 'shop-o' }
    }

    // 狀態映射
    const statusTypes = {
        active: { label: '有效', color: '#38a169', type: 'success' },
        pending: { label: '待審核', color: '#3182ce', type: 'primary' },
        expired: { label: '已過期', color: '#e53e3e', type: 'danger' }
    }

    return {
        members,
        stats,
        getMemberById,
        membershipTypes,
        statusTypes
    }
})
