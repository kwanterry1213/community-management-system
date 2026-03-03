<template>
  <div class="page payments-page">
    <van-nav-bar title="繳費管理" />

    <!-- 收款統計 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">本月應收</div>
        <div class="stat-value">{{ formatCurrency(paymentStats.receivableThisMonth) }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">已收款</div>
        <div class="stat-value">{{ formatCurrency(paymentStats.paidThisMonth) }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">待收款</div>
        <div class="stat-value">{{ formatCurrency(paymentStats.totalPending) }}</div>
      </div>
      <div class="stat-card red">
        <div class="stat-label">逾期未繳</div>
        <div class="stat-value">{{ formatCurrency(paymentStats.totalOverdue) }}</div>
      </div>
    </div>
    <!-- 新增繳費按鈕 & 生成到期帳單 -->
    <div class="actions-row" style="padding: 12px; text-align: right; display:flex; gap:8px; justify-content:flex-end;">
      <van-button type="primary" size="small" @click="showCreate = true">+ 新增繳費</van-button>
      <van-button type="info" size="small" @click="runDueJob">生成到期帳單</van-button>
    </div>

    <!-- 分類標籤 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="待繳費" name="pending" :badge="pendingCount > 0 ? pendingCount : ''" />
      <van-tab title="已繳費" name="paid" />
      <van-tab title="逾期未繳" name="overdue" :badge="overdueCount > 0 ? overdueCount : ''" />
    </van-tabs>

    <!-- 繳費列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <div class="payment-list">
        <div v-if="paymentList.length === 0" class="van-empty">
            <van-empty description="暫無記錄" />
        </div>
        <div v-else v-for="item in paymentList" :key="item.id" class="payment-card">
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
            <div class="payment-row"><span>建立時間</span><span>{{ formatDate(item.created_at) }}</span></div>
            <div v-if="item.due_date" class="payment-row"><span>繳費期限</span><span>{{ formatDate(item.due_date) }}</span></div>
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
    <!-- 新增繳費彈出表單 -->
    <van-popup v-model:show="showCreate" position="bottom" :style="{height: 'auto'}">
      <van-form @submit="createPayment">
        <van-field v-model="newPayment.user_id" label="會員ID" placeholder="輸入會員編號" required />
        <van-field v-model="newPayment.description" label="描述" placeholder="例如：會費或活動費" required />
        <van-field v-model="newPayment.amount" type="number" label="金額" placeholder="輸入金額" required />
        <van-field v-model="newPayment.due_date" label="繳費期限" placeholder="YYYY-MM-DD" />
        <van-field v-model="newPayment.related_type" label="分類" placeholder="event / membership / other" />
        <div style="padding: 12px;">
          <van-button round block type="primary" native-type="submit">建立</van-button>
          <van-button round block plain color="#999" @click="showCreate = false" style="margin-top:8px;">取消</van-button>
        </div>
      </van-form>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { paymentApi, maintenanceApi } from '@/services/api'
import { showToast, showDialog, showActionSheet } from 'vant'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const activeTab = ref('pending')
const refreshing = ref(false)
const payments = ref([])
const paymentStats = ref({
    receivableThisMonth: 0,
    paidThisMonth: 0,
    totalPending: 0,
    totalOverdue: 0
})

// create form state
const showCreate = ref(false)
const newPayment = reactive({
    user_id: '',
    description: '',
    amount: '',
    due_date: '',
    related_type: '',
    related_id: '',
    method: '',
    status: 'pending',
})

const formatCurrency = (value) => {
    if (typeof value !== 'number') {
        return '$--'
    }
    return `$${value.toLocaleString('en-US')}`
}

const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
}

const pendingCount = computed(() => {
    const now = new Date();
    return payments.value.filter(p => {
        const isOverdue = p.status === 'pending' && p.due_date && new Date(p.due_date) < now;
        return p.status === 'pending' && !isOverdue;
    }).length;
});

const overdueCount = computed(() => {
    const now = new Date();
    return payments.value.filter(p => p.status === 'pending' && p.due_date && new Date(p.due_date) < now).length;
});

const paymentList = computed(() => {
  const now = new Date();
  return payments.value.filter(p => {
    const isOverdue = p.status === 'pending' && p.due_date && new Date(p.due_date) < now;
    if (activeTab.value === 'pending') return p.status === 'pending' && !isOverdue;
    if (activeTab.value === 'paid') return p.status === 'paid';
    if (activeTab.value === 'overdue') return isOverdue;
    return true;
  }).map(p => ({
    ...p,
    avatar: p.profile_picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(p.username || 'User')}&background=random&color=fff`,
    statusText: getStatusText(p.status, p.due_date),
    statusClass: getStatusClass(p.status, p.due_date),
    membershipLabel: p.related_type === 'event' ? '活動費' : '會費'
  }))
})

const getStatusText = (status, dueDate) => {
    const now = new Date();
    const isOverdue = status === 'pending' && dueDate && new Date(dueDate) < now;
    if (isOverdue) return '逾期';
    const map = { pending: '待繳費', paid: '已繳費' };
    return map[status] || status;
}

const getStatusClass = (status, dueDate) => {
    const now = new Date();
    const isOverdue = status === 'pending' && dueDate && new Date(dueDate) < now;
    if (isOverdue) return 'overdue';
    if (status === 'paid') return 'paid';
    return 'pending';
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

const fetchPaymentStats = async () => {
    try {
        const stats = await paymentApi.getStats({ community_id: 1 });
        paymentStats.value = stats;
    } catch (error) {
        console.error("Failed to fetch payment stats:", error);
        showToast('無法獲取統計數據');
    }
}

const runDueJob = async () => {
    try {
        await maintenanceApi.generateDuePayments({ community_id: 1 });
        showToast('已生成到期帳單');
        onRefresh();
    } catch (err) {
        showToast('操作失敗');
    }
}

const onRefresh = () => {
    fetchPayments()
    fetchPaymentStats()
}

const createPayment = async () => {
    // simple validation
    if (!newPayment.user_id || !newPayment.amount || !newPayment.description) {
        showToast('請填寫會員、金額與描述')
        return
    }
    try {
        // coerce amount to number
        const payload = { ...newPayment, amount: parseFloat(newPayment.amount) }
        await paymentApi.create(payload)
        showToast('新增成功')
        showCreate.value = false
        // reset form
        Object.keys(newPayment).forEach(k => newPayment[k] = '')
        newPayment.status = 'pending'
        onRefresh()
    } catch (e) {
        showToast('新增失敗')
    }
}

const confirmPayment = async (item) => {
    // ask for payment method via action sheet
    try {
        const { name: method } = await showActionSheet({
            title: '選擇支付方式',
            options: [
                { name: '現金' },
                { name: '轉帳' },
                { name: '微信' },
                { name: '其他' },
            ],
        })
        await paymentApi.update(item.id, { status: 'paid', method })
        showToast('收款成功')
        onRefresh()
    } catch (err) {
        // cancelled or error
        if (err && err.message !== 'cancel') {
            showToast('操作失敗')
        }
    }
}

const sendReminder = (item) => {
    showToast('已發送提醒 (模擬)')
}

onMounted(() => {
    onRefresh()
})
</script>

<style scoped>
.payments-page { padding: 0; background: var(--color-gray-100); }

.stats-row { display: flex; gap: 10px; padding: 12px; }
.stat-card { flex: 1; background: white; border-radius: 10px; padding: 12px; text-align: center; }
.stat-card.green .stat-value { color: var(--color-success); }
.stat-card.orange .stat-value { color: var(--color-warning); }
.stat-card.red .stat-value { color: var(--color-danger); }
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
