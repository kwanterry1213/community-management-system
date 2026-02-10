<template>
  <div class="events-page">
    <van-nav-bar title="活動" />
    
    <!-- 活動分類 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="全部" name="all" />
      <van-tab title="講座" name="seminar" />
      <van-tab title="聚會" name="gathering" />
      <van-tab title="工作坊" name="workshop" />
      <van-tab title="我的報名" name="mine" />
    </van-tabs>

    <!-- 活動列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <div class="event-list">
        <div v-for="event in filteredEvents" :key="event.id" class="event-card" @click="showEventDetail(event)">
          <img :src="event.image" class="event-cover" />
          <div class="event-content">
            <div class="event-date-badge">
              <span class="month">{{ formatMonth(event.date) }}</span>
              <span class="day">{{ formatDay(event.date) }}</span>
            </div>
            <div class="event-info">
              <span :class="['event-type-tag', event.type]">{{ typeLabels[event.type] }}</span>
              <h3 class="event-title">{{ event.title }}</h3>
              <div class="event-meta">
                <span><van-icon name="clock-o" /> {{ event.time }}</span>
                <span><van-icon name="location-o" /> {{ event.location }}</span>
              </div>
              <div class="event-footer">
                <div class="event-progress">
                  <van-progress :percentage="(event.enrolled / event.quota) * 100" :show-pivot="false" stroke-width="4" />
                  <span class="progress-text">{{ event.enrolled }}/{{ event.quota }} 人已報名</span>
                </div>
                <van-button 
                  v-if="!event.isEnrolled && event.enrolled < event.quota"
                  size="small" 
                  type="primary" 
                  round
                  @click.stop="enrollEvent(event)"
                >
                  報名
                </van-button>
                <div v-else-if="event.isEnrolled" class="enrolled-status">
                  <van-tag type="success" round>已報名</van-tag>
                  <van-tag v-if="event.fee > 0" :type="event.paymentStatus === 'paid' ? 'success' : 'warning'" round plain>
                    {{ paymentStatusLabels[event.paymentStatus] }}
                  </van-tag>
                </div>
                <van-tag v-else type="default" round>已額滿</van-tag>
              </div>
            </div>
          </div>
        </div>

        <van-empty v-if="filteredEvents.length === 0" description="暫無活動" />
      </div>
    </van-pull-refresh>

    <!-- 活動詳情彈窗 -->
    <van-popup v-model:show="showDetail" position="bottom" round style="height: 80%">
      <div class="event-detail" v-if="selectedEvent">
        <img :src="selectedEvent.image" class="detail-cover" />
        <div class="detail-content">
          <span :class="['event-type-tag', selectedEvent.type]">{{ typeLabels[selectedEvent.type] }}</span>
          <h2>{{ selectedEvent.title }}</h2>
          
          <div class="detail-info-list">
            <div class="detail-info-item">
              <van-icon name="clock-o" />
              <div>
                <span class="label">時間</span>
                <span class="value">{{ selectedEvent.date }} {{ selectedEvent.time }}</span>
              </div>
            </div>
            <div class="detail-info-item">
              <van-icon name="location-o" />
              <div>
                <span class="label">地點</span>
                <span class="value">{{ selectedEvent.location }}</span>
              </div>
            </div>
            <div class="detail-info-item">
              <van-icon name="friends-o" />
              <div>
                <span class="label">人數</span>
                <span class="value">{{ selectedEvent.enrolled }}/{{ selectedEvent.quota }} 人</span>
              </div>
            </div>
            <div class="detail-info-item" v-if="selectedEvent.fee">
              <van-icon name="gold-coin-o" />
              <div>
                <span class="label">費用</span>
                <span class="value">{{ selectedEvent.memberOnly ? '會員專屬' : `MOP$ ${selectedEvent.fee}` }}</span>
              </div>
            </div>
            <!-- 付款狀態 (已報名且有費用) -->
            <div class="detail-info-item" v-if="selectedEvent.isEnrolled && selectedEvent.fee > 0">
              <van-icon name="balance-o" />
              <div>
                <span class="label">付款狀態</span>
                <span :class="['value', 'payment-status', selectedEvent.paymentStatus]">
                  {{ paymentStatusLabels[selectedEvent.paymentStatus] }}
                </span>
              </div>
            </div>
            <!-- 付款方式 (已報名且有費用且已付款) -->
            <div class="detail-info-item" v-if="selectedEvent.isEnrolled && selectedEvent.fee > 0 && selectedEvent.paymentMethod">
              <van-icon name="credit-pay" />
              <div>
                <span class="label">付款方式</span>
                <span class="value">{{ paymentMethodLabels[selectedEvent.paymentMethod] }}</span>
              </div>
            </div>
          </div>

          <div class="detail-description">
            <h4>活動說明</h4>
            <p>{{ selectedEvent.description || '歡迎所有街坊參與！詳細內容請關注後續通知。' }}</p>
          </div>
        </div>

        <div class="detail-footer">
          <van-button 
            v-if="!selectedEvent.isEnrolled && selectedEvent.enrolled < selectedEvent.quota"
            type="primary" 
            block 
            round
            @click="enrollEvent(selectedEvent)"
          >
            {{ selectedEvent.fee > 0 ? `立即報名 (MOP$ ${selectedEvent.fee})` : '立即報名' }}
          </van-button>
          <van-button 
            v-else-if="selectedEvent.isEnrolled"
            type="danger" 
            plain
            block 
            round
            @click="cancelEnroll(selectedEvent)"
          >
            取消報名
          </van-button>
          <van-button v-else disabled block round>已額滿</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 付款方式選擇彈窗 -->
    <van-popup v-model:show="showPaymentPopup" position="bottom" round :style="{ minHeight: '40%' }">
      <div class="payment-popup">
        <div class="payment-popup-header">
          <h3>選擇付款方式</h3>
          <van-icon name="cross" @click="showPaymentPopup = false" />
        </div>

        <div class="payment-summary">
          <div class="payment-summary-row">
            <span>活動</span>
            <span>{{ pendingPaymentEvent?.title }}</span>
          </div>
          <div class="payment-summary-row total">
            <span>費用</span>
            <span class="amount">MOP$ {{ pendingPaymentEvent?.fee }}</span>
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
            @click="confirmPayment"
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
import { showToast, showConfirmDialog } from 'vant'

const activeTab = ref('all')
const refreshing = ref(false)
const showDetail = ref(false)
const selectedEvent = ref(null)
const showPaymentPopup = ref(false)
const pendingPaymentEvent = ref(null)
const selectedPaymentMethod = ref('')

const typeLabels = {
  seminar: '講座',
  gathering: '聚會',
  workshop: '工作坊',
  meeting: '會議'
}

const paymentStatusLabels = {
  pending: '待付款',
  paid: '已付款',
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

const events = ref([
  {
    id: 1,
    title: '街坊創業分享會',
    type: 'seminar',
    date: '2026/02/15',
    time: '14:00 - 16:00',
    location: '社區中心 B1 會議室',
    image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&h=300&fit=crop',
    enrolled: 23,
    quota: 30,
    fee: 0,
    memberOnly: false,
    isEnrolled: false,
    paymentStatus: null,
    paymentMethod: null,
    description: '邀請多位成功創業的街坊分享他們的創業心得與經驗，適合想創業或正在創業的朋友參加。'
  },
  {
    id: 2,
    title: '新春團拜聚餐',
    type: 'gathering',
    date: '2026/02/20',
    time: '18:00 - 21:00',
    location: '金龍餐廳 (中正路88號)',
    image: 'https://images.unsplash.com/photo-1555244162-803834f70033?w=600&h=300&fit=crop',
    enrolled: 45,
    quota: 50,
    fee: 80,
    memberOnly: true,
    isEnrolled: true,
    paymentStatus: 'paid',
    paymentMethod: 'bank',
    description: '一年一度的新春團拜聚餐，歡迎所有圈圈委及圈圈民攜家帶眷參加！'
  },
  {
    id: 3,
    title: 'AI 應用工作坊',
    type: 'workshop',
    date: '2026/03/01',
    time: '09:00 - 12:00',
    location: '創新中心 3F',
    image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&h=300&fit=crop',
    enrolled: 15,
    quota: 20,
    fee: 80,
    memberOnly: false,
    isEnrolled: false,
    paymentStatus: null,
    paymentMethod: null,
    description: '學習如何在日常工作中運用 AI 工具提升效率，實作練習為主。'
  },
  {
    id: 4,
    title: '第一季會員大會',
    type: 'meeting',
    date: '2026/03/15',
    time: '19:00 - 21:00',
    location: '社區中心 大禮堂',
    image: 'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=600&h=300&fit=crop',
    enrolled: 58,
    quota: 100,
    fee: 0,
    memberOnly: false,
    isEnrolled: false,
    paymentStatus: null,
    paymentMethod: null,
    description: '2026年第一季會員大會，討論年度計畫與預算，歡迎所有圈圈友以上會員參加。'
  }
])

const filteredEvents = computed(() => {
  if (activeTab.value === 'all') return events.value
  if (activeTab.value === 'mine') return events.value.filter(e => e.isEnrolled)
  return events.value.filter(e => e.type === activeTab.value)
})

const formatMonth = (dateStr) => {
  const [, month] = dateStr.split('/')
  return `${parseInt(month)}月`
}

const formatDay = (dateStr) => {
  const [, , day] = dateStr.split('/')
  return day
}

const showEventDetail = (event) => {
  selectedEvent.value = event
  showDetail.value = true
}

const enrollEvent = async (event) => {
  try {
    await showConfirmDialog({
      title: '確認報名',
      message: `確定要報名「${event.title}」嗎？${event.fee > 0 ? `\n費用：MOP$ ${event.fee}` : ''}`
    })

    if (event.fee > 0) {
      // 有費用的活動 → 先選付款方式
      pendingPaymentEvent.value = event
      selectedPaymentMethod.value = ''
      showDetail.value = false
      showPaymentPopup.value = true
    } else {
      // 免費活動 → 直接報名
      event.isEnrolled = true
      event.enrolled++
      showToast({ type: 'success', message: '報名成功！' })
      showDetail.value = false
    }
  } catch {
    // 用戶取消
  }
}

const confirmPayment = () => {
  const event = pendingPaymentEvent.value
  if (!event || !selectedPaymentMethod.value) return

  event.isEnrolled = true
  event.enrolled++
  event.paymentMethod = selectedPaymentMethod.value

  // 模擬付款狀態：銀行轉賬和現金為待確認，其餘即時到賬
  if (selectedPaymentMethod.value === 'bank' || selectedPaymentMethod.value === 'cash') {
    event.paymentStatus = 'pending'
    showToast({ type: 'success', message: '報名成功！請完成付款' })
  } else {
    event.paymentStatus = 'paid'
    showToast({ type: 'success', message: '報名並付款成功！' })
  }

  showPaymentPopup.value = false
  pendingPaymentEvent.value = null
  selectedPaymentMethod.value = ''
}

const cancelEnroll = async (event) => {
  try {
    await showConfirmDialog({
      title: '取消報名',
      message: event.paymentStatus === 'paid' 
        ? '取消報名後將會安排退款，確定要取消嗎？' 
        : '確定要取消報名嗎？'
    })
    event.isEnrolled = false
    event.enrolled--
    if (event.paymentStatus === 'paid') {
      event.paymentStatus = 'refunded'
      showToast({ message: '已取消報名，退款處理中' })
    } else {
      event.paymentStatus = null
      event.paymentMethod = null
      showToast({ message: '已取消報名' })
    }
    showDetail.value = false
  } catch {
    // 用戶取消
  }
}

const onRefresh = () => {
  setTimeout(() => { refreshing.value = false }, 1000)
}
</script>

<style scoped>
.events-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 70px;
}

.event-list {
  padding: 12px;
}

.event-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.event-cover {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.event-content {
  position: relative;
  padding: 12px 14px;
}

.event-date-badge {
  position: absolute;
  top: -30px;
  left: 14px;
  background: #1a365d;
  color: #fff;
  padding: 8px 12px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.event-date-badge .month {
  display: block;
  font-size: 11px;
  opacity: 0.9;
}

.event-date-badge .day {
  display: block;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.event-info {
  padding-top: 20px;
}

.event-type-tag {
  display: inline-block;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-bottom: 6px;
}

.event-type-tag.seminar { background: #c6f6d5; color: #22543d; }
.event-type-tag.gathering { background: #feebc8; color: #744210; }
.event-type-tag.workshop { background: #e9d8fd; color: #553c9a; }
.event-type-tag.meeting { background: #bee3f8; color: #2c5282; }

.event-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 8px;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #718096;
  margin-bottom: 12px;
}

.event-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-progress {
  flex: 1;
  margin-right: 12px;
}

.progress-text {
  font-size: 11px;
  color: #718096;
}

.enrolled-status {
  display: flex;
  gap: 6px;
  align-items: center;
}

/* 付款狀態顏色 */
.payment-status.paid { color: #38a169; font-weight: 600; }
.payment-status.pending { color: #d69e2e; font-weight: 600; }
.payment-status.refunded { color: #718096; font-weight: 600; }

/* 詳情彈窗 */
.event-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-cover {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.detail-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.detail-content h2 {
  font-size: 20px;
  margin: 8px 0 16px;
  color: #1a202c;
}

.detail-info-list {
  background: #f7fafc;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.detail-info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
}

.detail-info-item:not(:last-child) {
  border-bottom: 1px solid #e2e8f0;
}

.detail-info-item .van-icon {
  font-size: 18px;
  color: #3182ce;
  margin-top: 2px;
}

.detail-info-item .label {
  display: block;
  font-size: 12px;
  color: #718096;
}

.detail-info-item .value {
  font-size: 14px;
  color: #1a202c;
}

.detail-description h4 {
  font-size: 15px;
  margin: 0 0 8px;
  color: #1a202c;
}

.detail-description p {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.6;
}

.detail-footer {
  padding: 16px;
  border-top: 1px solid #e2e8f0;
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
