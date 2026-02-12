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

      <!-- 基本資料卡片 -->
      <div class="card">
        <div class="card-title"><van-icon name="user-o" /> 基本資料</div>
        <van-cell-group :border="false">
          <van-cell title="會員編號" :value="member.membershipNo || String(member.id)" />
          <van-cell title="聯絡電話" :value="member.phone" is-link @click="callPhone" />
          <van-cell title="電子郵件" :value="member.email" />
          <van-cell title="簡介" :value="member.bio || '—'" />
        </van-cell-group>
      </div>

      <!-- 會籍資訊卡片 -->
      <div class="card">
        <div class="card-title"><van-icon name="certificate" /> 會籍資訊</div>
        <van-cell-group :border="false">
          <van-cell title="會籍類型">
            <template #value>
              <span :class="['membership-badge', member.level]">
                {{ memberStore.membershipTypes[member.level]?.label || member.level }}
              </span>
            </template>
          </van-cell>
          <van-cell title="加入日期" :value="member.joinDate" />
          <van-cell title="到期日期" :value="member.expiryDate || '—'" />
          <van-cell title="會籍狀態">
            <template #value>
              <span :class="['status-tag', member.status]">
                {{ memberStore.statusTypes[member.status]?.label || member.status }}
              </span>
            </template>
          </van-cell>
        </van-cell-group>
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

      <!-- 底部操作按鈕 -->
      <div class="action-footer">
        <van-button type="warning" icon="phone-o" @click="callPhone">撥打電話</van-button>
        <van-button type="primary" icon="edit" @click="openEditPopup">編輯會籍</van-button>
      </div>

      <!-- 編輯會籍彈窗 -->
      <van-popup v-model:show="showEditPopup" position="bottom" round :style="{ height: '50%' }">
        <div class="popup-header">
          <span>編輯會籍</span>
          <van-icon name="cross" @click="showEditPopup = false" />
        </div>
        <van-form @submit="saveMembership">
          <van-cell-group inset>
            <van-field
              v-model="editForm.roleText"
              is-link
              readonly
              label="角色權限"
              placeholder="請選擇角色"
              @click="showRolePicker = true"
            />
            <van-field
              v-model="editForm.statusText"
              is-link
              readonly
              label="會籍狀態"
              placeholder="請選擇狀態"
              @click="showStatusPicker = true"
            />
            <van-field
              v-model="editForm.expiryDate"
              label="到期日"
              placeholder="YYYY-MM-DD"
            />
          </van-cell-group>
          <div class="popup-footer">
            <van-button round block type="primary" native-type="submit" :loading="saving">儲存變更</van-button>
          </div>
        </van-form>
      </van-popup>

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
    </template>

    <van-empty v-else description="會員不存在" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMemberStore } from '@/stores/member'
import { paymentApi, membershipApi } from '@/services/api'
import { showToast } from 'vant'

const route = useRoute()
const memberStore = useMemberStore()

const member = computed(() => memberStore.getMemberById(route.params.id))
const payments = ref([])
const showEditPopup = ref(false)
const showRolePicker = ref(false)
const showStatusPicker = ref(false)
const saving = ref(false)

const editForm = ref({
  role: '',
  roleText: '',
  status: '',
  statusText: '',
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

const openEditPopup = () => {
  if (!member.value) return
  
  // 查找對應的 role 和 status
  // 由於 store 已經轉換過 role -> level, 我們需要反向查找或直接用 store 的 level 映射
  // member.level: admin, committee, citizen, friend
  // member.status: active, pending, expired
  
  const levelToRole = {
    'admin': 'admin',
    'committee': 'staff',
    'citizen': 'member',
    'friend': 'visitor'
  }
  
  const currentRole = levelToRole[member.value.level] || 'visitor'
  const currentRoleOption = roleOptions.find(o => o.value === currentRole)
  
  const currentStatusOption = statusOptions.find(o => o.value === member.value.status)

  editForm.value = {
    role: currentRole,
    roleText: currentRoleOption?.text || '圈友',
    status: member.value.status,
    statusText: currentStatusOption?.text || member.value.status,
    expiryDate: member.value.expiryDate !== '—' ? member.value.expiryDate : ''
  }
  showEditPopup.value = true
}

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

const saveMembership = async () => {
  if (!member.value.membershipId) {
    showToast('無法找到會籍 ID')
    return
  }
  
  saving.value = true
  try {
    // role 需要同時更新 level
    const roleToLevel = {
      'admin': 'admin',
      'staff': 'committee',
      'member': 'citizen',
      'visitor': 'friend'
    }
    
    await membershipApi.update(member.value.membershipId, {
      role: editForm.value.role,
      level: roleToLevel[editForm.value.role], // 同步更新 level
      status: editForm.value.status,
      expires_at: editForm.value.expiryDate ? editForm.value.expiryDate + ' 23:59:59' : null
    })
    
    showToast('更新成功')
    showEditPopup.value = false
    await memberStore.fetchMembers() // 重新載入列表
  } catch (err) {
    showToast(err.response?.data?.detail || '更新失敗')
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
