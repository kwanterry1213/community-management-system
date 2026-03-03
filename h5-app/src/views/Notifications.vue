<template>
  <div>
    <van-nav-bar
      title="Notifications"
      left-text="Back"
      left-arrow
      @click-left="onClickLeft"
    />
    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="No more notifications"
      @load="onLoad"
    >
      <van-cell v-for="item in list" :key="item.id" :title="item.title" :label="item.body" />
    </van-list>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const list = ref([]);
const loading = ref(false);
const finished = ref(false);

const onClickLeft = () => router.back();

const onLoad = () => {
  // Simulate fetching data
  setTimeout(() => {
    for (let i = 0; i < 10; i++) {
      const newItem = {
        id: list.value.length + 1,
        title: `Notification ${list.value.length + 1}`,
        body: 'This is a notification message.',
      };
      list.value.push(newItem);
    }

    loading.value = false;

    if (list.value.length >= 20) {
      finished.value = true;
    }
  }, 1000);
};
</script>
