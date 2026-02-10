<template>
  <div class="page detail-page">
    <van-nav-bar title="會員詳情" left-arrow @click-left="$router.back()" />
    
    <template v-if="member">
      <!-- 會員頭部資訊 -->
      <div class="profile-header">
        <img :src="member.avatar" class="profile-avatar" />
        <div class="profile-info">
          <div class="profile-name">{{ member.name }}</div>
          <div class="profile-tags">
            <span :class="['membership-badge', member.membershipType]">
              {{ memberStore.membershipTypes[member.membershipType].label }}
            </span>
            <span :class="['status-tag', member.status]">
              {{ memberStore.statusTypes[member.status].label }}
            </span>
          </div>
        </div>
      </div>

      <!-- 基本資料卡片 -->
      <div class="card">
        <div class="card-title"><van-icon name="user-o" /> 基本資料</div>
        <van-cell-group :border="false">
          <van-cell title="會員編號" :value="member.id" />
          <van-cell title="聯絡電話" :value="member.phone" is-link @click="callPhone" />
          <van-cell title="電子郵件" :value="member.email" />
          <van-cell title="公司名稱" :value="member.company" />
          <van-cell title="職稱" :value="member.title" />
        </van-cell-group>
      </div>

      <!-- 會籍資訊卡片 -->
      <div class="card">
        <div class="card-title"><van-icon name="certificate" /> 會籍資訊</div>
        <van-cell-group :border="false">
          <van-cell title="會籍類型">
            <template #value>
              <span :class="['membership-badge', member.membershipType]">
                {{ memberStore.membershipTypes[member.membershipType].label }}
              </span>
            </template>
          </van-cell>
          <van-cell title="加入日期" :value="member.joinDate" />
          <van-cell title="到期日期" :value="member.expiryDate || '-'" />
          <van-cell title="會籍狀態">
            <template #value>
              <span :class="['status-tag', member.status]">
                {{ memberStore.statusTypes[member.status].label }}
              </span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <!-- 繳費記錄 -->
      <div class="card">
        <div class="card-title"><van-icon name="bill-o" /> 繳費記錄</div>
        <div class="payment-list">
          <div class="payment-item">
            <div class="payment-info">
              <span class="payment-date">2024-07-01</span>
              <span class="payment-desc">年費 - 金級會員</span>
            </div>
            <span class="payment-amount">$12,000</span>
          </div>
          <div class="payment-item">
            <div class="payment-info">
              <span class="payment-date">2023-07-01</span>
              <span class="payment-desc">年費 - 銀級會員</span>
            </div>
            <span class="payment-amount">$6,000</span>
          </div>
        </div>
      </div>

      <!-- 底部操作按鈕 -->
      <div class="action-footer">
        <van-button type="warning" icon="phone-o" @click="callPhone">撥打電話</van-button>
        <van-button type="primary" icon="edit" @click="editMember">編輯資料</van-button>
      </div>
    </template>

    <van-empty v-else description="會員不存在" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMemberStore } from '@/stores/member'
import { showToast } from 'vant'

const route = useRoute()
const memberStore = useMemberStore()

const member = computed(() => memberStore.getMemberById(route.params.id))

const callPhone = () => {
  if (member.value?.phone) {
    window.location.href = `tel:${member.value.phone.replace(/-/g, '')}`
  }
}

const editMember = () => {
  showToast('編輯功能開發中')
}
</script>

<style scoped>
.detail-page { padding: 0; background: var(--color-gray-100); }

.profile-header {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  padding: 24px 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-avatar { width: 72px; height: 72px; border-radius: 16px; border: 3px solid rgba(255,255,255,0.3); }
.profile-info { color: white; }
.profile-name { font-size: 20px; font-weight: 600; margin-bottom: 8px; }
.profile-tags { display: flex; gap: 8px; }

.card { margin: 12px; }

.payment-list { display: flex; flex-direction: column; gap: 10px; }
.payment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: var(--color-gray-50);
  border-radius: 8px;
}
.payment-info { display: flex; flex-direction: column; }
.payment-date { font-size: 11px; color: var(--color-gray-400); }
.payment-desc { font-size: 13px; color: var(--color-gray-700); }
.payment-amount { font-weight: 600; color: var(--color-success); }

.action-footer {
  position: fixed;
  bottom: 60px;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background: white;
  display: flex;
  gap: 12px;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
}
.action-footer .van-button { flex: 1; }
</style>
