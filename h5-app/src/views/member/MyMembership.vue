<template>
  <div class="membership-page">
    <van-nav-bar title="我的會籍" />
    
    <div class="card-section">
      <div class="flip-card" @click="isFlipped = !isFlipped">
        <div class="flip-card-inner" :class="{ 'is-flipped': isFlipped }">
          
          <!-- Card Front -->
          <div class="flip-card-front membership-card" :class="authStore.userLevel">
            <div class="card-bg-pattern"></div>
            <div class="card-content">
              <div class="card-header">
                <div class="org-branding">
                  <van-icon name="gem-o" size="20" style="margin-right: 6px;" />
                  <span>未來街坊圈</span>
                </div>
                <span class="level-badge">{{ authStore.levelInfo.name }}</span>
              </div>
              
              <div class="card-body">
                <div class="chip-icon">
                  <div class="chip-line"></div>
                  <div class="chip-line"></div>
                  <div class="chip-line"></div>
                  <div class="chip-line"></div>
                </div>
                <div class="card-number">{{ formatCardNumber(authStore.membership?.membership_no) }}</div>
              </div>
              
              <div class="card-footer">
                <div class="member-name">{{ displayName }}</div>
                <div class="expiry-date">
                  <div class="label">VALID THRU</div>
                  <div class="date">{{ authStore.userLevel === 'friend' ? 'PERMANENT' : (authStore.membership?.expires_at?.split('T')[0] || '—') }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Card Back -->
          <div class="flip-card-back membership-card" :class="authStore.userLevel">
            <div class="card-content back-content">
              <div class="qr-title">掃描驗證會員身份</div>
              <div class="qr-frame">
                <van-icon name="qr" size="140" color="#000" />
              </div>
              <div class="qr-hint">輕觸卡片翻轉回正面</div>
            </div>
          </div>

        </div>
      </div>
      <div class="interaction-hint">
        <van-icon name="replay" /> 輕觸卡片查看背面 QR Code
      </div>
    </div>

    <div class="info-section">
      <van-cell-group inset title="會籍資訊">
        <van-cell title="會籍類型" :value="authStore.levelInfo.name" />
        <van-cell title="會員編號" :value="authStore.membership?.membership_no || '—'" />
        <van-cell title="加入日期" :value="authStore.membership?.joined_at?.split('T')[0] || '—'" />
        <van-cell title="會籍狀態"><template #value><van-tag :type="statusType">{{ statusLabel }}</van-tag></template></van-cell>
      </van-cell-group>
    </div>

    <div class="benefits-section">
      <van-cell-group inset title="會員權益">
        <div class="benefits-list">
          <div v-for="(b, i) in currentBenefits" :key="i" class="benefit-item">
            <van-icon :name="b.icon" size="20" :color="b.available ? '#38a169' : '#cbd5e0'" />
            <span :class="{ disabled: !b.available }">{{ b.text }}</span>
            <van-icon :name="b.available ? 'success' : 'cross'" size="16" :color="b.available ? '#38a169' : '#cbd5e0'" />
          </div>
        </div>
      </van-cell-group>
    </div>

    <div class="payment-section" v-if="authStore.userLevel !== 'friend'">
      <van-cell-group inset title="繳費記錄">
        <van-cell v-for="p in paymentHistory" :key="p.id" :title="p.description" :label="`${p.created_at?.split('T')[0] || '—'} · ${p.method || '—'}`">
          <template #value>
            <span class="payment-amount">MOP$ {{ p.amount }}</span>
            <van-tag :type="p.status === 'paid' ? 'success' : 'warning'" plain>{{ p.status === 'paid' ? '已付款' : '待付款' }}</van-tag>
          </template>
        </van-cell>
        <van-cell v-if="paymentHistory.length === 0" title="暫無繳費記錄" />
      </van-cell-group>
    </div>

    <div class="action-section">
      <van-button v-if="authStore.userLevel === 'friend'" type="primary" block round size="large" @click="showUpgrade">
        <van-icon name="star" /> 升級成為正式會員
      </van-button>
      <van-button v-else type="primary" plain block round size="large" @click="showRenew">提前續費</van-button>
    </div>

    <van-popup v-model:show="showFullQR" round style="padding: 30px; text-align: center;">
      <van-icon name="qr" size="200" color="#1a365d" />
      <div style="margin-top: 16px; font-size: 18px; font-weight: 700;">{{ displayName }}</div>
    </van-popup>

    <van-action-sheet v-model:show="showOptions" :title="optionsTitle" :actions="membershipOptions" @select="onSelectOption" />

    <van-popup v-model:show="showPaymentPopup" position="bottom" round :style="{ minHeight: '40%' }">
      <div style="padding: 16px;">
        <h3 style="margin: 0 0 16px;">選擇付款方式</h3>
        <div v-for="m in payMethods" :key="m.value" :class="['pay-method', { selected: selMethod === m.value }]" @click="selMethod = m.value">
          <van-icon :name="m.icon" size="24" :color="m.color" />
          <span style="flex: 1; margin-left: 12px;">{{ m.name }}</span>
          <van-icon v-if="selMethod === m.value" name="success" color="#38a169" />
        </div>
        <van-button type="primary" block round size="large" style="margin-top: 20px;" :disabled="!selMethod" @click="confirmPay">確認付款</van-button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'
import { paymentApi } from '@/services/api'

const authStore = useAuthStore()
const displayName = computed(() => authStore.currentUser?.username || '會員')
const statusLabel = computed(() => { const s = authStore.membership?.status; return s === 'active' ? '有效' : s === 'expired' ? '已過期' : '待審核' })
const statusType = computed(() => { const s = authStore.membership?.status; return s === 'active' ? 'success' : s === 'expired' ? 'danger' : 'warning' })

const benefitsMap = {
  committee: [
    { icon: 'todo-list-o', text: '參與決策投票', available: true },
    { icon: 'friends-o', text: '出席理監事會議', available: true },
    { icon: 'gift-o', text: '專屬會員福利', available: true },
    { icon: 'calendar-o', text: '優先活動報名', available: true },
  ],
  citizen: [
    { icon: 'todo-list-o', text: '參與決策投票', available: false },
    { icon: 'friends-o', text: '出席會員大會', available: true },
    { icon: 'gift-o', text: '專屬會員福利', available: true },
    { icon: 'calendar-o', text: '優先活動報名', available: true },
  ],
  friend: [
    { icon: 'todo-list-o', text: '參與決策投票', available: false },
    { icon: 'friends-o', text: '出席一般會議', available: true },
    { icon: 'gift-o', text: '專屬會員福利', available: false },
    { icon: 'calendar-o', text: '查看活動資訊', available: true },
  ]
}
const currentBenefits = computed(() => benefitsMap[authStore.userLevel])

const payMethods = [
  { value: 'bank', name: '銀行轉賬', icon: 'bank-card-o', color: '#d69e2e' },
  { value: 'cash', name: '現金', icon: 'cash-back-record', color: '#718096' },
]

const paymentHistory = ref([])
const showFullQR = ref(false)
const showOptions = ref(false)
const optionsTitle = ref('')
const membershipOptions = ref([])
const showPaymentPopup = ref(false)
const pendingPlan = ref(null)
const selMethod = ref('')
const isFlipped = ref(false)

const formatCardNumber = (no) => {
  if (!no) return 'NO. ————'
  // Simple format: grouping by 4 if needed, or just return
  return `NO. ${no}`
}

const showUpgrade = () => {
  optionsTitle.value = '選擇會籍方案'
  membershipOptions.value = [
    { name: '半年會籍', subname: 'MOP$ 300', value: 'half', amount: 300 },
    { name: '一年會籍', subname: 'MOP$ 500', value: 'year', amount: 500 },
  ]
  showOptions.value = true
}
const showRenew = () => {
  optionsTitle.value = '選擇續費方案'
  membershipOptions.value = [
    { name: '續費半年', subname: 'MOP$ 300', value: 'half', amount: 300 },
    { name: '續費一年', subname: 'MOP$ 500', value: 'year', amount: 500 },
  ]
  showOptions.value = true
}
const onSelectOption = (opt) => { showOptions.value = false; pendingPlan.value = opt; selMethod.value = ''; showPaymentPopup.value = true }

const confirmPay = async () => {
  if (!selMethod.value || !pendingPlan.value) return
  try {
    await paymentApi.create({
      user_id: authStore.userId,
      community_id: authStore.membership?.community_id || 1,
      description: pendingPlan.value.name,
      amount: pendingPlan.value.amount,
      method: selMethod.value,
      status: 'pending',
      related_type: 'membership',
    })
    showToast({ type: 'success', message: '已提交，請完成付款' })
    await fetchPayments()
  } catch { showToast({ type: 'fail', message: '操作失敗' }) }
  showPaymentPopup.value = false
}

const fetchPayments = async () => {
  if (!authStore.userId) return
  try { paymentHistory.value = await paymentApi.list({ user_id: authStore.userId }) } catch {}
}

onMounted(async () => { await authStore.fetchMembership(); await fetchPayments() })
</script>

<style scoped>
.membership-page { min-height: 100vh; background: #f5f7fa; padding-bottom: 90px; }
.card-section { padding: 24px; background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); display: flex; flex-direction: column; align-items: center; }

/* Flip Card Container */
.flip-card {
  background-color: transparent;
  width: 100%;
  max-width: 360px;
  aspect-ratio: 1.586; /* Credit Card Ratio */
  perspective: 1000px;
  cursor: pointer;
}

/* Flip Inner Container */
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform-style: preserve-3d;
}

.flip-card-inner.is-flipped {
  transform: rotateY(180deg);
}

/* Front and Back Faces */
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden; /* Safari */
  backface-visibility: hidden;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  overflow: hidden;
}

/* Front Style */
.flip-card-front {
  background-color: #1a202c;
  color: white;
}
.membership-card.committee { background: linear-gradient(135deg, #d69e2e, #b7791f); }
.membership-card.citizen { background: linear-gradient(135deg, #3182ce, #2c5282); }
.membership-card.friend { background: linear-gradient(135deg, #718096, #4a5568); }

.card-bg-pattern {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: radial-gradient(circle at 10% 20%, rgba(255,255,255,0.1) 0%, transparent 20%),
                    radial-gradient(circle at 90% 80%, rgba(255,255,255,0.1) 0%, transparent 20%);
  z-index: 1;
}

.card-content {
  position: relative;
  z-index: 2;
  height: 100%;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: left;
}

.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.org-branding { display: flex; align-items: center; font-size: 16px; font-weight: 700; letter-spacing: 1px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
.level-badge { font-size: 10px; background: rgba(255,255,255,0.25); padding: 4px 8px; border-radius: 4px; backdrop-filter: blur(4px); letter-spacing: 0.5px; font-weight: 600; text-transform: uppercase; }

.card-body { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 16px; margin-top: 10px; }
.chip-icon {
  width: 44px; height: 32px;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 6px;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(255,255,255,0.4), 0 2px 4px rgba(0,0,0,0.2);
}
.chip-line { position: absolute; background: rgba(0,0,0,0.15); height: 1px; width: 100%; }
.chip-line:nth-child(1) { top: 33%; }
.chip-line:nth-child(2) { top: 66%; }
.chip-line:nth-child(3) { left: 33%; height: 100%; width: 1px; top: 0; }
.chip-line:nth-child(4) { left: 66%; height: 100%; width: 1px; top: 0; }

.card-number { font-family: 'Courier New', Courier, monospace; font-size: 18px; letter-spacing: 2px; text-shadow: 0 2px 2px rgba(0,0,0,0.3); font-weight: 600; }

.card-footer { display: flex; justify-content: space-between; align-items: flex-end; }
.member-name { font-size: 18px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); max-width: 60%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.expiry-date { text-align: right; }
.expiry-date .label { font-size: 8px; opacity: 0.8; margin-bottom: 2px; letter-spacing: 1px; }
.expiry-date .date { font-family: 'Courier New', Courier, monospace; font-size: 14px; font-weight: 600; }

/* Back Style */
.flip-card-back {
  background-color: white;
  color: #1a202c;
  transform: rotateY(180deg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  padding: 24px;
}
.qr-title { font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #2d3748; }
.qr-frame { background: white; padding: 10px; border-radius: 8px; border: 2px solid #e2e8f0; }
.qr-hint { font-size: 12px; color: #718096; margin-top: 16px; }

.interaction-hint { margin-top: 20px; color: rgba(255,255,255,0.7); font-size: 13px; display: flex; align-items: center; gap: 6px; }

.benefits-list { padding: 12px 16px; }
.benefit-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.benefit-item:last-child { border-bottom: none; }
.benefit-item span { flex: 1; font-size: 14px; color: #1a202c; }
.benefit-item span.disabled { color: #a0aec0; text-decoration: line-through; }
.payment-amount { font-weight: 600; color: #38a169; margin-right: 8px; }
.action-section { padding: 16px; }
.pay-method { display: flex; align-items: center; padding: 14px; border: 2px solid #e2e8f0; border-radius: 12px; margin-bottom: 10px; cursor: pointer; }
.pay-method.selected { border-color: #3182ce; background: #ebf8ff; }
</style>
