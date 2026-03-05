<template>
  <div class="search-page">
    <van-nav-bar title="智能搜索" left-arrow @click-left="$router.back()" />

    <div class="search-header">
      <van-search
        v-model="searchQuery"
        placeholder="搜尋會員或描述你的需求..."
        show-action
        autofocus
        @search="doSearch"
        @cancel="$router.back()"
      >
        <template #action>
          <span @click="doSearch" class="search-action">搜尋</span>
        </template>
      </van-search>
    </div>

    <!-- Quick tags (shown before search) -->
    <div v-if="!hasSearched" class="quick-section">
      <div v-if="searchHistory.length" class="history-section">
        <div class="section-header">
          <span class="section-title">搜尋記錄</span>
          <span class="clear-btn" @click="clearHistory">清除</span>
        </div>
        <div class="tag-list">
          <van-tag
            v-for="(item, idx) in searchHistory"
            :key="idx"
            size="large"
            plain
            type="primary"
            class="quick-tag"
            @click="searchQuery = item; doSearch()"
          >{{ item }}</van-tag>
        </div>
      </div>

      <div class="suggest-section">
        <div class="section-header">
          <span class="section-title">快捷搜尋</span>
        </div>
        <div class="tag-list">
          <van-tag
            v-for="tag in quickTags"
            :key="tag"
            size="large"
            round
            color="#e8f4fd"
            text-color="#1989fa"
            class="quick-tag"
            @click="searchQuery = tag; doSearch()"
          >{{ tag }}</van-tag>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-section">
      <van-loading size="36px" vertical>AI 分析中...</van-loading>
    </div>

    <!-- Results -->
    <div v-if="hasSearched && !loading" class="results-section">
      <div v-if="isAi" class="ai-badge">
        <van-icon name="smile-o" /> AI 智能推薦
      </div>

      <van-empty v-if="!results.length" description="沒有找到匹配的會員" />

      <div v-for="item in results" :key="item.user_id" class="member-card" @click="toggleExpand(item.user_id)">
        <div class="card-main">
          <img :src="getAvatar(item)" class="card-avatar" />
          <div class="card-info">
            <div class="card-name">{{ item.username }}</div>
            <div v-if="item.occupation" class="card-occupation">{{ item.occupation }}</div>
            <div v-if="item.skills" class="card-skills">
              <van-tag
                v-for="skill in item.skills.split(',')"
                :key="skill"
                size="medium"
                round
                color="#f0f9eb"
                text-color="#67c23a"
                class="skill-tag"
              >{{ skill.trim() }}</van-tag>
            </div>
            <div v-if="item.match_reason" class="card-reason">
              <van-icon name="bulb-o" /> {{ item.match_reason }}
            </div>
          </div>
        </div>

        <van-collapse-item v-if="expandedId === item.user_id" :border="false" class="card-contact">
          <div class="contact-row" v-if="item.phone">
            <van-icon name="phone-o" />
            <span>{{ item.phone }}</span>
            <a :href="'tel:' + item.phone" class="call-btn" @click.stop>
              <van-button size="mini" type="primary" icon="phone-o" round>撥打</van-button>
            </a>
          </div>
          <div class="contact-row" v-if="item.email">
            <van-icon name="envelop-o" />
            <span>{{ item.email }}</span>
          </div>
          <div class="contact-row" v-if="item.bio">
            <van-icon name="description" />
            <span class="bio-text">{{ item.bio }}</span>
          </div>
        </van-collapse-item>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { showToast } from 'vant'
import { searchApi } from '@/services/api'

const searchQuery = ref('')
const results = ref([])
const isAi = ref(false)
const loading = ref(false)
const hasSearched = ref(false)
const expandedId = ref(null)

const HISTORY_KEY = 'smart_search_history'
const quickTags = ['找人裝修', '水電維修', '搬運服務', '清潔打掃', '殺蟲服務', '補習教學']

const searchHistory = ref(JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'))

function saveHistory(query) {
  let history = searchHistory.value.filter(h => h !== query)
  history.unshift(query)
  history = history.slice(0, 5)
  searchHistory.value = history
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
}

function clearHistory() {
  searchHistory.value = []
  localStorage.removeItem(HISTORY_KEY)
}

function getAvatar(item) {
  if (item.profile_picture) return item.profile_picture
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(item.username)}&background=1a365d&color=fff&size=80`
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

let lastSearchTime = 0
async function doSearch() {
  const q = searchQuery.value.trim()
  if (!q) {
    showToast('請輸入搜尋內容')
    return
  }

  const now = Date.now()
  if (now - lastSearchTime < 300) return
  lastSearchTime = now

  loading.value = true
  hasSearched.value = true
  results.value = []

  try {
    const res = await searchApi.smartSearch(q)
    results.value = res.results || []
    isAi.value = res.is_ai || false
    saveHistory(q)
  } catch (e) {
    showToast({ type: 'fail', message: '搜尋失敗，請稍後再試' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.search-header {
  position: sticky;
  top: 46px;
  z-index: 10;
  background: #fff;
}

.search-action {
  color: #1989fa;
  font-weight: 600;
}

.quick-section {
  padding: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.clear-btn {
  font-size: 13px;
  color: #999;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-tag {
  cursor: pointer;
  padding: 4px 12px !important;
}

.history-section {
  margin-bottom: 24px;
}

.suggest-section {
  margin-top: 8px;
}

.loading-section {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.results-section {
  padding: 12px 16px;
}

.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 16px;
  margin-bottom: 12px;
}

.member-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: transform 0.15s;
}

.member-card:active {
  transform: scale(0.98);
}

.card-main {
  display: flex;
  gap: 12px;
}

.card-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
}

.card-occupation {
  font-size: 13px;
  color: #718096;
  margin-top: 2px;
}

.card-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}

.skill-tag {
  font-size: 11px !important;
}

.card-reason {
  margin-top: 8px;
  font-size: 13px;
  color: #764ba2;
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-contact {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.contact-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 14px;
  color: #4a5568;
}

.contact-row .call-btn {
  margin-left: auto;
  text-decoration: none;
}

.bio-text {
  color: #718096;
  font-size: 13px;
}
</style>
