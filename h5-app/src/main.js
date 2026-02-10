import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Vant 基礎樣式
import 'vant/lib/index.css'

// 全域樣式
import './styles/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
