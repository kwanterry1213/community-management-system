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

    <!-- 操作列 -->
    <div class="actions-row">
      <van-button type="primary" size="small" icon="plus" @click="openCreate">新增繳費</van-button>
      <van-button type="default" size="small" icon="clock-o" @click="runDueJob">生成到期帳單</van-button>
      <van-button type="success" size="small" icon="down" @click="exportCSV">導出 CSV</van-button>
    </div>

    <!-- 搜尋篩選 -->
    <div class="filter-row">
      <van-field v-model="searchKeyword" placeholder="搜尋會員名 / 描述" clearable class="filter-input" />
      <van-field v-model="filterDateStart" placeholder="開始日期" class="filter-date" />
      <van-field v-model="filterDateEnd" placeholder="結束日期" class="filter-date" />
    </div>

    <!-- 分類標籤 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="全部" name="all" />
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
            <div v-if="item.note" class="payment-row"><span>備註</span><span class="note-text">{{ item.note }}</span></div>
          </div>
          <div class="payment-actions">
            <van-button v-if="item.status === 'pending'" size="small" type="success" icon="success" @click="confirmPayment(item)">確認收款</van-button>
            <van-button v-if="item.status === 'paid'" size="small" type="warning" plain icon="revoke" @click="revertPayment(item)">退回待繳</van-button>
            <van-button size="small" plain icon="edit" @click="openEdit(item)">編輯</van-button>
            <van-button size="small" plain type="danger" icon="delete-o" @click="deletePayment(item)">刪除</van-button>
          </div>
        </div>
      </div>
    </van-pull-refresh>

    <!-- 新增 / 編輯彈出表單 -->
    <van-popup v-model:show="showForm" position="bottom" :style="{ height: '85%' }" round>
      <div class="form-header">
        <span>{{ isEditing ? '編輯繳費記錄' : '新增繳費' }}</span>
        <van-icon name="cross" @click="showForm = false" />
      </div>
      <van-form @submit="submitForm" class="form-body">
        <van-field
          v-model="formData.memberLabel"
          label="會員"
          placeholder="選擇會員"
          readonly
          is-link
          @click="showMemberPicker = true"
          required
        />
        <van-field v-model="formData.description" label="描述" placeholder="例如：會費 / 活動費" required />
        <van-field v-model="formData.amount" type="number" label="金額" placeholder="輸入金額" required />
        <van-field v-model="formData.due_date" label="繳費期限" placeholder="YYYY-MM-DD" />
        <van-field
          v-model="formData.typeLabel"
          label="分類"
          placeholder="選擇分類"
          readonly
          is-link
          @click="showTypePicker = true"
        />
        <van-field
          v-model="formData.methodLabel"
          label="支付方式"
          placeholder="選擇支付方式"
          readonly
          is-link
          @click="showMethodPicker = true"
        />
        <van-field
          v-model="formData.statusLabel"
          label="狀態"
          placeholder="選擇狀態"
          readonly
          is-link
          @click="showStatusPicker = true"
        />
        <van-field v-model="formData.note" label="備註" type="textarea" placeholder="管理員備註（選填）" rows="2" autosize />
        <div style="padding: 12px;">
          <van-button round block type="primary" native-type="submit">{{ isEditing ? '儲存修改' : '建立' }}</van-button>
          <van-button round block plain color="#999" @click="showForm = false" style="margin-top:8px;">取消</van-button>
        </div>
      </van-form>
    </van-popup>

    <!-- 會員選擇器 -->
    <van-popup v-model:show="showMemberPicker" position="bottom" round>
      <van-picker
        :columns="memberColumns"
        @confirm="onMemberConfirm"
        @cancel="showMemberPicker = false"
        title="選擇會員"
      />
    </van-popup>

    <!-- 分類選擇器 -->
    <van-popup v-model:show="showTypePicker" position="bottom" round>
      <van-picker
        :columns="typeColumns"
        @confirm="onTypeConfirm"
        @cancel="showTypePicker = false"
        title="選擇分類"
      />
    </van-popup>

    <!-- 支付方式選擇器 -->
    <van-popup v-model:show="showMethodPicker" position="bottom" round>
      <van-picker
        :columns="methodColumns"
        @confirm="onMethodConfirm"
        @cancel="showMethodPicker = false"
        title="選擇支付方式"
      />
    </van-popup>

    <!-- 狀態選擇器 -->
    <van-popup v-model:show="showStatusPicker" position="bottom" round>
      <van-picker
        :columns="statusColumns"
        @confirm="onStatusConfirm"
        @cancel="showStatusPicker = false"
        title="選擇狀態"
      />
    </van-popup>

    <!-- 確認收款支付方式選擇器 -->
    <van-action-sheet
      v-model:show="showPayMethodSheet"
      :actions="payMethodActions"
      title="選擇支付方式"
      cancel-text="取消"
      @select="onPayMethodSelect"
      @cancel="showPayMethodSheet = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { paymentApi, maintenanceApi, userApi } from '@/services/api'
import { showToast, showDialog } from 'vant'

const activeTab = ref('all')
const refreshing = ref(false)
const payments = ref([])
const members = ref([])
const paymentStats = ref({
  receivableThisMonth: 0,
  paidThisMonth: 0,
  totalPending: 0,
  totalOverdue: 0,
})

const searchKeyword = ref('')
const filterDateStart = ref('')
const filterDateEnd = ref('')

const showForm = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const showMemberPicker = ref(false)
const showTypePicker = ref(false)
const showMethodPicker = ref(false)
const showStatusPicker = ref(false)

const defaultFormData = {
  user_id: '',
  memberLabel: '',
  description: '',
  amount: '',
  due_date: '',
  related_type: '',
  typeLabel: '',
  method: '',
  methodLabel: '',
  status: 'pending',
  statusLabel: '待繳費',
  note: '',
}
const formData = reactive({ ...defaultFormData })

const typeColumns = [
  { text: '會費', value: 'membership' },
  { text: '活動費', value: 'event' },
  { text: '其他', value: 'other' },
]
const methodColumns = [
  { text: '現金', value: '現金' },
  { text: '轉帳', value: '轉帳' },
  { text: '微信', value: '微信' },
  { text: '其他', value: '其他' },
]
const statusColumns = [
  { text: '待繳費', value: 'pending' },
  { text: '已繳費', value: 'paid' },
]
const typeMap = { membership: '會費', event: '活動費', other: '其他' }
const statusMap = { pending: '待繳費', paid: '已繳費' }
const methodMap = { '現金': '現金', '轉帳': '轉帳', '微信': '微信', '其他': '其他' }

const memberColumns = computed(() =>
  members.value.map((m) => ({ text: `${m.username} (ID:${m.id})`, value: m.id }))
)

const formatCurrency = (value) => {
  if (typeof value !== 'number') return '$--'
  return `$${value.toLocaleString('en-US')}`
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const pendingCount = computed(() => {
  const now = new Date()
  return payments.value.filter((p) => {
    const isOverdue = p.status === 'pending' && p.due_date && new Date(p.due_date) < now
    return p.status === 'pending' && !isOverdue
  }).length
})

const overdueCount = computed(() => {
  const now = new Date()
  return payments.value.filter(
    (p) => p.status === 'pending' && p.due_date && new Date(p.due_date) < now
  ).length
})

const paymentList = computed(() => {
  const now = new Date()
  let list = payments.value

  if (activeTab.value !== 'all') {
    list = list.filter((p) => {
      const isOverdue = p.status === 'pending' && p.due_date && new Date(p.due_date) < now
      if (activeTab.value === 'pending') return p.status === 'pending' && !isOverdue
      if (activeTab.value === 'paid') return p.status === 'paid'
      if (activeTab.value === 'overdue') return isOverdue
      return true
    })
  }

  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    list = list.filter(
      (p) =>
        (p.username || '').toLowerCase().includes(kw) ||
        (p.description || '').toLowerCase().includes(kw)
    )
  }

  if (filterDateStart.value) {
    list = list.filter((p) => p.created_at >= filterDateStart.value)
  }
  if (filterDateEnd.value) {
    list = list.filter((p) => p.created_at <= filterDateEnd.value + 'T23:59:59')
  }

  return list.map((p) => ({
    ...p,
    avatar:
      p.profile_picture ||
      `https://ui-avatars.com/api/?name=${encodeURIComponent(p.username || 'User')}&background=random&color=fff`,
    statusText: getStatusText(p.status, p.due_date),
    statusClass: getStatusClass(p.status, p.due_date),
    membershipLabel: typeMap[p.related_type] || '其他',
  }))
})

const getStatusText = (status, dueDate) => {
  const now = new Date()
  if (status === 'pending' && dueDate && new Date(dueDate) < now) return '逾期'
  return statusMap[status] || status
}

const getStatusClass = (status, dueDate) => {
  const now = new Date()
  if (status === 'pending' && dueDate && new Date(dueDate) < now) return 'overdue'
  if (status === 'paid') return 'paid'
  return 'pending'
}

// --- Data fetching ---
const fetchMembers = async () => {
  try {
    members.value = await userApi.listUsers()
  } catch (e) {
    console.error('Failed to fetch members:', e)
  }
}

const fetchPayments = async () => {
  try {
    const res = await paymentApi.list({ community_id: 1 })
    payments.value = res
  } catch (error) {
    showToast('無法獲取繳費列表')
  } finally {
    refreshing.value = false
  }
}

const fetchPaymentStats = async () => {
  try {
    const stats = await paymentApi.getStats({ community_id: 1 })
    paymentStats.value = stats
  } catch (error) {
    showToast('無法獲取統計數據')
  }
}

const onRefresh = () => {
  fetchPayments()
  fetchPaymentStats()
}

// --- Picker callbacks ---
const onMemberConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  formData.user_id = opt.value
  formData.memberLabel = opt.text
  showMemberPicker.value = false
}

const onTypeConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  formData.related_type = opt.value
  formData.typeLabel = opt.text
  showTypePicker.value = false
}

const onMethodConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  formData.method = opt.value
  formData.methodLabel = opt.text
  showMethodPicker.value = false
}

const onStatusConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  formData.status = opt.value
  formData.statusLabel = opt.text
  showStatusPicker.value = false
}

// --- Form actions ---
const resetForm = () => {
  Object.assign(formData, { ...defaultFormData })
  isEditing.value = false
  editingId.value = null
}

const openCreate = () => {
  resetForm()
  showForm.value = true
}

const openEdit = (item) => {
  isEditing.value = true
  editingId.value = item.id
  const member = members.value.find((m) => m.id === item.user_id)
  Object.assign(formData, {
    user_id: item.user_id,
    memberLabel: member ? `${member.username} (ID:${member.id})` : `ID:${item.user_id}`,
    description: item.description || '',
    amount: String(item.amount ?? ''),
    due_date: item.due_date ? item.due_date.split('T')[0] : '',
    related_type: item.related_type || '',
    typeLabel: typeMap[item.related_type] || item.related_type || '',
    method: item.method || '',
    methodLabel: item.method || '',
    status: item.status || 'pending',
    statusLabel: statusMap[item.status] || item.status || '',
    note: item.note || '',
  })
  showForm.value = true
}

const submitForm = async () => {
  if (!formData.user_id || !formData.amount || !formData.description) {
    showToast('請填寫會員、金額與描述')
    return
  }
  try {
    const payload = {
      user_id: Number(formData.user_id),
      description: formData.description,
      amount: parseFloat(formData.amount),
      due_date: formData.due_date || null,
      related_type: formData.related_type || null,
      method: formData.method || null,
      status: formData.status,
      note: formData.note || null,
    }
    if (isEditing.value) {
      await paymentApi.update(editingId.value, payload)
      showToast('修改成功')
    } else {
      await paymentApi.create(payload)
      showToast('新增成功')
    }
    showForm.value = false
    resetForm()
    onRefresh()
  } catch (e) {
    showToast(isEditing.value ? '修改失敗' : '新增失敗')
  }
}

// --- Payment actions ---
const showPayMethodSheet = ref(false)
const payMethodActions = [{ name: '現金' }, { name: '轉帳' }, { name: '微信' }, { name: '其他' }]
const confirmingItem = ref(null)

const confirmPayment = (item) => {
  confirmingItem.value = item
  showPayMethodSheet.value = true
}

const onPayMethodSelect = async (action) => {
  showPayMethodSheet.value = false
  if (!confirmingItem.value) return
  try {
    await paymentApi.update(confirmingItem.value.id, { status: 'paid', method: action.name })
    showToast('收款成功')
    onRefresh()
  } catch (err) {
    showToast('操作失敗')
  }
  confirmingItem.value = null
}

const revertPayment = async (item) => {
  try {
    await showDialog({ title: '確認退回', message: `確定將此筆 $${item.amount} 退回「待繳費」？` })
    await paymentApi.update(item.id, { status: 'pending' })
    showToast('已退回待繳費')
    onRefresh()
  } catch (_) {}
}

const deletePayment = async (item) => {
  try {
    await showDialog({
      title: '確認刪除',
      message: `確定刪除「${item.description}」($${item.amount})？此操作不可復原。`,
    })
    await paymentApi.delete(item.id)
    showToast('已刪除')
    onRefresh()
  } catch (_) {}
}

const runDueJob = async () => {
  try {
    await maintenanceApi.generateDuePayments({ community_id: 1 })
    showToast('已生成到期帳單')
    onRefresh()
  } catch (err) {
    showToast('操作失敗')
  }
}

const exportCSV = () => {
  const params = { community_id: 1 }
  if (activeTab.value === 'paid') params.status = 'paid'
  else if (activeTab.value === 'pending') params.status = 'pending'
  if (filterDateStart.value) params.start = filterDateStart.value
  if (filterDateEnd.value) params.end = filterDateEnd.value
  paymentApi.exportCSV(params)
}

onMounted(() => {
  fetchMembers()
  onRefresh()
})
</script>

<style scoped>
.payments-page {
  padding: 0;
  background: var(--color-gray-100);
}

.stats-row {
  display: flex;
  gap: 10px;
  padding: 12px;
}
.stat-card {
  flex: 1;
  background: white;
  border-radius: 10px;
  padding: 12px;
  text-align: center;
}
.stat-card.green .stat-value { color: var(--color-success); }
.stat-card.orange .stat-value { color: var(--color-warning); }
.stat-card.red .stat-value { color: var(--color-danger); }
.stat-label { font-size: 11px; color: var(--color-gray-500); margin-bottom: 4px; }
.stat-value { font-size: 18px; font-weight: 700; color: var(--color-gray-800); }

.actions-row {
  padding: 0 12px 8px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.filter-row {
  display: flex;
  gap: 6px;
  padding: 0 12px 8px;
}
.filter-input { flex: 2; }
.filter-date { flex: 1; }
.filter-row .van-field {
  background: white;
  border-radius: 8px;
  padding: 4px 8px;
}

.payment-list { padding: 12px; }
.payment-card {
  background: white;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
}
.payment-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.payment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  margin-right: 10px;
  object-fit: cover;
}
.payment-info { flex: 1; }
.payment-name { display: block; font-weight: 600; font-size: 15px; color: #333; }
.payment-desc { font-size: 12px; color: var(--color-gray-500); }
.payment-body {
  background: var(--color-gray-50);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 12px;
}
.payment-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}
.payment-row .amount { font-weight: 600; color: var(--color-primary); }
.note-text { color: var(--color-gray-600); font-style: italic; max-width: 60%; text-align: right; }

.payment-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.payment-actions .van-button { flex: none; }

.status-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.status-tag.pending { background: #fff3e0; color: #e65100; }
.status-tag.paid { background: #e8f5e9; color: #2e7d32; }
.status-tag.overdue { background: #ffebee; color: #c62828; }

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
}
.form-body {
  padding-bottom: 24px;
  overflow-y: auto;
  max-height: calc(85vh - 60px);
}
</style>
