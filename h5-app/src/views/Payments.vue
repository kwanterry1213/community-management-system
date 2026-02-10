<template>
  <div class="page payments-page">
    <van-nav-bar title="繳費管理" />

    <!-- 收款統計 -->
    <div class="stats-row">
      <div class="stat-card"><div class="stat-label">本月應收</div><div class="stat-value">$245,000</div></div>
      <div class="stat-card green"><div class="stat-label">已收款</div><div class="stat-value">$189,200</div></div>
      <div class="stat-card orange"><div class="stat-label">待收款</div><div class="stat-value">$55,800</div></div>
    </div>

    <!-- 分類標籤 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="待繳費" name="pending" badge="42" />
      <van-tab title="已繳費" name="paid" />
      <van-tab title="逾期未繳" name="overdue" badge="8" />
    </van-tabs>

    <!-- 繳費列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <div class="payment-list">
        <div v-for="item in paymentList" :key="item.id" class="payment-card">
          <div class="payment-header">
            <img :src="item.avatar" class="payment-avatar" />
            <div class="payment-info">
              <span class="payment-name">{{ item.name }}</span>
              <span class="payment-id">{{ item.id }}</span>
            </div>
            <span :class="['status-tag', item.statusClass]">{{ item.statusText }}</span>
          </div>
          <div class="payment-body">
            <div class="payment-row"><span>會籍類型</span><span>{{ item.membershipLabel }}</span></div>
            <div class="payment-row"><span>應繳金額</span><span class="amount">{{ item.amount }}</span></div>
            <div class="payment-row"><span>繳費期限</span><span>{{ item.dueDate }}</span></div>
          </div>
          <div class="payment-actions">
            <van-button size="small" type="success" icon="success">確認收款</van-button>
            <van-button size="small" plain icon="bell">發送提醒</van-button>
          </div>
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('pending')
const refreshing = ref(false)

const paymentList = ref([
  { id: 'M-2024-0160', name: '王建國', avatar: 'https://ui-avatars.com/api/?name=王建國&background=e53e3e&color=fff', membershipLabel: '普通會員', amount: '$3,600', dueDate: '2026-01-15', statusClass: 'expired', statusText: '逾期' },
  { id: 'M-2024-0164', name: '周雅婷', avatar: 'https://ui-avatars.com/api/?name=周雅婷&background=dd6b20&color=fff', membershipLabel: '普通會員', amount: '$3,600', dueDate: '2026-02-28', statusClass: 'pending', statusText: '即將到期' },
  { id: 'M-2024-0170', name: '蔡明翰', avatar: 'https://ui-avatars.com/api/?name=蔡明翰&background=3182ce&color=fff', membershipLabel: '銀級會員', amount: '$6,000', dueDate: '2026-03-15', statusClass: 'pending', statusText: '待繳' },
  { id: 'M-2024-0175', name: '劉怡君', avatar: 'https://ui-avatars.com/api/?name=劉怡君&background=d69e2e&color=fff', membershipLabel: '金級會員', amount: '$12,000', dueDate: '2026-03-31', statusClass: 'pending', statusText: '待繳' },
])

const onRefresh = () => { setTimeout(() => { refreshing.value = false }, 1000) }
</script>

<style scoped>
.payments-page { padding: 0; background: var(--color-gray-100); }

.stats-row { display: flex; gap: 10px; padding: 12px; }
.stat-card { flex: 1; background: white; border-radius: 10px; padding: 12px; text-align: center; }
.stat-card.green .stat-value { color: var(--color-success); }
.stat-card.orange .stat-value { color: var(--color-warning); }
.stat-label { font-size: 11px; color: var(--color-gray-500); margin-bottom: 4px; }
.stat-value { font-size: 18px; font-weight: 700; color: var(--color-gray-800); }

.payment-list { padding: 12px; }
.payment-card { background: white; border-radius: 12px; padding: 14px; margin-bottom: 10px; }
.payment-header { display: flex; align-items: center; margin-bottom: 12px; }
.payment-avatar { width: 40px; height: 40px; border-radius: 10px; margin-right: 10px; }
.payment-info { flex: 1; }
.payment-name { display: block; font-weight: 600; font-size: 14px; }
.payment-id { font-size: 11px; color: var(--color-gray-400); }
.payment-body { background: var(--color-gray-50); border-radius: 8px; padding: 10px; margin-bottom: 12px; }
.payment-row { display: flex; justify-content: space-between; font-size: 13px; padding: 4px 0; }
.payment-row .amount { font-weight: 600; color: var(--color-primary); }
.payment-actions { display: flex; gap: 10px; }
.payment-actions .van-button { flex: 1; }
</style>
