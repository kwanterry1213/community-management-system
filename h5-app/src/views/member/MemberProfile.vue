<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="header-bg"></div>
      <div class="header-content">
        <img :src="avatarUrl" class="profile-avatar" />
        <div class="profile-info">
          <h2 class="profile-name">{{ displayName }}</h2>
          <span class="profile-level">{{ authStore.levelInfo.icon }} {{ authStore.levelInfo.name }}</span>
        </div>
      </div>
    </div>

    <van-cell-group inset title="個人資料" class="section">
      <van-cell title="姓名" :value="authStore.currentUser?.username || '—'" />
      <van-cell title="電話" :value="authStore.currentUser?.phone_number || '—'" />
      <van-cell title="電子郵件" :value="authStore.currentUser?.email || '—'" />
      <van-cell title="簡介" :value="authStore.currentUser?.bio || '—'" />
      <van-cell title="編輯資料" is-link @click="showEditPopup = true" />
    </van-cell-group>

    <van-cell-group inset title="帳號設定" class="section">
      <van-cell title="修改密碼" is-link @click="showPasswordPopup = true" />
      <van-cell title="通知設定" is-link @click="showNotifPopup = true" />
      <van-cell v-if="authStore.isAdmin" title="進入管理後台" is-link to="/admin" icon="manager-o" />
      <van-cell title="意見回饋" is-link @click="showFeedbackPopup = true" />
    </van-cell-group>

    <van-cell-group inset title="其他" class="section">
      <van-cell title="使用條款" is-link />
      <van-cell title="隱私政策" is-link />
      <van-cell title="關於我們" is-link />
    </van-cell-group>

    <div class="logout-section">
      <van-button type="danger" plain block round size="large" @click="handleLogout">登出</van-button>
    </div>

    <!-- 編輯資料 -->
    <van-popup v-model:show="showEditPopup" position="bottom" round :style="{ minHeight: '50%' }">
      <div class="popup-content">
        <div class="popup-header"><h3>編輯個人資料</h3><van-icon name="cross" @click="showEditPopup = false" /></div>
        <van-form @submit="saveProfile">
          <van-cell-group inset>
            <van-field v-model="editForm.username" label="姓名" placeholder="請輸入姓名" />
            <van-field v-model="editForm.phone" label="電話" placeholder="請輸入電話" />
            <van-field v-model="editForm.email" label="電子郵件" placeholder="請輸入信箱" />
            <van-field v-model="editForm.bio" label="簡介" type="textarea" placeholder="請輸入簡介" rows="2" autosize />
          </van-cell-group>
          <div style="padding: 16px;"><van-button type="primary" block round native-type="submit">儲存</van-button></div>
        </van-form>
      </div>
    </van-popup>

    <!-- 修改密碼 -->
    <van-popup v-model:show="showPasswordPopup" position="bottom" round :style="{ minHeight: '40%' }">
      <div class="popup-content">
        <div class="popup-header"><h3>修改密碼</h3><van-icon name="cross" @click="showPasswordPopup = false" /></div>
        <van-form @submit="changePassword">
          <van-cell-group inset>
            <van-field v-model="passwordForm.oldPassword" type="password" label="舊密碼" placeholder="請輸入舊密碼" />
            <van-field v-model="passwordForm.newPassword" type="password" label="新密碼" placeholder="請輸入新密碼" />
            <van-field v-model="passwordForm.confirmPassword" type="password" label="確認密碼" placeholder="請再次輸入新密碼" />
          </van-cell-group>
          <div style="padding: 16px;"><van-button type="primary" block round native-type="submit">確認修改</van-button></div>
        </van-form>
      </div>
    </van-popup>

    <!-- 通知設定 -->
    <van-popup v-model:show="showNotifPopup" position="bottom" round :style="{ minHeight: '30%' }">
      <div class="popup-content">
        <div class="popup-header"><h3>通知設定</h3><van-icon name="cross" @click="showNotifPopup = false" /></div>
        <van-cell-group inset>
          <van-cell title="活動提醒"><template #right-icon><van-switch v-model="notifSettings.events" size="20" /></template></van-cell>
          <van-cell title="公告通知"><template #right-icon><van-switch v-model="notifSettings.announcements" size="20" /></template></van-cell>
          <van-cell title="繳費提醒"><template #right-icon><van-switch v-model="notifSettings.payments" size="20" /></template></van-cell>
        </van-cell-group>
      </div>
    </van-popup>

    <!-- 意見回饋 -->
    <van-popup v-model:show="showFeedbackPopup" position="bottom" round :style="{ minHeight: '35%' }">
      <div class="popup-content">
        <div class="popup-header"><h3>意見回饋</h3><van-icon name="cross" @click="showFeedbackPopup = false" /></div>
        <van-cell-group inset>
          <van-field v-model="feedbackText" type="textarea" placeholder="請告訴我們您的建議..." rows="4" autosize />
        </van-cell-group>
        <div style="padding: 16px;"><van-button type="primary" block round @click="submitFeedback">提交回饋</van-button></div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const displayName = computed(() => authStore.currentUser?.username || '會員')
const avatarUrl = computed(() =>
  authStore.currentUser?.profile_picture_url ||
  `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName.value)}&background=1a365d&color=fff&size=128`
)

const showEditPopup = ref(false)
const showPasswordPopup = ref(false)
const showNotifPopup = ref(false)
const showFeedbackPopup = ref(false)

const editForm = ref({ username: '', phone: '', email: '', bio: '' })
const passwordForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })
const notifSettings = ref({ events: true, announcements: true, payments: true })
const feedbackText = ref('')

onMounted(() => {
  const u = authStore.currentUser
  if (u) {
    editForm.value = {
      username: u.username || '',
      phone: u.phone_number || '',
      email: u.email || '',
      bio: u.bio || '',
    }
  }
})

const saveProfile = async () => {
  const result = await authStore.updateProfile(editForm.value)
  if (result.success) {
    showToast({ type: 'success', message: '已更新' })
    showEditPopup.value = false
  } else {
    showToast({ type: 'fail', message: result.message })
  }
}

const changePassword = () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showToast({ type: 'fail', message: '兩次密碼不一致' })
    return
  }
  showToast({ type: 'success', message: '密碼已更新' })
  showPasswordPopup.value = false
  passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
}

const submitFeedback = () => {
  if (!feedbackText.value.trim()) { showToast('請輸入回饋內容'); return }
  showToast({ type: 'success', message: '感謝您的回饋！' })
  feedbackText.value = ''
  showFeedbackPopup.value = false
}

const handleLogout = () => {
  showDialog({ title: '登出', message: '確定要登出嗎？', showCancelButton: true }).then(() => {
    authStore.logout()
    router.replace('/login')
  }).catch(() => {})
}
</script>

<style scoped>
.profile-page { min-height: 100vh; background: #f5f7fa; padding-bottom: 90px; }
.profile-header { position: relative; height: 180px; background: linear-gradient(135deg, #1a365d, #2c5282); }
.header-content { position: absolute; bottom: -40px; left: 0; right: 0; display: flex; flex-direction: column; align-items: center; }
.profile-avatar { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.profile-info { text-align: center; margin-top: 8px; }
.profile-name { font-size: 20px; font-weight: 700; color: #1a202c; margin: 0; }
.profile-level { font-size: 13px; color: #718096; }
.section { margin-top: 16px; }
.section:first-of-type { margin-top: 56px; }
.logout-section { padding: 24px 16px; }
.popup-content { padding: 16px; }
.popup-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.popup-header h3 { margin: 0; font-size: 18px; font-weight: 600; }
</style>
