import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi, membershipApi } from '@/services/api'

export const useMemberStore = defineStore('member', () => {
    const members = ref([])
    const loading = ref(false)

    // 從 API 載入會員列表（users + memberships）
    async function fetchMembers() {
        loading.value = true
        try {
            const [users, memberships] = await Promise.all([
                userApi.listUsers(),
                membershipApi.list(),
            ])

            // 合併 user + membership 資訊
            members.value = users.map(user => {
                const ms = memberships.find(m => m.user_id === user.id)
                return {
                    id: user.id,
                    membershipId: ms?.id,
                    name: user.username,
                    avatar: user.profile_picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=1a365d&color=fff`,
                    email: user.email,
                    phone: user.phone,
                    bio: user.bio,
                    skills: user.skills,
                    occupation: user.occupation,
                    joinDate: ms?.joined_at?.split('T')[0] || user.created_at?.split('T')[0] || '—',
                    level: ms?.role === 'admin' ? 'admin' : ms?.role === 'staff' ? 'committee' : ms?.role === 'member' ? 'citizen' : 'friend',
                    status: ms?.status || 'pending',
                    membershipNo: ms?.membership_no || '',
                    expiryDate: ms?.expires_at?.split('T')[0] || '',
                }
            })
        } catch (err) {
            console.error('載入會員列表失敗', err)
        } finally {
            loading.value = false
        }
    }

    // 統計
    const stats = computed(() => ({
        total: members.value.length,
        active: members.value.filter(m => m.status === 'active').length,
        pending: members.value.filter(m => m.status === 'pending').length,
        expired: members.value.filter(m => m.status === 'expired').length,
    }))

    // 級別映射
    const membershipTypes = {
        admin: { label: '管理員', color: '#e53e3e', icon: '👑' },
        committee: { label: '圈委', color: '#d69e2e', icon: '⭐⭐⭐' },
        citizen: { label: '圈民', color: '#3182ce', icon: '⭐⭐' },
        friend: { label: '圈友', color: '#718096', icon: '⭐' },
    }

    const statusTypes = {
        active: { label: '有效', type: 'success' },
        pending: { label: '待審核', type: 'warning' },
        expired: { label: '已過期', type: 'danger' },
    }

    function getMemberById(id) {
        return members.value.find(m => m.id === parseInt(id))
    }

    return {
        members,
        loading,
        stats,
        membershipTypes,
        statusTypes,
        fetchMembers,
        getMemberById,
    }
})
