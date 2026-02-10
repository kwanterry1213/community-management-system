<template>
  <div class="admin-layout">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
    
    <!-- 管理後台底部導航 -->
    <van-tabbar v-model="activeTab" route>
      <van-tabbar-item to="/admin" icon="home-o">首頁</van-tabbar-item>
      <van-tabbar-item to="/admin/members" icon="friends-o">會員</van-tabbar-item>
      <van-tabbar-item to="/admin/payments" icon="card">繳費</van-tabbar-item>
      <van-tabbar-item to="/admin/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeTab = ref(route.path)

watch(() => route.path, (path) => {
  activeTab.value = path
})
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: var(--color-gray-100);
}
</style>
