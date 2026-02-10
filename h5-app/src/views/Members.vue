<template>
  <div class="page members-page">
    <van-nav-bar title="會員管理" />
    
    <!-- 搜尋列 -->
    <van-search
      v-model="searchText"
      placeholder="搜尋會員姓名、電話..."
      show-action
      @search="onSearch"
    >
      <template #action>
        <van-icon name="filter-o" size="20" @click="showFilter = true" />
      </template>
    </van-search>

    <!-- 篩選標籤 -->
    <div class="filter-tabs">
      <van-tabs v-model:active="activeStatus" shrink>
        <van-tab title="全部" name="all" />
        <van-tab :title="`有效 (${stats.active})`" name="active" />
        <van-tab :title="`待審核 (${stats.pending})`" name="pending" />
        <van-tab :title="`已過期 (${stats.expired})`" name="expired" />
      </van-tabs>
    </div>

    <!-- 會員列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="沒有更多了"
        @load="onLoad"
      >
        <div class="member-list">
          <div
            v-for="member in filteredMembers"
            :key="member.id"
            class="member-card"
            @click="$router.push(`/admin/member/${member.id}`)"
          >
            <img :src="member.avatar" class="member-avatar" />
            <div class="member-content">
              <div class="member-header">
                <span class="member-name">{{ member.name }}</span>
                <span :class="['membership-badge', member.membershipType]">
                  {{ memberStore.membershipTypes[member.membershipType].label }}
                </span>
              </div>
              <div class="member-meta">
                <span>{{ member.phone }}</span>
                <span class="divider">|</span>
                <span>{{ member.id }}</span>
              </div>
              <div class="member-footer">
                <span :class="['status-tag', member.status]">
                  {{ memberStore.statusTypes[member.status].label }}
                </span>
                <span v-if="member.expiryDate" class="expiry-date">
                  到期：{{ member.expiryDate }}
                </span>
              </div>
            </div>
            <van-icon name="arrow" class="arrow-icon" />
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 篩選彈窗 -->
    <van-popup v-model:show="showFilter" position="right" :style="{ width: '80%', height: '100%' }">
      <div class="filter-panel">
        <div class="filter-header">
          <span>篩選條件</span>
          <van-button type="primary" size="small" plain @click="resetFilter">重置</van-button>
        </div>
        <div class="filter-section">
          <div class="filter-title">會籍類型</div>
          <van-checkbox-group v-model="filterMembership" direction="horizontal">
            <van-checkbox name="normal" shape="square">普通會員</van-checkbox>
            <van-checkbox name="silver" shape="square">銀級會員</van-checkbox>
            <van-checkbox name="gold" shape="square">金級會員</van-checkbox>
            <van-checkbox name="enterprise" shape="square">企業會員</van-checkbox>
          </van-checkbox-group>
        </div>
        <div class="filter-footer">
          <van-button type="primary" block round @click="applyFilter">確認篩選</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMemberStore } from '@/stores/member'

const memberStore = useMemberStore()
const stats = computed(() => memberStore.stats)

const searchText = ref('')
const activeStatus = ref('all')
const showFilter = ref(false)
const filterMembership = ref([])

const refreshing = ref(false)
const loading = ref(false)
const finished = ref(true)

const filteredMembers = computed(() => {
  let result = memberStore.members

  // 狀態篩選
  if (activeStatus.value !== 'all') {
    result = result.filter(m => m.status === activeStatus.value)
  }

  // 會籍類型篩選
  if (filterMembership.value.length > 0) {
    result = result.filter(m => filterMembership.value.includes(m.membershipType))
  }

  // 搜尋
  if (searchText.value) {
    const query = searchText.value.toLowerCase()
    result = result.filter(m =>
      m.name.toLowerCase().includes(query) ||
      m.phone.includes(query) ||
      m.id.toLowerCase().includes(query)
    )
  }

  return result
})

const onSearch = () => {}
const onRefresh = () => {
  setTimeout(() => { refreshing.value = false }, 1000)
}
const onLoad = () => {
  loading.value = false
  finished.value = true
}
const resetFilter = () => {
  filterMembership.value = []
}
const applyFilter = () => {
  showFilter.value = false
}
</script>

<style scoped>
.members-page {
  padding: 0;
  background: var(--color-gray-100);
}

.filter-tabs {
  background: white;
}

.member-list {
  padding: 12px;
}

.member-card {
  background: white;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.member-avatar {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  margin-right: 12px;
  flex-shrink: 0;
}

.member-content {
  flex: 1;
  min-width: 0;
}

.member-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.member-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-gray-800);
}

.member-meta {
  font-size: 12px;
  color: var(--color-gray-500);
  margin-bottom: 6px;
}

.member-meta .divider {
  margin: 0 6px;
  color: var(--color-gray-300);
}

.member-footer {
  display: flex;
  align-items: center;
  gap: 10px;
}

.expiry-date {
  font-size: 11px;
  color: var(--color-gray-400);
}

.arrow-icon {
  color: var(--color-gray-300);
  margin-left: 8px;
}

.filter-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--color-gray-100);
}

.filter-section {
  padding: 16px;
}

.filter-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 12px;
  color: var(--color-gray-700);
}

.filter-footer {
  margin-top: auto;
  padding: 16px;
}
</style>
