<template>
  <div class="events-page">
    <van-nav-bar title="活動" />
    
    <!-- 活動分類 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="全部" name="all" />
      <van-tab title="即將舉行" name="upcoming" />
      <van-tab title="已結束" name="past" />
    </van-tabs>

    <!-- 活動列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <div class="event-list">
        <div v-for="event in filteredEvents" :key="event.id" class="event-card" @click="showEventDetail(event)">
          <img :src="getEventImage(event)" class="event-cover" />
          <div class="event-content">
            <div class="event-date-badge">
              <span class="month">{{ formatMonth(event.start_at) }}</span>
              <span class="day">{{ formatDay(event.start_at) }}</span>
            </div>
            <div class="event-info">
              <span :class="['event-type-tag', event.is_public ? 'public' : 'members']">
                {{ event.is_public ? '公開活動' : '會員專屬' }}
              </span>
              <h3 class="event-title">{{ event.title }}</h3>
              <div class="event-meta">
                <span><van-icon name="clock-o" /> {{ formatTime(event.start_at) }}</span>
                <span><van-icon name="location-o" /> {{ event.location || '待定' }}</span>
              </div>
              <div class="event-footer">
                <div class="event-progress" v-if="event.capacity">
                  <span class="progress-text">名額 {{ event.capacity }} 人</span>
                </div>
                <span v-else class="progress-text">不限名額</span>
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
        <img :src="getEventImage(selectedEvent)" class="detail-cover" />
        <div class="detail-content">
          <span :class="['event-type-tag', selectedEvent.is_public ? 'public' : 'members']">
            {{ selectedEvent.is_public ? '公開活動' : '會員專屬' }}
          </span>
          <h2>{{ selectedEvent.title }}</h2>
          
          <div class="detail-info-list">
            <div class="detail-info-item">
              <van-icon name="clock-o" />
              <div>
                <span class="label">時間</span>
                <span class="value">{{ formatDate(selectedEvent.start_at) }}{{ selectedEvent.end_at ? ' ~ ' + formatDate(selectedEvent.end_at) : '' }}</span>
              </div>
            </div>
            <div class="detail-info-item">
              <van-icon name="location-o" />
              <div>
                <span class="label">地點</span>
                <span class="value">{{ selectedEvent.location || '待定' }}</span>
              </div>
            </div>
            <div class="detail-info-item" v-if="selectedEvent.capacity">
              <van-icon name="friends-o" />
              <div>
                <span class="label">名額</span>
                <span class="value">{{ selectedEvent.capacity }} 人</span>
              </div>
            </div>
          </div>

          <div class="detail-description">
            <h4>活動說明</h4>
            <p>{{ selectedEvent.description || '歡迎所有街坊參與！詳細內容請關注後續通知。' }}</p>
          </div>
        </div>

        <div class="detail-footer">
          <van-button type="primary" block round>
            了解更多
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { eventApi } from '@/services/api'

const activeTab = ref('all')
const refreshing = ref(false)
const showDetail = ref(false)
const selectedEvent = ref(null)

const events = ref([])
const loading = ref(false)

const eventImages = [
  'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&h=300&fit=crop',
  'https://images.unsplash.com/photo-1555244162-803834f70033?w=600&h=300&fit=crop',
  'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&h=300&fit=crop',
  'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=600&h=300&fit=crop',
]

const getEventImage = (event) => eventImages[(event.id - 1) % eventImages.length]

const filteredEvents = computed(() => {
  const now = new Date()
  if (activeTab.value === 'upcoming') {
    return events.value.filter(e => new Date(e.start_at) >= now)
  }
  if (activeTab.value === 'past') {
    return events.value.filter(e => new Date(e.start_at) < now)
  }
  return events.value
})

const formatMonth = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月`
}

const formatDay = (dateStr) => {
  if (!dateStr) return ''
  return String(new Date(dateStr).getDate()).padStart(2, '0')
}

const formatTime = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const showEventDetail = (event) => {
  selectedEvent.value = event
  showDetail.value = true
}

const fetchEvents = async () => {
  loading.value = true
  try {
    events.value = await eventApi.list()
  } catch (err) {
    console.error('載入活動失敗', err)
  } finally {
    loading.value = false
  }
}

const onRefresh = async () => {
  await fetchEvents()
  refreshing.value = false
}

onMounted(fetchEvents)
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

.event-type-tag.public { background: #c6f6d5; color: #22543d; }
.event-type-tag.members { background: #feebc8; color: #744210; }

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

.progress-text {
  font-size: 11px;
  color: #718096;
}

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
</style>
