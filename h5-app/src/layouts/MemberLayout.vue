<template>
  <div class="member-layout">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
    
    <!-- 會員端底部導航 -->
    <van-tabbar v-model="activeTab" route>
      <van-tabbar-item to="/m/home" icon="wap-home-o">首頁</van-tabbar-item>
      <van-tabbar-item to="/m/events" icon="calendar-o">活動</van-tabbar-item>
      <van-tabbar-item to="/m/membership" icon="idcard">會籍</van-tabbar-item>
      <van-tabbar-item to="/m/profile" icon="user-o">我的</van-tabbar-item>
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
.member-layout {
  min-height: 100vh;
  background: #f5f7fa;
}
</style>
