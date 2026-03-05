<template>
  <div class="member-layout">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
    
    <!-- 浮動搜索按鈕 -->
    <div
      v-if="!isSearchPage"
      class="fab-search"
      @click="$router.push('/m/search')"
    >
      <van-icon name="search" size="22" />
    </div>

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
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeTab = ref(route.path)
const isSearchPage = computed(() => route.path.includes('/search'))

watch(() => route.path, (path) => {
  activeTab.value = path
})
</script>

<style scoped>
.member-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.fab-search {
  position: fixed;
  right: 20px;
  bottom: 80px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa 0%, #667eea 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(25, 137, 250, 0.4);
  z-index: 100;
  cursor: pointer;
  transition: transform 0.2s;
}

.fab-search:active {
  transform: scale(0.9);
}
</style>
