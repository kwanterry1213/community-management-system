<template>
  <div class="login-page">
    <div class="login-bg"></div>
    <div class="login-content">
      <!-- Logo 區 -->
      <div class="logo-section">
        <div class="logo-icon">
          <img src="/images/login-logo.png" alt="Logo" class="logo-image" />
        </div>
        <h1 class="app-title">未來街坊圈</h1>
        <p class="app-subtitle">商務社團管理系統</p>
      </div>

      <!-- 主表單卡片 -->
      <div class="form-card">
        <!-- 登入 / 註冊 -->
        <template v-if="currentView === 'auth'">
          <van-tabs v-model:active="activeTab" animated>
            <van-tab title="登入">
              <van-form @submit="handleLogin" class="form-body">
                <van-cell-group inset>
                  <van-field
                    v-model="loginForm.identifier"
                    label="帳號"
                    placeholder="電子郵件 / 手機號碼 / 用戶名"
                    left-icon="manager-o"
                    :rules="[{ required: true, message: '請輸入帳號' }]"
                  />
                  <van-field
                    v-model="loginForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    label="密碼"
                    placeholder="請輸入密碼"
                    left-icon="lock"
                    :right-icon="showPassword ? 'eye-o' : 'closed-eye'"
                    @click-right-icon="showPassword = !showPassword"
                    :rules="[{ required: true, message: '請輸入密碼' }]"
                  />
                </van-cell-group>
                <div class="forgot-link">
                  <span @click="currentView = 'forgot'">忘記密碼？</span>
                </div>
                <div class="form-actions">
                  <van-button
                    type="primary"
                    block
                    round
                    size="large"
                    native-type="submit"
                    :loading="authStore.loading"
                    loading-text="登入中..."
                  >
                    登入
                  </van-button>
                </div>
              </van-form>
            </van-tab>

            <van-tab title="註冊">
              <van-form @submit="handleRegister" class="form-body">
                <van-cell-group inset>
                  <van-field
                    v-model="registerForm.username"
                    label="姓名"
                    placeholder="請輸入姓名"
                    left-icon="friends-o"
                    :rules="[{ required: true, message: '請輸入姓名' }]"
                  />
                  <van-field
                    v-model="registerForm.email"
                    label="信箱"
                    placeholder="請輸入電子郵件"
                    left-icon="envelop-o"
                    :rules="[{ required: true, message: '請輸入信箱' }, { pattern: /.+@.+\..+/, message: '請輸入有效的信箱格式' }]"
                  />
                  <van-field
                    v-model="registerForm.phone_number"
                    label="電話"
                    placeholder="選填"
                    left-icon="phone-o"
                  />
                  <van-field
                    v-model="registerForm.password"
                    :type="showRegPassword ? 'text' : 'password'"
                    label="密碼"
                    placeholder="請設定密碼（至少6位）"
                    left-icon="lock"
                    :right-icon="showRegPassword ? 'eye-o' : 'closed-eye'"
                    @click-right-icon="showRegPassword = !showRegPassword"
                    :rules="[{ required: true, message: '請設定密碼' }, { validator: v => v.length >= 6, message: '密碼至少6個字元' }]"
                  />
                </van-cell-group>
                <div class="form-actions">
                  <van-button
                    type="primary"
                    block
                    round
                    size="large"
                    native-type="submit"
                    :loading="authStore.loading"
                    loading-text="註冊中..."
                  >
                    註冊
                  </van-button>
                </div>
              </van-form>
            </van-tab>
          </van-tabs>
        </template>

        <!-- 忘記密碼 - 步驟一：輸入 email -->
        <template v-if="currentView === 'forgot'">
          <div class="view-header">
            <van-icon name="arrow-left" class="back-icon" @click="currentView = 'auth'" />
            <span class="view-title">忘記密碼</span>
          </div>
          <van-form @submit="handleForgotPassword" class="form-body">
            <div class="view-desc">請輸入您註冊時使用的電子郵件，我們將發送密碼重置連結。</div>
            <van-cell-group inset>
              <van-field
                v-model="forgotEmail"
                label="信箱"
                placeholder="請輸入電子郵件"
                left-icon="envelop-o"
                :rules="[{ required: true, message: '請輸入信箱' }, { pattern: /.+@.+\..+/, message: '請輸入有效的信箱格式' }]"
              />
            </van-cell-group>
            <div class="form-actions">
              <van-button
                type="primary"
                block
                round
                size="large"
                native-type="submit"
                :loading="forgotLoading"
                loading-text="發送中..."
              >
                發送重置連結
              </van-button>
              <van-button
                plain
                block
                round
                size="large"
                @click="currentView = 'auth'"
                style="margin-top: 10px;"
              >
                返回登入
              </van-button>
            </div>
          </van-form>
        </template>

        <!-- 忘記密碼 - 步驟二：輸入新密碼 -->
        <template v-if="currentView === 'reset'">
          <div class="view-header">
            <van-icon name="arrow-left" class="back-icon" @click="currentView = 'forgot'" />
            <span class="view-title">重設密碼</span>
          </div>
          <van-form @submit="handleResetPassword" class="form-body">
            <div class="view-desc">
              <van-icon name="passed" color="#67c23a" /> 驗證碼已發送至 <strong>{{ forgotEmail }}</strong>
            </div>
            <van-cell-group inset>
              <van-field
                v-model="resetForm.token"
                label="驗證碼"
                placeholder="請輸入重置驗證碼"
                left-icon="shield-o"
                :rules="[{ required: true, message: '請輸入驗證碼' }]"
              />
              <van-field
                v-model="resetForm.newPassword"
                :type="showResetPassword ? 'text' : 'password'"
                label="新密碼"
                placeholder="請輸入新密碼（至少6位）"
                left-icon="lock"
                :right-icon="showResetPassword ? 'eye-o' : 'closed-eye'"
                @click-right-icon="showResetPassword = !showResetPassword"
                :rules="[{ required: true, message: '請輸入新密碼' }, { validator: v => v.length >= 6, message: '密碼至少6個字元' }]"
              />
              <van-field
                v-model="resetForm.confirmPassword"
                :type="showResetPassword ? 'text' : 'password'"
                label="確認密碼"
                placeholder="請再次輸入新密碼"
                left-icon="lock"
                :rules="[{ required: true, message: '請確認密碼' }, { validator: v => v === resetForm.newPassword, message: '兩次密碼不一致' }]"
              />
            </van-cell-group>
            <div class="form-actions">
              <van-button
                type="primary"
                block
                round
                size="large"
                native-type="submit"
                :loading="resetLoading"
                loading-text="重設中..."
              >
                重設密碼
              </van-button>
            </div>
          </van-form>
        </template>

        <!-- 重設成功 -->
        <template v-if="currentView === 'success'">
          <div class="success-view">
            <van-icon name="checked" size="64" color="#67c23a" />
            <h3>密碼重設成功</h3>
            <p>請使用新密碼登入您的帳號。</p>
            <van-button type="primary" block round size="large" @click="backToLogin">
              返回登入
            </van-button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref(0)
const currentView = ref('auth')
const showPassword = ref(false)
const showRegPassword = ref(false)
const showResetPassword = ref(false)

const loginForm = ref({ identifier: '', password: '' })
const registerForm = ref({ username: '', email: '', phone_number: '', password: '' })

const forgotEmail = ref('')
const forgotLoading = ref(false)

const resetForm = reactive({ token: '', newPassword: '', confirmPassword: '' })
const resetLoading = ref(false)

const handleLogin = async () => {
  const result = await authStore.login(loginForm.value.identifier, loginForm.value.password)
  if (result.success) {
    showToast({ type: 'success', message: '登入成功' })
    router.replace('/m/home')
  } else {
    showToast({ type: 'fail', message: result.message })
  }
}

const handleRegister = async () => {
  const result = await authStore.register(registerForm.value)
  if (result.success) {
    showToast({ type: 'success', message: '註冊成功' })
    router.replace('/m/home')
  } else {
    showToast({ type: 'fail', message: result.message })
  }
}

const handleForgotPassword = async () => {
  forgotLoading.value = true
  try {
    const res = await authApi.forgotPassword(forgotEmail.value)
    if (res.reset_token) {
      resetForm.token = res.reset_token
    }
    showToast({ type: 'success', message: '驗證碼已發送' })
    currentView.value = 'reset'
  } catch (err) {
    const msg = err.response?.data?.detail || '發送失敗，請稍後重試'
    showToast({ type: 'fail', message: msg })
  } finally {
    forgotLoading.value = false
  }
}

const handleResetPassword = async () => {
  if (resetForm.newPassword !== resetForm.confirmPassword) {
    showToast({ type: 'fail', message: '兩次密碼不一致' })
    return
  }
  resetLoading.value = true
  try {
    await authApi.resetPassword(resetForm.token, resetForm.newPassword)
    currentView.value = 'success'
  } catch (err) {
    const msg = err.response?.data?.detail || '重設失敗，請稍後重試'
    showToast({ type: 'fail', message: msg })
  } finally {
    resetLoading.value = false
  }
}

const backToLogin = () => {
  currentView.value = 'auth'
  forgotEmail.value = ''
  resetForm.token = ''
  resetForm.newPassword = ''
  resetForm.confirmPassword = ''
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 50%, #1a365d 100%);
}

.login-bg {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(49, 130, 206, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(214, 158, 46, 0.2) 0%, transparent 50%);
}

.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px 40px;
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 188px;
  height: 188px;
  border-radius: 50%;
  overflow: hidden;
  background: #1a365d;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 20px;
  filter: brightness(0) invert(1);
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 6px;
  letter-spacing: 3px;
}

.app-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.form-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.form-body {
  padding: 8px 0 16px;
}

.form-actions {
  padding: 20px 16px 8px;
}

.forgot-link {
  text-align: right;
  padding: 8px 24px 0;
}
.forgot-link span {
  font-size: 13px;
  color: #3182ce;
  cursor: pointer;
}
.forgot-link span:active {
  opacity: 0.7;
}

/* 忘記密碼 / 重設密碼 view */
.view-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px 8px;
}
.back-icon {
  font-size: 20px;
  color: #666;
  cursor: pointer;
}
.view-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}
.view-desc {
  padding: 8px 24px 12px;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

/* 成功頁 */
.success-view {
  text-align: center;
  padding: 40px 24px;
}
.success-view h3 {
  margin: 16px 0 8px;
  font-size: 20px;
  color: #333;
}
.success-view p {
  color: #666;
  font-size: 14px;
  margin-bottom: 24px;
}
</style>
