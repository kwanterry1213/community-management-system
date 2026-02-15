<template>
  <div class="scanner-page">
    <van-nav-bar title="掃碼簽到" left-text="返回" left-arrow @click-left="onClickLeft" />
    
    <div class="scanner-container">
      <div id="reader" width="100%"></div>
      <div class="scan-overlay" v-if="scanning">
        <div class="scan-area"></div>
        <div class="scan-text">請將會員 QR Code 置於框內</div>
      </div>
    </div>

    <div class="control-panel">
      <div class="event-selector" @click="showEventPicker = true">
        <span class="label">當前活動：</span>
        <span class="value">{{ selectedEvent?.title || '請選擇活動' }}</span>
        <van-icon name="arrow-down" />
      </div>

      <div class="scan-result" v-if="lastResult">
        <van-icon :name="resultIcon" :color="resultColor" size="40" />
        <div class="result-text">{{ lastResult.message }}</div>
        <div class="result-time">{{ lastResult.time }}</div>
      </div>
      
       <div class="manual-input">
        <van-field v-model="manualInput" placeholder="手動輸入會員編號" center clearable>
            <template #button>
                <van-button size="small" type="primary" @click="handleManualCheckIn" :disabled="!manualInput">簽到</van-button>
            </template>
        </van-field>
      </div>
    </div>

    <van-popup v-model:show="showEventPicker" position="bottom">
      <van-picker
        :columns="eventColumns"
        @confirm="onEventConfirm"
        @cancel="showEventPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import { Html5Qrcode } from 'html5-qrcode'
import { eventApi } from '@/services/api' // We'll need to add checkin api to services
import api from '@/services/api' // Direct axios access for new endpoint if not yet in service

const router = useRouter()
const scanning = ref(true)
const showEventPicker = ref(false)
const events = ref([])
const selectedEvent = ref(null)
const lastResult = ref(null)
const manualInput = ref('')
let html5QrCode = null

const eventColumns = computed(() => events.value.map(e => ({ text: e.title, value: e.id })))

const resultIcon = computed(() => {
  if (!lastResult.value) return ''
  if (lastResult.value.status === 'checked_in') return 'checked'
  if (lastResult.value.status === 'already_checked_in') return 'info'
  return 'clear'
})

const resultColor = computed(() => {
    if (!lastResult.value) return ''
    if (lastResult.value.status === 'checked_in') return '#07c160'
    if (lastResult.value.status === 'already_checked_in') return '#1989fa'
    return '#ee0a24'
})


const onClickLeft = () => router.back()

const fetchEvents = async () => {
    try {
        const res = await eventApi.list()
        events.value = res || []
        if (events.value.length > 0) {
            selectedEvent.value = events.value[0]
        }
    } catch (error) {
        showToast('無法獲取活動列表')
    }
}

const onEventConfirm = ({ selectedOptions }) => {
    selectedEvent.value = events.value.find(e => e.id === selectedOptions[0].value)
    showEventPicker.value = false
}

const handleCheckIn = async (membershipNo) => {
    if (!selectedEvent.value) {
        showToast('請先選擇活動')
        return
    }
    
    // Simple debounce/duplicate check mechanism could be added here
    
    try {
        // Call backend API
        const res = await api.post('/events/checkin', {
            event_id: selectedEvent.value.id,
            membership_no: membershipNo
        })
        
        lastResult.value = {
            status: res.status || 'checked_in',
            message: res.message,
            time: new Date().toLocaleTimeString()
        }
        
        // Play success sound (optional)
        // const audio = new Audio('/success.mp3'); audio.play();

    } catch (error) {
        console.error(error)
        const msg = error.response?.data?.detail || '簽到失敗'
        lastResult.value = {
            status: 'error',
            message: msg,
            time: new Date().toLocaleTimeString()
        }
    }
}

const handleManualCheckIn = () => {
    if(!manualInput.value) return
    handleCheckIn(manualInput.value)
    manualInput.value = ''
}


const onScanSuccess = (decodedText, decodedResult) => {
    // Prevent rapid multiple scans of the same code logic can be added
    console.log(`Code matched = ${decodedText}`, decodedResult)
    
    // Assuming QR code contains just the membership number or json?
    // Let's assume it's just the membership number for now as per MemberHome.vue (it displays membership_no)
    // If QR contains "NO. 12345", strict parsing might be needed. 
    // Based on MemberHome.vue: <div class="qr-id">{{ authStore.membership?.membership_no || '' }}</div>
    // It seems to be just the number string.
    
    handleCheckIn(decodedText)
    
    // Pause scanning for a moment?
    // html5QrCode.pause();
    // setTimeout(() => html5QrCode.resume(), 2000);
}

const onScanFailure = (error) => {
    // console.warn(`Code scan error = ${error}`)
}

onMounted(async () => {
    await fetchEvents()
    
    html5QrCode = new Html5Qrcode("reader")
    const config = { fps: 10, qrbox: { width: 250, height: 250 } }
    
    // Prefer back camera
    html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess, onScanFailure)
    .catch(err => {
        console.error("Error starting scanner", err)
        showToast('無法啟動相機，請確保已授權')
        scanning.value = false
    })
})

onBeforeUnmount(() => {
    if (html5QrCode) {
        html5QrCode.stop().then((ignore) => {
            // QR Code scanning is stopped.
        }).catch((err) => {
            // Stop failed.
        })
    }
})
</script>

<style scoped>
.scanner-page {
  min-height: 100vh;
  background: #000;
  display: flex;
  flex-direction: column;
}

.scanner-container {
  flex: 1;
  position: relative;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

#reader {
  width: 100%;
}

.scan-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.scan-area {
  width: 250px;
  height: 250px;
  border: 2px solid #07c160;
  border-radius: 12px;
  box-shadow: 0 0 0 4000px rgba(0,0,0,0.5); /* Dim surrounding */
}

.scan-text {
  margin-top: 20px;
  color: white;
  font-size: 14px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.control-panel {
  background: white;
  padding: 20px;
  border-radius: 20px 20px 0 0;
  min-height: 250px;
}

.event-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f7f8fa;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.event-selector .value {
  font-weight: 600;
  color: #1a202c;
  flex: 1;
  text-align: right;
  margin-right: 8px;
}

.scan-result {
  text-align: center;
  padding: 20px;
  background: #f0fdf4;
  border-radius: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

.result-text {
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
  color: #1a202c;
}

.result-time {
  font-size: 12px;
  color: #718096;
  margin-top: 4px;
}

.manual-input {
    margin-top: 10px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
