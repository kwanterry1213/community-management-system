<template>
  <div class="membership-page">
    <van-nav-bar title="我的會籍" />

    <!-- 會員證卡片 -->
    <div class="card-section">
      <div class="membership-card" :class="currentUser.level">
        <div class="card-pattern"></div>
        <div class="card-content">
          <div class="card-header">
            <div class="org-name">未來街坊</div>
            <span class="level-badge">{{ levelInfo.icon }} {{ levelInfo.name }}</span>
          </div>
          
          <div class="qr-section" @click="showFullQR = true">
            <div class="qr-placeholder">
              <van-icon name="qr" size="80" color="#fff" />
            </div>
            <span class="qr-hint">點擊放大</span>
          </div>

          <div class="card-info">
            <div class="member-name">{{ currentUser.name }}</div>
            <div class="member-id">{{ currentUser.id }}</div>
          </div>

          <div class="card-footer">
            <div class="validity" v-if="currentUser.level !== 'friend'">
              有效期至：{{ currentUser.expiryDate }}
            </div>
            <div class="validity" v-else>
              免費會員 · 無到期限制
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 會籍資訊 -->
    <div class="info-section">
      <van-cell-group inset title="會籍資訊">
        <van-cell title="會籍類型" :value="levelInfo.name" />
        <van-cell title="會員編號" :value="currentUser.id" />
        <van-cell title="加入日期" :value="currentUser.joinDate" />
        <van-cell title="到期日期" :value="currentUser.level !== 'friend' ? currentUser.expiryDate : '無'" />
        <van-cell title="會籍狀態">
          <template #value>
            <van-tag :type="statusInfo.type">{{ statusInfo.label }}</van-tag>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 會員權益 -->
    <div class="benefits-section">
      <van-cell-group inset title="會員權益">
        <div class="benefits-list">
          <div v-for="(benefit, index) in currentBenefits" :key="index" class="benefit-item">
            <van-icon :name="benefit.icon" size="20" :color="benefit.available ? '#38a169' : '#cbd5e0'" />
            <span :class="{ disabled: !benefit.available }">{{ benefit.text }}</span>
            <van-icon v-if="benefit.available" name="success" size="16" color="#38a169" />
            <van-icon v-else name="cross" size="16" color="#cbd5e0" />
          </div>
        </div>
      </van-cell-group>
    </div>

    <!-- 繳費記錄 -->
    <div class="payment-section" v-if="currentUser.level !== 'friend'">
      <van-cell-group inset title="繳費記錄">
        <van-cell 
          v-for="payment in paymentHistory" 
          :key="payment.id"
          :title="payment.description"
          :label="`${payment.date} · ${paymentMethodLabels[payment.method]}`"
        >
          <template #value>
            <div class="payment-cell-value">
              <span class="payment-amount">MOP$ {{ payment.amount }}</span>
              <van-tag :type="payment.status === 'paid' ? 'success' : 'warning'" plain>
                {{ paymentStatusLabels[payment.status] }}
              </van-tag>
            </div>
          </template>
        </van-cell>
        <van-cell v-if="paymentHistory.length === 0" title="暫無繳費記錄" />
      </van-cell-group>
    </div>

    <!-- 操作按鈕 -->
    <div class="action-section">
      <van-button 
        v-if="currentUser.level === 'friend'"
        type="primary" 
        block 
        round
        size="large"
        @click="showUpgradeOptions"
      >
        <van-icon name="star" /> 升級成為正式會員
      </van-button>
      <van-button 
        v-else-if="needsRenewal"
        type="warning" 
        block 
        round
        size="large"
        @click="showRenewOptions"
      >
        <van-icon name="replay" /> 立即續費
      </van-button>
      <van-button 
        v-else
        type="primary" 
        plain 
        block 
        round
        size="large"
        @click="showRenewOptions"
      >
        提前續費
      </van-button>
    </div>

    <!-- QR Code 全屏彈窗 -->
    <van-popup v-model:show="showFullQR" round style="padding: 30px; text-align: center;">
      <div class="qr-full">
        <div class="qr-code-large">
          <van-icon name="qr" size="200" color="#1a365d" />
        </div>
        <div class="qr-info">
          <div class="qr-level">{{ levelInfo.icon }} {{ levelInfo.name }}</div>
          <div class="qr-name">{{ currentUser.name }}</div>
          <div class="qr-id">{{ currentUser.id }}</div>
        </div>
      </div>
    </van-popup>

    <!-- 升級/續費選項 -->
    <van-action-sheet 
      v-model:show="showOptions" 
      :title="optionsTitle"
      :actions="membershipOptions"
      @select="onSelectOption"
    />

    <!-- 付款方式選擇彈窗 -->
    <van-popup v-model:show="showPaymentPopup" position="bottom" round :style="{ minHeight: '45%' }">
      <div class="payment-popup">
        <div class="payment-popup-header">
          <h3>選擇付款方式</h3>
          <van-icon name="cross" @click="showPaymentPopup = false" />
        </div>

        <div class="payment-summary">
          <div class="payment-summary-row">
            <span>方案</span>
            <span>{{ pendingPlan?.name }}</span>
          </div>
          <div class="payment-summary-row total">
            <span>費用</span>
            <span class="amount">{{ pendingPlan?.price }}</span>
          </div>
        </div>

        <div class="payment-methods">
          <div 
            v-for="method in paymentMethods" 
            :key="method.value"
            :class="['payment-method-item', { selected: selectedPaymentMethod === method.value }]"
            @click="selectedPaymentMethod = method.value"
          >
            <div class="method-left">
              <van-icon :name="method.icon" size="24" :color="method.color" />
              <div class="method-info">
                <span class="method-name">{{ method.name }}</span>
                <span class="method-desc">{{ method.desc }}</span>
              </div>
            </div>
            <van-icon v-if="selectedPaymentMethod === method.value" name="success" color="#38a169" size="20" />
          </div>
        </div>

        <div class="payment-popup-footer">
          <van-button 
            type="primary" 
            block 
            round 
            size="large"
            :disabled="!selectedPaymentMethod"
            @click="confirmMembershipPayment"
          >
            確認付款
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { showToast } from 'vant'

const currentUser = ref({
  id: 'M-2024-0158',
  name: '陳大明',
  level: 'committee', // committee | citizen | friend
  joinDate: '2022-06-15',
  expiryDate: '2026-06-30',
  status: 'active' // active | expiring | expired
})

const levelInfo = computed(() => {
  const levels = {
    committee: { name: '未來街坊圈圈委', icon: '⭐⭐⭐', color: '#d69e2e' },
    citizen: { name: '未來街坊圈圈民', icon: '⭐⭐', color: '#3182ce' },
    friend: { name: '未來街坊圈圈友', icon: '⭐', color: '#718096' }
  }
  return levels[currentUser.value.level]
})

const statusInfo = computed(() => {
  const statuses = {
    active: { label: '有效', type: 'success' },
    expiring: { label: '即將到期', type: 'warning' },
    expired: { label: '已過期', type: 'danger' }
  }
  return statuses[currentUser.value.status]
})

const needsRenewal = computed(() => {
  return currentUser.value.status === 'expiring' || currentUser.value.status === 'expired'
})

const benefits = {
  committee: [
    { icon: 'todo-list-o', text: '參與決策投票', available: true },
    { icon: 'friends-o', text: '出席理監事會議', available: true },
    { icon: 'gift-o', text: '專屬會員福利', available: true },
    { icon: 'calendar-o', text: '優先活動報名', available: true },
    { icon: 'coupon-o', text: '合作商家折扣', available: true }
  ],
  citizen: [
    { icon: 'todo-list-o', text: '參與決策投票', available: false },
    { icon: 'friends-o', text: '出席會員大會', available: true },
    { icon: 'gift-o', text: '專屬會員福利', available: true },
    { icon: 'calendar-o', text: '優先活動報名', available: true },
    { icon: 'coupon-o', text: '合作商家折扣', available: true }
  ],
  friend: [
    { icon: 'todo-list-o', text: '參與決策投票', available: false },
    { icon: 'friends-o', text: '出席一般會議', available: true },
    { icon: 'gift-o', text: '專屬會員福利', available: false },
    { icon: 'calendar-o', text: '查看活動資訊', available: true },
    { icon: 'coupon-o', text: '合作商家折扣', available: false }
  ]
}

const currentBenefits = computed(() => benefits[currentUser.value.level])

const paymentStatusLabels = {
  paid: '已付款',
  pending: '待付款',
  refunded: '已退款'
}

const paymentMethodLabels = {
  mpay: 'MPay 澳門錢包',
  alipay: '支付寶 (澳門)',
  wechat: '微信支付',
  bank: '銀行轉賬',
  cash: '現金'
}

const paymentMethods = [
  { value: 'bank', name: '銀行轉賬', desc: '1-2個工作天確認', icon: 'bank-card-o', color: '#d69e2e' },
  { value: 'cash', name: '現金', desc: '到場繳付', icon: 'cash-back-record', color: '#718096' }
]

const paymentHistory = ref([
  { id: 1, description: '2025年度會費（一年）', date: '2025-01-15', amount: 500, status: 'paid', method: 'bank' },
  { id: 2, description: '2024年度會費（一年）', date: '2024-01-20', amount: 500, status: 'paid', method: 'cash' },
  { id: 3, description: '2023年度會費（一年）', date: '2023-01-18', amount: 500, status: 'paid', method: 'bank' }
])

const showFullQR = ref(false)
const showOptions = ref(false)
const optionsTitle = ref('')
const showPaymentPopup = ref(false)
const pendingPlan = ref(null)
const selectedPaymentMethod = ref('')

const membershipOptions = ref([])

const showUpgradeOptions = () => {
  optionsTitle.value = '選擇會籍方案'
  membershipOptions.value = [
    { name: '半年會籍', subname: 'MOP$ 300 · 享會員福利', value: 'halfYear', price: 'MOP$ 300' },
    { name: '一年會籍', subname: 'MOP$ 500 · 更優惠', value: 'oneYear', price: 'MOP$ 500' }
  ]
  showOptions.value = true
}

const showRenewOptions = () => {
  optionsTitle.value = '選擇續費方案'
  membershipOptions.value = [
    { name: '續費半年', subname: 'MOP$ 300', value: 'halfYear', price: 'MOP$ 300' },
    { name: '續費一年', subname: 'MOP$ 500 · 更優惠', value: 'oneYear', price: 'MOP$ 500' }
  ]
  showOptions.value = true
}

const onSelectOption = (option) => {
  // 選完方案 → 打開付款方式選擇
  showOptions.value = false
  pendingPlan.value = option
  selectedPaymentMethod.value = ''
  showPaymentPopup.value = true
}

const confirmMembershipPayment = () => {
  if (!selectedPaymentMethod.value || !pendingPlan.value) return

  const isInstant = !['bank', 'cash'].includes(selectedPaymentMethod.value)
  const amount = pendingPlan.value.value === 'oneYear' ? 500 : 300

  // 新增繳費記錄
  paymentHistory.value.unshift({
    id: Date.now(),
    description: pendingPlan.value.name,
    date: new Date().toISOString().split('T')[0],
    amount,
    status: isInstant ? 'paid' : 'pending',
    method: selectedPaymentMethod.value
  })

  if (isInstant) {
    showToast({ type: 'success', message: '付款成功！會籍已更新' })
  } else {
    showToast({ type: 'success', message: '已提交，請完成付款' })
  }

  showPaymentPopup.value = false
  pendingPlan.value = null
  selectedPaymentMethod.value = ''
}
</script>

<style scoped>
.membership-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 90px;
}

.card-section {
  padding: 16px;
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
}

.membership-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 1.6;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.membership-card.committee {
  background: linear-gradient(135deg, #d69e2e 0%, #b7791f 100%);
}

.membership-card.citizen {
  background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
}

.membership-card.friend {
  background: linear-gradient(135deg, #718096 0%, #4a5568 100%);
}

.card-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background-image: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 20px,
    rgba(255,255,255,0.1) 20px,
    rgba(255,255,255,0.1) 40px
  );
}

.card-content {
  position: relative;
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  color: #fff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.org-name {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 2px;
}

.level-badge {
  font-size: 11px;
  background: rgba(255,255,255,0.2);
  padding: 4px 10px;
  border-radius: 20px;
}

.qr-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.qr-placeholder {
  width: 100px;
  height: 100px;
  background: rgba(255,255,255,0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-hint {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 6px;
}

.card-info {
  text-align: center;
  margin-bottom: 8px;
}

.card-info .member-name {
  font-size: 20px;
  font-weight: 700;
}

.card-info .member-id {
  font-size: 12px;
  opacity: 0.8;
}

.card-footer {
  text-align: center;
}

.validity {
  font-size: 12px;
  opacity: 0.9;
}

/* 權益列表 */
.benefits-list {
  padding: 12px 16px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
}

.benefit-item:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.benefit-item span {
  flex: 1;
  font-size: 14px;
  color: #1a202c;
}

.benefit-item span.disabled {
  color: #a0aec0;
  text-decoration: line-through;
}

/* 繳費記錄 */
.payment-cell-value {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.payment-amount {
  font-weight: 600;
  color: #38a169;
}

/* 操作區 */
.action-section {
  padding: 16px;
}

/* QR全屏 */
.qr-full {
  text-align: center;
}

.qr-code-large {
  width: 220px;
  height: 220px;
  margin: 0 auto 20px;
  background: #f7fafc;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-level {
  font-size: 14px;
  color: #718096;
  margin-bottom: 4px;
}

.qr-name {
  font-size: 22px;
  font-weight: 700;
  color: #1a202c;
}

.qr-id {
  font-size: 14px;
  color: #718096;
  margin-top: 4px;
}

/* 付款彈窗 */
.payment-popup {
  padding: 16px;
}

.payment-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.payment-popup-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.payment-summary {
  background: #f7fafc;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 20px;
}

.payment-summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #4a5568;
  padding: 4px 0;
}

.payment-summary-row.total {
  margin-top: 8px;
  padding-top: 10px;
  border-top: 1px solid #e2e8f0;
  font-weight: 600;
  color: #1a202c;
}

.payment-summary-row .amount {
  color: #e53e3e;
  font-size: 18px;
  font-weight: 700;
}

.payment-methods {
  margin-bottom: 20px;
}

.payment-method-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-method-item.selected {
  border-color: #3182ce;
  background: #ebf8ff;
}

.method-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.method-info {
  display: flex;
  flex-direction: column;
}

.method-name {
  font-size: 15px;
  font-weight: 500;
  color: #1a202c;
}

.method-desc {
  font-size: 12px;
  color: #718096;
}

.payment-popup-footer {
  padding-bottom: 16px;
}
</style>
