<template>
  <div class="page reports-page">
    <van-nav-bar title="財務報表" />

    <!-- 總覽摘要卡片 -->
    <div class="summary-section">
      <div class="summary-title">收支總覽</div>
      <div class="summary-cards">
        <div class="summary-card">
          <div class="summary-label">總收入</div>
          <div class="summary-value green">{{ formatCurrency(summaryData.totalPaid) }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">待收款</div>
          <div class="summary-value orange">{{ formatCurrency(summaryData.totalPending) }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">總帳單數</div>
          <div class="summary-value">{{ summaryData.totalCount }}</div>
        </div>
      </div>
      <!-- 分類小計 -->
      <div class="category-summary">
        <div v-for="(val, key) in categoryTotals" :key="key" class="cat-item">
          <span class="cat-dot" :style="{ background: catColor(key) }"></span>
          <span class="cat-label">{{ typeMap[key] || key }}</span>
          <span class="cat-value">{{ formatCurrency(val) }}</span>
        </div>
      </div>
    </div>

    <!-- 圖表區 -->
    <div class="charts-section">
      <div class="section-title">月度收入趨勢</div>
      <div class="chart-wrapper">
        <canvas id="monthly-chart"></canvas>
      </div>
      <div class="section-title" style="margin-top: 20px;">收入分類佔比</div>
      <div class="chart-wrapper pie-wrapper">
        <canvas id="category-chart"></canvas>
      </div>
    </div>

    <!-- 財務明細表格 -->
    <div class="table-section">
      <div class="section-title">財務明細</div>
      <div class="table-controls">
        <van-field v-model="filterMonth" placeholder="YYYY-MM" label="月份" class="month-input" />
        <van-button size="small" type="primary" @click="loadDetails">查詢</van-button>
        <van-button size="small" type="success" icon="down" @click="exportCSV">導出 CSV</van-button>
      </div>

      <div v-if="!filterMonth && details.length === 0" class="empty-hint">
        <van-icon name="info-o" /> 請選擇月份後點擊查詢
      </div>
      <div v-else-if="details.length === 0" style="padding: 16px;">
        <van-empty description="該月份無資料" />
      </div>
      <div v-else class="table-container">
        <table class="report-table">
          <thead>
            <tr>
              <th class="col-seq">#</th>
              <th class="col-date">日期</th>
              <th class="col-member">會員</th>
              <th class="col-desc">描述</th>
              <th class="col-type">分類</th>
              <th class="col-method">支付方式</th>
              <th class="col-status">狀態</th>
              <th class="col-amount">金額</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in details" :key="item.id" :class="{ 'row-paid': item.status === 'paid', 'row-pending': item.status === 'pending' }">
              <td class="col-seq">{{ idx + 1 }}</td>
              <td class="col-date">{{ formatDate(item.created_at) }}</td>
              <td class="col-member">{{ item.username || '-' }}</td>
              <td class="col-desc">{{ item.description }}</td>
              <td class="col-type"><span class="type-badge" :style="{ background: catColor(item.related_type) }">{{ typeMap[item.related_type] || '其他' }}</span></td>
              <td class="col-method">{{ item.method || '-' }}</td>
              <td class="col-status"><span :class="['status-badge', item.status]">{{ statusMap[item.status] || item.status }}</span></td>
              <td class="col-amount">{{ formatCurrency(item.amount) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td colspan="5">合計（{{ details.length }} 筆）</td>
              <td>已收：{{ paidCount }} 筆</td>
              <td>待收：{{ pendingCount }} 筆</td>
              <td class="col-amount">{{ formatCurrency(detailsTotal) }}</td>
            </tr>
            <tr class="sub-total-row">
              <td colspan="5"></td>
              <td class="green-text">已收金額</td>
              <td></td>
              <td class="col-amount green-text">{{ formatCurrency(paidTotal) }}</td>
            </tr>
            <tr class="sub-total-row">
              <td colspan="5"></td>
              <td class="orange-text">待收金額</td>
              <td></td>
              <td class="col-amount orange-text">{{ formatCurrency(pendingTotal) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- 月度匯總小表 -->
      <div v-if="monthlyTotals.length > 0" class="monthly-summary">
        <div class="section-title">月度匯總</div>
        <table class="report-table compact">
          <thead>
            <tr>
              <th>月份</th>
              <th class="col-amount">金額</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in monthlyTotals" :key="m.month">
              <td>{{ m.month }}</td>
              <td class="col-amount">{{ formatCurrency(m.total) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td>年度合計</td>
              <td class="col-amount">{{ formatCurrency(monthlyGrandTotal) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import Chart from 'chart.js/auto'
import { paymentApi } from '@/services/api'
import { showToast } from 'vant'

const monthlyChart = ref(null)
const categoryChart = ref(null)
const details = ref([])
const monthlyTotals = ref([])
const categoryTotals = ref({})
const filterMonth = ref('')

const typeMap = { membership: '會費', event: '活動費', other: '其他' }
const statusMap = { pending: '待繳費', paid: '已繳費' }
const catColors = { membership: '#67c23a', event: '#e6a23c', other: '#909399' }
const catColor = (type) => catColors[type] || catColors.other

const formatCurrency = (value) => {
  if (value == null || isNaN(value)) return '$0'
  return `$${Number(value).toLocaleString('en-US')}`
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return dateString.split('T')[0]
}

const detailsTotal = computed(() => details.value.reduce((s, d) => s + (d.amount || 0), 0))
const paidTotal = computed(() => details.value.filter(d => d.status === 'paid').reduce((s, d) => s + (d.amount || 0), 0))
const pendingTotal = computed(() => details.value.filter(d => d.status === 'pending').reduce((s, d) => s + (d.amount || 0), 0))
const paidCount = computed(() => details.value.filter(d => d.status === 'paid').length)
const pendingCount = computed(() => details.value.filter(d => d.status === 'pending').length)
const monthlyGrandTotal = computed(() => monthlyTotals.value.reduce((s, m) => s + (m.total || 0), 0))

const summaryData = computed(() => {
  const paid = Object.values(categoryTotals.value).reduce((s, v) => s + v, 0)
  return {
    totalPaid: paid,
    totalPending: pendingTotal.value,
    totalCount: details.value.length || '-',
  }
})

const renderMonthly = (data) => {
  const ctx = document.getElementById('monthly-chart')?.getContext('2d')
  if (!ctx) return
  if (monthlyChart.value) monthlyChart.value.destroy()
  monthlyChart.value = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.month),
      datasets: [{ label: '收入 ($)', data: data.map(d => d.total), backgroundColor: '#409eff', borderRadius: 4 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
    },
  })
}

const renderCategory = (cats) => {
  const ctx = document.getElementById('category-chart')?.getContext('2d')
  if (!ctx) return
  if (categoryChart.value) categoryChart.value.destroy()
  const labels = Object.keys(cats).map(k => typeMap[k] || k)
  categoryChart.value = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data: Object.values(cats), backgroundColor: ['#67c23a', '#e6a23c', '#909399'], borderWidth: 2 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
    },
  })
}

const loadReport = async () => {
  try {
    const res = await paymentApi.getReport({ community_id: 1 })
    monthlyTotals.value = res.monthlyTotals || []
    categoryTotals.value = res.categoryTotals || {}
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

const exportCSV = () => {
  const params = { community_id: 1 }
  if (filterMonth.value) {
    params.start = filterMonth.value + '-01'
    params.end = filterMonth.value + '-31'
  }
  paymentApi.exportCSV(params)
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.reports-page {
  padding: 0;
  background: var(--color-gray-100);
  padding-bottom: 24px;
}

/* 摘要區 */
.summary-section {
  background: white;
  margin: 12px;
  border-radius: 12px;
  padding: 16px;
}
.summary-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}
.summary-cards {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}
.summary-card {
  flex: 1;
  background: var(--color-gray-50);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}
.summary-label { font-size: 12px; color: var(--color-gray-500); margin-bottom: 4px; }
.summary-value { font-size: 20px; font-weight: 700; color: #333; }
.summary-value.green { color: #67c23a; }
.summary-value.orange { color: #e6a23c; }

.category-summary {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.cat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.cat-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.cat-label { color: var(--color-gray-600); }
.cat-value { font-weight: 600; color: #333; }

/* 圖表區 */
.charts-section {
  background: white;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}
.chart-wrapper { height: 200px; }
.pie-wrapper { height: 220px; }

/* 表格區 */
.table-section {
  background: white;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 16px;
}
.table-controls {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}
.month-input { flex: 1; }
.empty-hint {
  text-align: center;
  padding: 24px;
  color: var(--color-gray-500);
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.report-table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
  font-size: 13px;
}
.report-table th,
.report-table td {
  padding: 10px 8px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}
.report-table thead th {
  background: var(--color-gray-50);
  font-weight: 600;
  color: var(--color-gray-600);
  position: sticky;
  top: 0;
}
.report-table tbody tr:hover { background: #f9fbff; }

.col-seq { width: 36px; text-align: center; color: var(--color-gray-400); }
.col-date { width: 90px; }
.col-member { width: 80px; }
.col-desc { min-width: 100px; }
.col-type { width: 70px; }
.col-method { width: 70px; }
.col-status { width: 70px; }
.col-amount { width: 90px; text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  color: white;
  font-size: 11px;
  font-weight: 500;
}
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}
.status-badge.paid { background: #e8f5e9; color: #2e7d32; }
.status-badge.pending { background: #fff3e0; color: #e65100; }

.row-paid td { color: #333; }
.row-pending td { color: #666; }

.total-row {
  background: var(--color-gray-50);
  font-weight: 700;
  font-size: 14px;
}
.total-row td { border-top: 2px solid #ddd; border-bottom: none; }
.sub-total-row td {
  border-bottom: none;
  font-size: 13px;
  font-weight: 600;
  padding-top: 4px;
  padding-bottom: 4px;
}
.green-text { color: #67c23a; }
.orange-text { color: #e6a23c; }

/* 月度匯總 */
.monthly-summary {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}
.report-table.compact { min-width: auto; }
.report-table.compact th,
.report-table.compact td { padding: 8px 12px; }
</style>
