<template>
  <div class="page reports-page">
    <van-nav-bar title="報表統計" />

    <div class="charts-container">
      <canvas id="monthly-chart"></canvas>
      <canvas id="category-chart" style="margin-top:24px;"></canvas>
    </div>

    <van-cell-group title="收入明細">
      <div class="detail-controls">
        <van-field v-model="filterMonth" placeholder="YYYY-MM" label="月份" />
        <van-button size="small" type="primary" @click="loadDetails">查詢</van-button>
      </div>
      <div v-if="details.length === 0" class="van-empty" style="padding: 16px;">
        <van-empty description="無資料" />
      </div>
      <div v-else class="details-list">
        <div v-for="item in details" :key="item.id" class="detail-item">
          <span>{{ item.created_at.split('T')[0] }}</span>
          <span>{{ item.description }}</span>
          <span>{{ item.related_type || '其他' }}</span>
          <span>{{ item.amount }}</span>
        </div>
      </div>
    </van-cell-group>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'
import { paymentApi } from '@/services/api'
import { showToast } from 'vant'

const monthlyChart = ref(null)
const categoryChart = ref(null)
const details = ref([])
const filterMonth = ref('')

const renderMonthly = (data) => {
  const ctx = document.getElementById('monthly-chart').getContext('2d')
  if (monthlyChart.value) monthlyChart.value.destroy()
  monthlyChart.value = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.month),
      datasets: [{ label: '收入', data: data.map(d => d.total), backgroundColor: '#409eff' }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  })
}

const renderCategory = (cats) => {
  const ctx = document.getElementById('category-chart').getContext('2d')
  if (categoryChart.value) categoryChart.value.destroy()
  categoryChart.value = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: Object.keys(cats),
      datasets: [{ data: Object.values(cats), backgroundColor: ['#67c23a','#e6a23c','#909399'] }]
    }
  })
}

const loadReport = async () => {
  try {
    const res = await paymentApi.getReport({ community_id: 1 })
    renderMonthly(res.monthlyTotals)
    renderCategory(res.categoryTotals)
  } catch (e) {
    showToast('無法取得報表')
  }
}

const loadDetails = async () => {
  if (!filterMonth.value) {
    details.value = []
    return
  }
  try {
    const start = filterMonth.value + '-01'
    const end = filterMonth.value + '-31'
    const res = await paymentApi.getReport({ community_id: 1, start, end })
    details.value = res.details || []
  } catch (e) {
    showToast('查詢失敗')
  }
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.reports-page { padding: 0; background: var(--color-gray-100); }
.charts-container { padding: 12px; }
.charts-container canvas { width: 100%; height: 220px; }
.detail-controls { display: flex; gap: 8px; padding: 12px; }
.details-list { padding: 0 12px; }
.detail-item { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #eee; font-size: 13px; }
</style>
