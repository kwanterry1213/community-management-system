<template>
  <div class="member-home">
    <!-- 頂部歡迎區 -->
    <div class="welcome-header">
      <div class="welcome-bg"></div>
      <div class="welcome-content">
        <div class="user-greeting">
          <img :src="currentUser.avatar" class="user-avatar" />
          <div class="greeting-text">
            <span class="greeting">{{ greeting }}，</span>
            <span class="user-name">{{ currentUser.name }}</span>
          </div>
        </div>
        <van-icon name="bell" size="24" color="#fff" badge="2" />
      </div>
    </div>

    <!-- 會籍狀態卡 -->
    <div class="membership-card" :class="currentUser.level">
      <div class="card-bg"></div>
      <div class="card-content">
        <div class="card-header">
          <span class="level-badge">{{ levelInfo.icon }} {{ levelInfo.name }}</span>
          <span class="member-id">{{ currentUser.id }}</span>
        </div>
        <div class="card-body">
          <div class="member-name">{{ currentUser.name }}</div>
          <div class="member-since">加入於 {{ currentUser.joinDate }}</div>
        </div>
        <div class="card-footer" v-if="currentUser.level !== 'friend'">
          <div class="expiry-info">
            <van-icon name="clock-o" />
            <span>會籍到期：{{ currentUser.expiryDate }}</span>
          </div>
          <van-button size="small" round plain color="#fff" @click="$router.push('/m/membership')">
            續費
          </van-button>
        </div>
        <div class="card-footer" v-else>
          <div class="upgrade-hint">
            <van-icon name="star-o" />
            <span>升級成為正式會員，享受更多權益</span>
          </div>
          <van-button size="small" round type="warning" @click="$router.push('/m/membership')">
            升級會籍
          </van-button>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <div class="action-item" @click="$router.push('/m/events')">
        <div class="action-icon events">
          <van-icon name="calendar-o" size="24" />
        </div>
        <span>活動報名</span>
      </div>
      <div class="action-item" @click="$router.push('/m/membership')">
        <div class="action-icon membership">
          <van-icon name="card" size="24" />
        </div>
        <span>我的會籍</span>
      </div>
      <div class="action-item" @click="showQRCode">
        <div class="action-icon qrcode">
          <van-icon name="qr" size="24" />
        </div>
        <span>會員證</span>
      </div>
      <div class="action-item" @click="$router.push('/m/profile')">
        <div class="action-icon profile">
          <van-icon name="setting-o" size="24" />
        </div>
        <span>設定</span>
      </div>
    </div>

    <!-- 近期活動 -->
    <div class="section">
      <div class="section-header">
        <span class="section-title">近期活動</span>
        <span class="section-more" @click="$router.push('/m/events')">
          查看全部 <van-icon name="arrow" />
        </span>
      </div>
      <div class="event-list">
        <div v-for="event in upcomingEvents" :key="event.id" class="event-card">
          <img :src="event.image" class="event-image" />
          <div class="event-info">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-meta">
              <span><van-icon name="clock-o" /> {{ event.date }}</span>
              <span><van-icon name="location-o" /> {{ event.location }}</span>
            </div>
            <div class="event-footer">
              <span :class="['event-type', event.type]">{{ eventTypes[event.type] }}</span>
              <span class="event-quota">{{ event.enrolled }}/{{ event.quota }} 人</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最新公告 -->
    <div class="section">
      <div class="section-header">
        <span class="section-title">最新公告</span>
      </div>
      <van-notice-bar left-icon="volume-o" scrollable :text="latestAnnouncement" />
    </div>

    <!-- QR Code 彈窗 -->
    <van-popup v-model:show="showQR" round style="padding: 20px; text-align: center;">
      <div class="qr-popup">
        <div class="qr-title">會員證 QR Code</div>
        <div class="qr-code-placeholder">
          <van-icon name="qr" size="120" color="#1a365d" />
        </div>
        <div class="qr-id">{{ currentUser.id }}</div>
        <div class="qr-name">{{ currentUser.name }}</div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 當前登入用戶（模擬）
const currentUser = ref({
  id: 'M-2024-0158',
  name: '陳大明',
  level: 'committee', // committee | citizen | friend
  phone: '0912-345-678',
  email: 'daming.chen@email.com',
  joinDate: '2022-06-15',
  expiryDate: '2026-06-30',
  avatar: 'https://ui-avatars.com/api/?name=陳大明&background=1a365d&color=fff&size=128'
})

// 級別資訊
const levelInfo = computed(() => {
  const levels = {
    committee: { name: '未來街坊圈圈委', icon: '⭐⭐⭐', color: '#d69e2e' },
    citizen: { name: '未來街坊圈圈民', icon: '⭐⭐', color: '#3182ce' },
    friend: { name: '未來街坊圈圈友', icon: '⭐', color: '#718096' }
  }
  return levels[currentUser.value.level]
})

// 問候語
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早安'
  if (hour < 18) return '午安'
  return '晚安'
})

// 近期活動
const upcomingEvents = ref([
  {
    id: 1,
    title: '街坊創業分享會',
    date: '2026/02/15 14:00',
    location: '社區中心 B1',
    image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=300&h=200&fit=crop',
    type: 'seminar',
    enrolled: 23,
    quota: 30
  },
  {
    id: 2,
    title: '新春團拜聚餐',
    date: '2026/02/20 18:00',
    location: '金龍餐廳',
    image: 'https://images.unsplash.com/photo-1555244162-803834f70033?w=300&h=200&fit=crop',
    type: 'gathering',
    enrolled: 45,
    quota: 50
  }
])

const eventTypes = {
  seminar: '講座',
  gathering: '聚會',
  workshop: '工作坊',
  meeting: '會議'
}

const latestAnnouncement = '【重要通知】2026年度會費繳納已開始，請於3月31日前完成繳費，逾期將影響會員權益。'

const showQR = ref(false)
const showQRCode = () => {
  showQR.value = true
}
</script>

<style scoped>
.member-home {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 70px;
}

/* 歡迎區 */
.welcome-header {
  position: relative;
  padding: 20px 16px;
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-greeting {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.3);
}

.greeting-text {
  color: #fff;
}

.greeting {
  font-size: 14px;
  opacity: 0.9;
}

.user-name {
  display: block;
  font-size: 18px;
  font-weight: 600;
  margin-top: 2px;
}

/* 會籍卡 */
.membership-card {
  position: relative;
  margin: -20px 16px 16px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
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

.card-content {
  position: relative;
  padding: 20px;
  color: #fff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.level-badge {
  font-size: 12px;
  background: rgba(255,255,255,0.2);
  padding: 4px 10px;
  border-radius: 20px;
}

.member-id {
  font-size: 12px;
  opacity: 0.8;
}

.card-body {
  margin-bottom: 16px;
}

.card-body .member-name {
  font-size: 24px;
  font-weight: 700;
}

.member-since {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.2);
}

.expiry-info, .upgrade-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

/* 快速操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 16px;
  background: #fff;
  margin: 0 16px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.action-icon.events { background: linear-gradient(135deg, #38a169, #2f855a); }
.action-icon.membership { background: linear-gradient(135deg, #3182ce, #2c5282); }
.action-icon.qrcode { background: linear-gradient(135deg, #805ad5, #6b46c1); }
.action-icon.profile { background: linear-gradient(135deg, #718096, #4a5568); }

.action-item span {
  font-size: 12px;
  color: #4a5568;
}

/* 區塊 */
.section {
  margin: 0 16px 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
}

.section-more {
  font-size: 13px;
  color: #3182ce;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 活動卡片 */
.event-card {
  display: flex;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.event-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  flex-shrink: 0;
}

.event-info {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.event-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a202c;
  line-height: 1.3;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #718096;
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

.event-type {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #e2e8f0;
  color: #4a5568;
}

.event-type.seminar { background: #c6f6d5; color: #22543d; }
.event-type.gathering { background: #feebc8; color: #744210; }

.event-quota {
  font-size: 12px;
  color: #718096;
}

/* QR彈窗 */
.qr-popup {
  text-align: center;
}

.qr-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.qr-code-placeholder {
  width: 160px;
  height: 160px;
  margin: 0 auto 16px;
  background: #f5f7fa;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-id {
  font-size: 14px;
  color: #718096;
}

.qr-name {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
  margin-top: 4px;
}
</style>
