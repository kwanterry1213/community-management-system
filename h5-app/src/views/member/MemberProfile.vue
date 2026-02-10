<template>
  <div class="profile-page">
    <van-nav-bar title="我的" />

    <!-- 用戶卡片 -->
    <div class="user-card">
      <div class="user-info" @click="$router.push('/m/membership')">
        <img :src="currentUser.avatar" class="user-avatar" />
        <div class="user-details">
          <div class="user-name">{{ currentUser.name }}</div>
          <div class="user-level">
            <span class="level-badge" :class="currentUser.level">
              {{ levelInfo.icon }} {{ levelInfo.name }}
            </span>
          </div>
        </div>
        <van-icon name="arrow" color="#c0c4cc" />
      </div>
    </div>

    <!-- 功能選單 -->
    <van-cell-group inset title="帳戶設定">
      <van-cell title="個人資料" icon="user-o" is-link @click="showEditProfile = true" />
      <van-cell title="修改密碼" icon="lock" is-link @click="showChangePassword = true" />
      <van-cell title="綁定手機" icon="phone-o" :value="maskedPhone" is-link />
      <van-cell title="綁定信箱" icon="envelop-o" :value="maskedEmail" is-link />
    </van-cell-group>

    <van-cell-group inset title="通知設定">
      <van-cell title="活動通知" icon="bell">
        <template #right-icon>
          <van-switch v-model="notifications.events" size="20" />
        </template>
      </van-cell>
      <van-cell title="繳費提醒" icon="clock-o">
        <template #right-icon>
          <van-switch v-model="notifications.payment" size="20" />
        </template>
      </van-cell>
      <van-cell title="系統公告" icon="volume-o">
        <template #right-icon>
          <van-switch v-model="notifications.system" size="20" />
        </template>
      </van-cell>
    </van-cell-group>

    <van-cell-group inset title="其他">
      <van-cell title="聯絡客服" icon="service-o" is-link @click="contactService" />
      <van-cell title="意見反饋" icon="comment-o" is-link @click="showFeedback = true" />
      <van-cell title="關於我們" icon="info-o" is-link />
      <van-cell title="使用條款" icon="description" is-link />
    </van-cell-group>

    <!-- 管理員入口（僅圈圈委可見） -->
    <van-cell-group v-if="currentUser.level === 'committee'" inset title="管理功能">
      <van-cell 
        title="進入管理後台" 
        icon="setting-o" 
        is-link 
        @click="$router.push('/admin')"
      >
        <template #label>
          <span style="color: #d69e2e;">圈圈委專屬</span>
        </template>
      </van-cell>
    </van-cell-group>

    <div class="logout-section">
      <van-button type="default" block round @click="logout">
        登出帳號
      </van-button>
    </div>

    <div class="version-info">
      版本 1.0.0
    </div>

    <!-- 編輯個人資料 -->
    <van-popup v-model:show="showEditProfile" position="bottom" round style="height: 70%">
      <div class="popup-content">
        <div class="popup-header">
          <span>編輯個人資料</span>
          <van-icon name="cross" @click="showEditProfile = false" />
        </div>
        <van-form @submit="saveProfile">
          <van-cell-group inset>
            <van-field v-model="editForm.name" label="姓名" placeholder="請輸入姓名" />
            <van-field v-model="editForm.phone" label="電話" placeholder="請輸入電話" />
            <van-field v-model="editForm.email" label="信箱" placeholder="請輸入信箱" />
            <van-field v-model="editForm.company" label="公司" placeholder="請輸入公司名稱" />
            <van-field v-model="editForm.title" label="職稱" placeholder="請輸入職稱" />
            <van-field
              v-model="editForm.address"
              label="地址"
              type="textarea"
              rows="2"
              placeholder="請輸入聯絡地址"
            />
          </van-cell-group>
          <div style="padding: 16px;">
            <van-button type="primary" block round native-type="submit">儲存</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 修改密碼 -->
    <van-popup v-model:show="showChangePassword" position="bottom" round style="height: 50%">
      <div class="popup-content">
        <div class="popup-header">
          <span>修改密碼</span>
          <van-icon name="cross" @click="showChangePassword = false" />
        </div>
        <van-form @submit="changePassword">
          <van-cell-group inset>
            <van-field v-model="passwordForm.current" type="password" label="目前密碼" placeholder="請輸入目前密碼" />
            <van-field v-model="passwordForm.new" type="password" label="新密碼" placeholder="請輸入新密碼" />
            <van-field v-model="passwordForm.confirm" type="password" label="確認密碼" placeholder="請再次輸入新密碼" />
          </van-cell-group>
          <div style="padding: 16px;">
            <van-button type="primary" block round native-type="submit">確認修改</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 意見反饋 -->
    <van-popup v-model:show="showFeedback" position="bottom" round style="height: 50%">
      <div class="popup-content">
        <div class="popup-header">
          <span>意見反饋</span>
          <van-icon name="cross" @click="showFeedback = false" />
        </div>
        <van-form @submit="submitFeedback">
          <van-cell-group inset>
            <van-field
              v-model="feedbackText"
              type="textarea"
              rows="5"
              placeholder="請輸入您的意見或建議..."
              show-word-limit
              maxlength="500"
            />
          </van-cell-group>
          <div style="padding: 16px;">
            <van-button type="primary" block round native-type="submit">提交反饋</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { showToast, showConfirmDialog } from 'vant'

const currentUser = ref({
  id: 'M-2024-0158',
  name: '陳大明',
  level: 'committee',
  phone: '0912-345-678',
  email: 'daming.chen@email.com',
  company: '大明科技股份有限公司',
  title: '總經理',
  address: '台北市中正區忠孝東路100號',
  avatar: 'https://ui-avatars.com/api/?name=陳大明&background=1a365d&color=fff&size=128'
})

const levelInfo = computed(() => {
  const levels = {
    committee: { name: '未來街坊圈圈委', icon: '⭐⭐⭐' },
    citizen: { name: '未來街坊圈圈民', icon: '⭐⭐' },
    friend: { name: '未來街坊圈圈友', icon: '⭐' }
  }
  return levels[currentUser.value.level]
})

const maskedPhone = computed(() => {
  const phone = currentUser.value.phone
  return phone.replace(/(\d{4})-(\d{3})-(\d{3})/, '$1-***-$3')
})

const maskedEmail = computed(() => {
  const email = currentUser.value.email
  const [name, domain] = email.split('@')
  return `${name.slice(0, 2)}***@${domain}`
})

const notifications = ref({
  events: true,
  payment: true,
  system: true
})

const showEditProfile = ref(false)
const showChangePassword = ref(false)
const showFeedback = ref(false)

const editForm = ref({
  name: currentUser.value.name,
  phone: currentUser.value.phone,
  email: currentUser.value.email,
  company: currentUser.value.company,
  title: currentUser.value.title,
  address: currentUser.value.address
})

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

const feedbackText = ref('')

const saveProfile = () => {
  currentUser.value = { ...currentUser.value, ...editForm.value }
  showToast({ type: 'success', message: '儲存成功' })
  showEditProfile.value = false
}

const changePassword = () => {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    showToast({ type: 'fail', message: '兩次密碼不一致' })
    return
  }
  showToast({ type: 'success', message: '密碼修改成功' })
  showChangePassword.value = false
  passwordForm.value = { current: '', new: '', confirm: '' }
}

const contactService = () => {
  showToast({ message: '客服電話：02-1234-5678' })
}

const submitFeedback = () => {
  showToast({ type: 'success', message: '感謝您的反饋！' })
  showFeedback.value = false
  feedbackText.value = ''
}

const logout = async () => {
  try {
    await showConfirmDialog({
      title: '確認登出',
      message: '確定要登出帳號嗎？'
    })
    showToast({ message: '已登出' })
  } catch {
    // 用戶取消
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 90px;
}

.user-card {
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
  padding: 24px 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.user-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 3px solid rgba(255,255,255,0.3);
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.level-badge {
  display: inline-block;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 20px;
  margin-top: 6px;
}

.level-badge.committee {
  background: rgba(214, 158, 46, 0.3);
  color: #fbd38d;
}

.level-badge.citizen {
  background: rgba(49, 130, 206, 0.3);
  color: #90cdf4;
}

.level-badge.friend {
  background: rgba(113, 128, 150, 0.3);
  color: #e2e8f0;
}

.logout-section {
  padding: 24px 16px 16px;
}

.version-info {
  text-align: center;
  font-size: 12px;
  color: #a0aec0;
  padding-bottom: 16px;
}

.popup-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #f0f0f0;
}

.popup-header .van-icon {
  font-size: 20px;
  color: #999;
}
</style>
