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
            <span :class="['membership-badge', member.level]">
              {{ memberStore.membershipTypes[member.level]?.label || member.level }}
            </span>
            <span :class="['status-tag', member.status]">
              {{ memberStore.statusTypes[member.status]?.label || member.status }}
            </span>
          </div>
        </div>
      </div>

      <!-- 基本資料卡片 (ReadOnly) -->
      <div class="card">
        <div class="card-title"><van-icon name="user-o" /> 基本資料</div>
        <van-cell-group :border="false">
          <van-cell title="會員編號" :value="member.membershipNo || String(member.id)" />
          <van-cell title="聯絡電話" :value="member.phone" is-link @click="callPhone" />
          <van-cell title="電子郵件" :value="member.email" />
          <van-cell title="簡介" :value="member.bio || '—'" />
        </van-cell-group>
      </div>

      <!-- 會籍資訊卡片 (Direct Edit) -->
      <div class="card">
        <div class="card-title">
          <van-icon name="certificate" /> 會籍資訊 (可編輯)
        </div>
        <van-form @submit="saveDirectly">
          <van-cell-group :border="false">
            <!-- 會籍類型 (Level/Role) -->
            <van-field
              v-model="editForm.roleText"
              is-link
              readonly
              label="會籍類型"
              placeholder="請選擇"
              @click="showRolePicker = true"
            />
            
            <!-- 加入日期 (Joined At) -->
            <van-field
              v-model="editForm.joinDate"
              is-link
              readonly
              label="加入日期"
              placeholder="請選擇"
              @click="showJoinCalendar = true"
            />

            <!-- 到期日期 (Expires At) -->
            <van-field
              v-model="editForm.expiryDate"
              is-link
              readonly
              label="到期日期"
              placeholder="請選擇 (留空為永久)"
              @click="showExpiryCalendar = true"
            />

            <!-- 會籍狀態 (Status) -->
            <van-field
              v-model="editForm.statusText"
              is-link
              readonly
              label="會籍狀態"
              placeholder="請選擇"
              @click="showStatusPicker = true"
            />
          </van-cell-group>
          
          <div style="padding: 16px;">
            <van-button 
                round 
                block 
                type="primary" 
                native-type="submit" 
                :loading="saving"
            >儲存會籍變更</van-button>
          </div>
        </van-form>
      </div>

      <!-- 繳費記錄 -->
      <div class="card">
        <div class="card-title"><van-icon name="bill-o" /> 繳費記錄</div>
        <div class="payment-list">
          <div v-for="p in payments" :key="p.id" class="payment-item">
            <div class="payment-info">
              <span class="payment-date">{{ p.created_at?.split('T')[0] || '—' }}</span>
              <span class="payment-desc">{{ p.description }}</span>
            </div>
            <span class="payment-amount">MOP$ {{ p.amount }}</span>
          </div>
          <div v-if="payments.length === 0" style="text-align: center; padding: 16px; color: #999;">暫無繳費記錄</div>
        </div>
      </div>
      
      <div style="height: 100px;"></div> <!-- Spacer -->

    </template>

    <van-empty v-else description="會員不存在" />

    <!-- Pickers & Calendars -->
    <van-popup v-model:show="showRolePicker" position="bottom">
      <van-picker
        :columns="roleOptions"
        @confirm="onRoleConfirm"
        @cancel="showRolePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showStatusPicker" position="bottom">
      <van-picker
        :columns="statusOptions"
        @confirm="onStatusConfirm"
        @cancel="showStatusPicker = false"
      />
    </van-popup>
    
    <van-calendar 
        v-model:show="showJoinCalendar" 
        @confirm="onJoinDateConfirm" 
        :min-date="minDate"
        :max-date="maxDate"
    />
    
    <van-calendar 
        v-model:show="showExpiryCalendar" 
        @confirm="onExpiryDateConfirm" 
        :min-date="minDate"
        :max-date="maxDate"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMemberStore } from '@/stores/member'
import { paymentApi, membershipApi } from '@/services/api'
import { showToast } from 'vant'

const route = useRoute()
const memberStore = useMemberStore()

const member = computed(() => memberStore.getMemberById(route.params.id))
const payments = ref([])
const saving = ref(false)

const showRolePicker = ref(false)
const showStatusPicker = ref(false)
const showJoinCalendar = ref(false)
const showExpiryCalendar = ref(false)

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const editForm = ref({
  role: '',
  roleText: '',
  status: '',
  statusText: '',
  joinDate: '',
  expiryDate: ''
})

const roleOptions = [
  { text: '管理員', value: 'admin' },
  { text: '圈委', value: 'staff' },
  { text: '圈民', value: 'member' },
  { text: '圈友', value: 'visitor' }
]

const statusOptions = [
  { text: '有效', value: 'active' },
  { text: '待審核', value: 'pending' },
  { text: '已過期', value: 'expired' },
  { text: '已停權', value: 'suspended' }
]

// Initialize form when member data is available
watch(member, (newVal) => {
  if (newVal) initForm(newVal)
}, { immediate: true })

const initForm = (m) => {
  // Role mapping
  const levelToRole = {
    'admin': 'admin',
    'committee': 'staff',
    'citizen': 'member',
    'friend': 'visitor'
  }
  const currentRole = levelToRole[m.level] || 'visitor'
  const currentRoleOption = roleOptions.find(o => o.value === currentRole)
  const currentStatusOption = statusOptions.find(o => o.value === m.status)

  editForm.value = {
    role: currentRole,
    roleText: currentRoleOption?.text || '圈友',
    status: m.status,
    statusText: currentStatusOption?.text || m.status,
    joinDate: m.joinDate,
    expiryDate: m.expiryDate !== '—' ? m.expiryDate : ''
  }
}

onMounted(async () => {
  if (memberStore.members.length === 0) {
    await memberStore.fetchMembers()
  }
  try {
    payments.value = await paymentApi.list({ user_id: parseInt(route.params.id) })
  } catch {}
})

const callPhone = () => {
  if (member.value?.phone) {
    window.location.href = `tel:${member.value.phone.replace(/-/g, '')}`
  }
}

// Picker Handlers
const onRoleConfirm = ({ selectedOptions }) => {
  editForm.value.role = selectedOptions[0].value
  editForm.value.roleText = selectedOptions[0].text
  showRolePicker.value = false
}

const onStatusConfirm = ({ selectedOptions }) => {
  editForm.value.status = selectedOptions[0].value
  editForm.value.statusText = selectedOptions[0].text
  showStatusPicker.value = false
}

const formatDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const onJoinDateConfirm = (date) => {
  editForm.value.joinDate = formatDate(date)
  showJoinCalendar.value = false
}

const onExpiryDateConfirm = (date) => {
  editForm.value.expiryDate = formatDate(date)
  showExpiryCalendar.value = false
}

const saveDirectly = async () => {
  saving.value = true
  try {
    const roleToLevel = {
      'admin': 'admin',
      'staff': 'committee',
      'member': 'citizen',
      'visitor': 'friend'
    }

    const payload = {
      role: editForm.value.role,
      level: roleToLevel[editForm.value.role],
      status: editForm.value.status,
      expires_at: editForm.value.expiryDate ? editForm.value.expiryDate + ' 23:59:59' : null,
      joined_at: editForm.value.joinDate ? editForm.value.joinDate + ' 00:00:00' : null
    }

    if (member.value.membershipId) {
      // Update existing
      await membershipApi.update(member.value.membershipId, payload)
      showToast('更新成功')
    } else {
      // Create new
      await membershipApi.create({
        ...payload,
        user_id: member.value.id,
        community_id: 1 // Default to 1
      })
      showToast('建立會籍成功')
    }
    
    await memberStore.fetchMembers()
  } catch (err) {
    console.error('Update failed:', err)
    const msg = err.response?.data?.detail || err.message || '更新失敗'
    showToast(msg)
  } finally {
    saving.value = false
  }
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

.card { margin: 12px; border-radius: 12px; overflow: hidden; background: white; }
.card-title {
    padding: 12px 16px;
    font-size: 15px;
    font-weight: 600;
    color: #333;
    border-bottom: 1px solid #f5f5f5;
    background: #fafafa;
}

.payment-list { display: flex; flex-direction: column; gap: 10px; padding: 12px; }
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

:deep(.van-field__label) {
    width: 6em;
}
</style>
