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

      <!-- 登入/註冊表單 -->
      <div class="form-card">
        <van-tabs v-model:active="activeTab" animated>
          <van-tab title="登入">
            <van-form @submit="handleLogin" class="form-body">
              <van-cell-group inset>
                <van-field
                  v-model="loginForm.identifier"
                  label="帳號"
                  placeholder="電子郵件或手機號碼"
                  :rules="[{ required: true, message: '請輸入帳號' }]"
                />
                <van-field
                  v-model="loginForm.password"
                  type="password"
                  label="密碼"
                  placeholder="請輸入密碼"
                  :rules="[{ required: true, message: '請輸入密碼' }]"
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
                  :rules="[{ required: true, message: '請輸入姓名' }]"
                />
                <van-field
                  v-model="registerForm.email"
                  label="信箱"
                  placeholder="請輸入電子郵件"
                  :rules="[{ required: true, message: '請輸入信箱' }]"
                />
                <van-field
                  v-model="registerForm.phone_number"
                  label="電話"
                  placeholder="選填"
                />
                <van-field
                  v-model="registerForm.password"
                  type="password"
                  label="密碼"
                  placeholder="請設定密碼"
                  :rules="[{ required: true, message: '請設定密碼' }]"
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const activeTab = ref(0)

const loginForm = ref({ identifier: '', password: '' })
const registerForm = ref({ username: '', email: '', phone_number: '', password: '' })

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
</style>
