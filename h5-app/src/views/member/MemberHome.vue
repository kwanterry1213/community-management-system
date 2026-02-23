<template>
  <div class="member-home">
    <!-- 頂部導航 -->
    <van-nav-bar title="首頁">
      <template #right>
        <van-icon name="bell" size="24" badge="2" color="#323233" />
      </template>
    </van-nav-bar>

    <!-- 會籍狀態卡 -->
    <div class="membership-card" :class="authStore.userLevel">
      <div class="card-bg"></div>
      <div class="card-content">
        <div class="card-header">
          <span class="level-badge">{{ authStore.levelInfo.icon }} {{ authStore.levelInfo.name }}</span>
          <span class="member-id">{{ authStore.membership?.membership_no || '' }}</span>
        </div>
        <div class="card-body">
          <div class="member-name">{{ displayName }}</div>
          <div class="member-since">加入於 {{ authStore.membership?.joined_at?.split('T')[0] || '—' }}</div>
        </div>
        <div class="card-footer" v-if="authStore.userLevel === 'admin'">
          <div class="admin-stats">
             <span><van-icon name="manager" /> 管理員權限已啟用</span>
          </div>
          <van-button size="small" round color="#ecc94b" style="color: #000; font-weight: bold;" @click="$router.push('/admin/events')">
            進入管理後台
          </van-button>
        </div>
        <div class="card-footer" v-else-if="authStore.userLevel !== 'friend'">
          <div class="expiry-info">
            <van-icon name="clock-o" />
            <span>會籍到期：{{ authStore.membership?.expires_at?.split('T')[0] || '—' }}</span>
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
      <div class="action-item" @click="$router.push('/admin/scanner')" v-if="authStore.isCommitteeOrAbove">
        <div class="action-icon scanner">
          <van-icon name="scan" size="24" />
        </div>
        <span>掃碼簽到</span>
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
      <div class="event-list" v-if="upcomingEvents.length > 0">
        <div v-for="event in upcomingEvents" :key="event.id" class="event-card" @click="router.push(`/m/events?eventId=${event.id}`)">
          <img :src="getEventImage(event)" class="event-image" />
          <div class="event-info">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-meta">
              <span><van-icon name="clock-o" /> {{ formatDate(event.start_at) }}</span>
              <span><van-icon name="location-o" /> {{ event.location || '待定' }}</span>
            </div>
            <div class="event-footer">
              <span class="event-type">{{ event.is_public ? '公開' : '會員專屬' }}</span>
              <span class="event-quota">{{ event.capacity ? `${event.capacity} 人` : '不限' }}</span>
            </div>
          </div>
        </div>
      </div>
      <van-empty v-else description="暫無近期活動" image="search" />
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
        <div class="qr-code-placeholder" style="background: white; padding: 10px;">
          <qrcode-vue :value="authStore.membership?.membership_no || ''" :size="140" level="H" />
        </div>
        <div class="qr-id">{{ authStore.membership?.membership_no || '' }}</div>
        <div class="qr-name">{{ displayName }}</div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { eventApi, announcementApi } from '@/services/api'
import { useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'

const authStore = useAuthStore()
const router = useRouter()

const isAdmin = computed(() => authStore.isAdmin)
const displayName = computed(() => authStore.currentUser?.username || '會員')
const avatarUrl = computed(() =>
  authStore.currentUser?.profile_picture_url ||
  `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName.value)}&background=1a365d&color=fff&size=128`
)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早安'
  if (hour < 18) return '午安'
  return '晚安'
})

// API 數據
const upcomingEvents = ref([])
const latestAnnouncement = ref('歡迎來到未來街坊圈！')

const eventImages = [
  'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=300&h=200&fit=crop',
  'https://images.unsplash.com/photo-1555244162-803834f70033?w=300&h=200&fit=crop',
  'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=300&h=200&fit=crop',
  'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=300&h=200&fit=crop',
]

const getEventImage = (event) => {
  return eventImages[(event.id - 1) % eventImages.length]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const showQR = ref(false)
const showQRCode = () => { showQR.value = true }

onMounted(async () => {
  // 獲取會籍
  await authStore.fetchMembership()

  // 獲取近期活動（最多顯示2個）
  try {
    const events = await eventApi.list()
    upcomingEvents.value = events.slice(0, 2)
  } catch (err) {
    console.error('載入活動失敗', err)
  }

  // 獲取最新公告
  try {
    const announcements = await announcementApi.list()
    if (announcements.length > 0) {
      latestAnnouncement.value = `【${announcements[0].title}】${announcements[0].content}`
    }
  } catch (err) {
    console.error('載入公告失敗', err)
  }
})
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
/* Default background to avoid white flash */
.membership-card {
  margin: 16px;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  /* aspect-ratio: 1.586; */ /* Too tall */
  height: 180px; /* Fixed height for better proportion */
  box-shadow: 0 4px 12px rgba(0,0,0,0.1); /* Softer shadow */
  cursor: pointer;
  transition: transform 0.2s;
  background: linear-gradient(135deg, #718096, #4a5568); /* Default to friend style */
}

.membership-card:active {
  transform: scale(0.98);
}

.membership-card.committee { background: linear-gradient(135deg, #d69e2e, #b7791f); }
.membership-card.citizen { background: linear-gradient(135deg, #3182ce, #2c5282); }
.membership-card.friend { background: linear-gradient(135deg, #718096, #4a5568); }
.membership-card.admin { background: linear-gradient(135deg, #1a202c, #2d3748); border: 1px solid #4a5568; }
.membership-card.admin { background: linear-gradient(135deg, #1a202c, #2d3748); border: 1px solid #4a5568; }

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
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.org-branding {
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.level-badge {
  font-size: 10px;
  background: rgba(255,255,255,0.25);
  padding: 4px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
  font-weight: 600;
  text-transform: uppercase;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.chip-icon {
  width: 36px; height: 26px;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(255,255,255,0.4), 0 2px 4px rgba(0,0,0,0.2);
}

.chip-line { position: absolute; background: rgba(0,0,0,0.15); height: 1px; width: 100%; }
.chip-line:nth-child(1) { top: 33%; }
.chip-line:nth-child(2) { top: 66%; }
.chip-line:nth-child(3) { left: 33%; height: 100%; width: 1px; top: 0; }
.chip-line:nth-child(4) { left: 66%; height: 100%; width: 1px; top: 0; }

.card-number {
  font-family: 'Courier New', Courier, monospace;
  font-size: 16px;
  letter-spacing: 2px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  font-weight: 600;
  margin-top: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.member-name {
  font-size: 16px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.validity {
  font-size: 10px;
  opacity: 0.9;
  margin-top: 2px;
}

.mini-qr {
  opacity: 0.8;
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
.action-icon.scanner { background: linear-gradient(135deg, #ed8936, #dd6b20); }

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
  background: #c6f6d5;
  color: #22543d;
}

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
