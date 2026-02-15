<template>
  <div class="page payments-page">
    <van-nav-bar title="繳費管理" />

    <!-- 收款統計 -->
    <div class="stats-row">
      <div class="stat-card"><div class="stat-label">本月應收</div><div class="stat-value">$245,000</div></div>
      <div class="stat-card green"><div class="stat-label">已收款</div><div class="stat-value">$189,200</div></div>
      <div class="stat-card orange"><div class="stat-label">待收款</div><div class="stat-value">$55,800</div></div>
    </div>

    <!-- 分類標籤 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="待繳費" name="pending" badge="42" />
      <van-tab title="已繳費" name="paid" />
      <van-tab title="逾期未繳" name="overdue" badge="8" />
    </van-tabs>

    <!-- 繳費列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <div class="payment-list">
        <div v-for="item in paymentList" :key="item.id" class="payment-card">
          <div class="payment-header">
            <img :src="item.avatar" class="payment-avatar" />
            <div class="payment-info">
              <span class="payment-name">{{ item.username || '未知會員' }}</span>
              <span class="payment-desc">{{ item.description }}</span>
            </div>
            <span :class="['status-tag', item.statusClass]">{{ item.statusText }}</span>
          </div>
          <div class="payment-body">
            <div class="payment-row"><span>分類</span><span>{{ item.membershipLabel }}</span></div>
            <div class="payment-row"><span>金額</span><span class="amount">${{ item.amount }}</span></div>
            <div class="payment-row"><span>建立時間</span><span>{{ new Date(item.created_at).toLocaleDateString() }}</span></div>
            <div class="payment-row"><span>支付方式</span><span>{{ item.method || '未定' }}</span></div>
          </div>
          <div class="payment-actions">
            <van-button 
                v-if="item.status === 'pending'" 
                size="small" 
                type="success" 
                icon="success" 
                @click="confirmPayment(item)"
            >確認收款</van-button>
            <van-button size="small" plain icon="bell" @click="sendReminder(item)">發送提醒</van-button>
          </div>
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { paymentApi } from '@/services/api'
import { showToast, showDialog } from 'vant'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const activeTab = ref('pending')
const refreshing = ref(false)
const payments = ref([])

const paymentList = computed(() => {
  return payments.value.filter(p => {
    if (activeTab.value === 'pending') return p.status === 'pending'
    if (activeTab.value === 'paid') return p.status === 'paid'
    if (activeTab.value === 'overdue') return p.status === 'overdue'
    return true
  }).map(p => ({
    ...p,
    avatar: p.profile_picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(p.username || 'User')}&background=random&color=fff`,
    statusText: getStatusText(p.status),
    statusClass: p.status,
    membershipLabel: p.related_type === 'event' ? '活動費' : '會費'
  }))
})

const getStatusText = (status) => {
    const map = { pending: '待繳費', paid: '已繳費', overdue: '逾期' }
    return map[status] || status
}

const fetchPayments = async () => {
    try {
        const res = await paymentApi.list({ community_id: 1 }) // Fetch all payments for community (admin view)
        payments.value = res
    } catch (error) {
        showToast('無法獲取繳費列表')
    } finally {
        refreshing.value = false
    }
}

const onRefresh = () => {
    fetchPayments()
}

const confirmPayment = (item) => {
    showDialog({
        title: '確認收款',
        message: `確定收到 ${item.description} 的款項 $${item.amount} 嗎？`,
        showCancelButton: true
    }).then(async () => {
        try {
            await paymentApi.update(item.id, { status: 'paid' })
            showToast('收款成功')
            fetchPayments()
        } catch (error) {
            showToast('操作失敗')
        }
    })
}

const sendReminder = (item) => {
    showToast('已發送提醒 (模擬)')
}

onMounted(() => {
    fetchPayments()
})
</script>

<style scoped>
.payments-page { padding: 0; background: var(--color-gray-100); }

.stats-row { display: flex; gap: 10px; padding: 12px; }
.stat-card { flex: 1; background: white; border-radius: 10px; padding: 12px; text-align: center; }
.stat-card.green .stat-value { color: var(--color-success); }
.stat-card.orange .stat-value { color: var(--color-warning); }
.stat-label { font-size: 11px; color: var(--color-gray-500); margin-bottom: 4px; }
.stat-value { font-size: 18px; font-weight: 700; color: var(--color-gray-800); }

.payment-list { padding: 12px; }
.payment-card { background: white; border-radius: 12px; padding: 14px; margin-bottom: 10px; }
.payment-header { display: flex; align-items: center; margin-bottom: 12px; }
.payment-avatar { width: 40px; height: 40px; border-radius: 10px; margin-right: 10px; }
.payment-info { flex: 1; }
.payment-name { display: block; font-weight: 600; font-size: 15px; color: #333; }
.payment-desc { font-size: 12px; color: var(--color-gray-500); }
.payment-body { background: var(--color-gray-50); border-radius: 8px; padding: 10px; margin-bottom: 12px; }
.payment-row { display: flex; justify-content: space-between; font-size: 13px; padding: 4px 0; }
.payment-row .amount { font-weight: 600; color: var(--color-primary); }
.payment-actions { display: flex; gap: 10px; }
.payment-actions .van-button { flex: 1; }
</style>
