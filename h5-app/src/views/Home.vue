<template>
  <div class="page home-page">
    <!-- 頂部歡迎區 -->
    <div class="welcome-card">
      <div class="welcome-info">
        <h1>會籍管理系統</h1>
        <p>歡迎回來，管理員</p>
      </div>
      <van-icon name="bell" size="24" color="#fff" badge="3" />
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-icon"><van-icon name="friends-o" size="20" /></div>
        <div class="kpi-label">會員總數</div>
        <div class="kpi-value">{{ stats.total }}</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-icon"><van-icon name="passed" size="20" /></div>
        <div class="kpi-label">有效會員</div>
        <div class="kpi-value">{{ stats.active }}</div>
      </div>
      <div class="kpi-card orange">
        <div class="kpi-icon"><van-icon name="clock-o" size="20" /></div>
        <div class="kpi-label">待審核</div>
        <div class="kpi-value">{{ stats.pending }}</div>
      </div>
      <div class="kpi-card gold">
        <div class="kpi-icon"><van-icon name="warning-o" size="20" /></div>
        <div class="kpi-label">已過期</div>
        <div class="kpi-value">{{ stats.expired }}</div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="card">
      <div class="card-title"><van-icon name="apps-o" /> 快捷操作</div>
      <van-grid :column-num="4" :border="false">
        <van-grid-item icon="add-o" text="新增會員" @click="showAddMember = true" />
        <van-grid-item icon="scan" text="掃碼簽到" />
        <van-grid-item icon="bill-o" text="收款確認" to="/admin/payments" />
        <van-grid-item icon="chart-trending-o" text="數據報表" />
      </van-grid>
    </div>

    <!-- 近期待處理 -->
    <div class="card">
      <div class="card-title">
        <van-icon name="todo-list-o" /> 待處理事項
        <span class="card-more" @click="$router.push('/admin/members')">查看全部</span>
      </div>
      <van-cell-group :border="false">
        <van-cell
          v-for="item in pendingItems"
          :key="item.id"
          :title="item.name"
          :label="item.action"
          is-link
          @click="$router.push(`/admin/member/${item.id}`)"
        >
          <template #icon>
            <img :src="item.avatar" class="cell-avatar" />
          </template>
          <template #value>
            <span :class="['status-tag', item.status]">{{ item.statusText }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 新增會員彈窗 -->
    <van-popup v-model:show="showAddMember" position="bottom" round :style="{ height: '70%' }">
      <div class="popup-header">
        <span>新增會員</span>
        <van-icon name="cross" @click="showAddMember = false" />
      </div>
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field v-model="form.name" label="姓名" placeholder="請輸入會員姓名" :rules="[{ required: true }]" />
          <van-field v-model="form.phone" label="電話" type="tel" placeholder="請輸入聯絡電話" :rules="[{ required: true }]" />
          <van-field v-model="form.email" label="郵箱" type="email" placeholder="請輸入電子郵件" />
          <van-field v-model="form.company" label="公司" placeholder="請輸入公司名稱" />
          <van-field
            v-model="form.membershipText"
            is-link
            readonly
            label="會籍類型"
            placeholder="請選擇會籍類型"
            @click="showPicker = true"
          />
        </van-cell-group>
        <div class="popup-footer">
          <van-button round block type="primary" native-type="submit">確認新增</van-button>
        </div>
      </van-form>
    </van-popup>

    <!-- 會籍選擇器 -->
    <van-popup v-model:show="showPicker" position="bottom">
      <van-picker
        :columns="membershipOptions"
        @confirm="onPickerConfirm"
        @cancel="showPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMemberStore } from '@/stores/member'
import { showToast } from 'vant'

const memberStore = useMemberStore()
const stats = computed(() => memberStore.stats)

const showAddMember = ref(false)
const showPicker = ref(false)

const form = ref({
  name: '',
  phone: '',
  email: '',
  company: '',
  membership: '',
  membershipText: ''
})

const membershipOptions = [
  { text: '圈委', value: 'committee' },
  { text: '圈民', value: 'citizen' },
  { text: '圈友', value: 'friend' }
]

const pendingItems = computed(() => {
  return memberStore.members
    .filter(m => m.status === 'pending' || m.status === 'expired')
    .slice(0, 3)
    .map(m => ({
      ...m,
      action: m.status === 'pending' ? '新會員申請審核' : '會籍已過期，待續費',
      statusText: memberStore.statusTypes[m.status]?.label || m.status
    }))
})

const onPickerConfirm = ({ selectedOptions }) => {
  form.value.membership = selectedOptions[0].value
  form.value.membershipText = selectedOptions[0].text
  showPicker.value = false
}

const onSubmit = () => {
  showToast('會員新增成功')
  showAddMember.value = false
  form.value = { name: '', phone: '', email: '', company: '', membership: '', membershipText: '' }
}

onMounted(() => {
  memberStore.fetchMembers()
})
</script>

<style scoped>
.home-page {
  padding-top: 0;
}

.welcome-card {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  padding: 24px 16px;
  padding-top: calc(24px + var(--safe-area-top));
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: -16px -16px 16px -16px;
}

.welcome-info h1 {
  color: white;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.welcome-info p {
  color: rgba(255,255,255,0.8);
  font-size: 13px;
}

.kpi-card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.kpi-icon {
  color: var(--color-primary);
  margin-bottom: 8px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-more {
  margin-left: auto;
  font-size: 12px;
  color: var(--color-info);
  font-weight: normal;
}

.cell-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  margin-right: 10px;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--color-gray-100);
}

.popup-footer {
  padding: 16px;
}
</style>
