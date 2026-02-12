<template>
  <div class="page profile-page">
    <div class="profile-header">
      <img src="https://ui-avatars.com/api/?name=Admin&background=1a365d&color=fff&size=80" class="profile-avatar" />
      <div class="profile-info">
        <div class="profile-name">管理員</div>
        <div class="profile-role">系統管理員</div>
      </div>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="帳號設定" icon="setting-o" is-link />
        <van-cell title="消息通知" icon="bell" is-link>
          <template #value><van-badge :content="3" /></template>
        </van-cell>
        <van-cell title="數據報表" icon="chart-trending-o" is-link />
      </van-cell-group>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="系統設定" icon="apps-o" is-link />
        <van-cell title="幫助中心" icon="question-o" is-link />
        <van-cell title="關於我們" icon="info-o" is-link />
      </van-cell-group>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell 
          title="返回會員端" 
          icon="arrow-left" 
          is-link 
          @click="$router.push('/m/home')"
        >
          <template #label>
            <span style="color: #3182ce;">退出管理後台</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="退出登入" icon="revoke" is-link @click="logout" />
      </van-cell-group>
    </div>

    <div class="version-info">版本 1.0.0</div>
  </div>
</template>

<script setup>
import { showConfirmDialog, showToast } from 'vant'

const logout = () => {
  showConfirmDialog({ title: '確認退出？', message: '退出後需要重新登入' })
    .then(() => showToast('已退出登入'))
    .catch(() => {})
}
</script>

<style scoped>
.profile-page { padding: 0; background: var(--color-gray-100); }

.profile-header {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  padding: 32px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.profile-avatar { width: 64px; height: 64px; border-radius: 50%; border: 3px solid rgba(255,255,255,0.3); }
.profile-info { color: white; }
.profile-name { font-size: 18px; font-weight: 600; }
.profile-role { font-size: 13px; opacity: 0.8; }

.menu-section { margin-top: 12px; }
.version-info { text-align: center; padding: 20px; font-size: 12px; color: var(--color-gray-400); }
</style>
