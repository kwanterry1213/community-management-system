<template>
  <div class="page event-edit-page">
    <van-nav-bar
      :title="isEdit ? '編輯活動' : '建立活動'"
      left-arrow
      @click-left="router.back()"
    />

    <div class="form-content">
      <van-cell-group inset>
        <!-- 基本資訊 -->
        <div class="upload-section">
           <van-uploader v-model="fileList" :max-count="1" :after-read="afterRead" upload-text="上傳封面" />
        </div>

        <van-field
          v-model="form.title"
          label="活動名稱"
          placeholder="請輸入活動名稱"
          required
        />
        
        <van-field
          v-model="form.description"
          label="活動說明"
          type="textarea"
          placeholder="請輸入詳細說明"
          rows="3"
          autosize
        />

        <van-field
          v-model="form.location"
          label="地點"
          placeholder="例如：社區活動中心"
          left-icon="location-o"
        />

        <!-- 費用與名額 -->
        <van-field
          v-model.number="form.price"
          label="費用"
          type="number"
          placeholder="0 為免費"
          left-icon="gold-coin-o"
        />

        <van-field
          v-model.number="form.capacity"
          label="名額限制"
          type="digit"
          placeholder="留空表示不限"
          left-icon="friends-o"
        />

        <div class="field-help">若不限名額請留空或填 0</div>

        <!-- Early Bird -->
        <div class="section-divider">早鳥優惠 (選填)</div>
        
          <van-field
            v-model.number="form.early_bird_price"
            label="早鳥價"
            type="number"
            placeholder="請輸入早鳥優惠價"
            left-icon="discount"
          />
          <van-field
            v-model="form.eb_date_str"
            label="截止日期"
            placeholder="格式：20260205"
            left-icon="clock-o"
            @update:model-value="(val) => handleDateInput(val, 'eb')"
            @click-right-icon="showEbCalendar = true"
            right-icon="arrow-down"
          />
          <van-field
            v-model="form.eb_time"
            label="截止時間"
            type="time"
            left-icon="clock-o"
            @click="showEbTime = true"
          />

        <!-- Smart Date Inputs -->
        <van-field
          v-model="form.start_date_str"
          label="開始日期"
          placeholder="格式：20260205"
          left-icon="calendar-o"
          @update:model-value="(val) => handleDateInput(val, 'start')"
          @click-right-icon="showStartCalendar = true"
          right-icon="arrow-down"
        />
        <van-field
          v-model="form.start_time"
          label="開始時間"
          type="time"
          left-icon="clock-o"
          @click="showStartTime = true"
        />

        <van-field
          v-model="form.end_date_str"
          label="結束日期"
          placeholder="格式：20260205"
          left-icon="calendar-o"
          @update:model-value="(val) => handleDateInput(val, 'end')"
          @click-right-icon="showEndCalendar = true"
          right-icon="arrow-down"
        />
        <van-field
          v-model="form.end_time"
          label="結束時間"
          type="time"
          left-icon="clock-o"
          @click="showEndTime = true"
        />

        <!-- 設定 -->
        <van-cell center title="公開活動">
          <template #right-icon>
            <van-switch v-model="form.is_public" />
          </template>
        </van-cell>
      </van-cell-group>

      <div class="action-buttons">
        <van-button block type="primary" @click="onSubmit" :loading="submitting">
          {{ isEdit ? '儲存變更' : '建立活動' }}
        </van-button>
        <van-button v-if="isEdit" block type="danger" plain class="mt-2" @click="onDelete">
          刪除活動
        </van-button>
      </div>
    </div>

    <!-- Calendar Popups -->
    <van-calendar v-model:show="showStartCalendar" @confirm="onConfirmStartDate" />
    <van-calendar v-model:show="showEndCalendar" @confirm="onConfirmEndDate" />
    <van-calendar v-model:show="showEbCalendar" @confirm="onConfirmEbDate" />
    
    <!-- Time Pickers -->
    <van-popup v-model:show="showStartTime" position="bottom">
      <van-time-picker
        v-model="form.start_time_picker"
        title="選擇開始時間"
        @confirm="(val) => { form.start_time = val.selectedValues.join(':'); showStartTime = false }"
        @cancel="showStartTime = false"
      />
    </van-popup>
    <van-popup v-model:show="showEndTime" position="bottom">
      <van-time-picker
        v-model="form.end_time_picker"
        title="選擇結束時間"
        @confirm="(val) => { form.end_time = val.selectedValues.join(':'); showEndTime = false }"
        @cancel="showEndTime = false"
      />
    </van-popup>
    <van-popup v-model:show="showEbTime" position="bottom">
      <van-time-picker
        v-model="form.eb_time_picker"
        title="選擇截止時間"
        @confirm="(val) => { form.eb_time = val.selectedValues.join(':'); showEbTime = false }"
        @cancel="showEbTime = false"
      />
    </van-popup>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { eventApi, commonApi } from '@/services/api'
import { showToast, showLoadingToast, showSuccessToast, showFailToast, showDialog } from 'vant'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => !!route.params.id)
const submitting = ref(false)

const showStartCalendar = ref(false)
const showEndCalendar = ref(false)
const showEbCalendar = ref(false)
const showStartTime = ref(false)
const showEndTime = ref(false)
const showEbTime = ref(false)

const fileList = ref([])

const form = ref({
  title: '',
  description: '',
  location: '',
  price: 0,
  capacity: null,
  is_public: true,
  image_url: '',
  early_bird_price: null,
  start_date_str: '',
  start_time: '12:00',
  start_time_picker: ['12', '00'],
  end_date_str: '',
  end_time: '14:00',
  end_time_picker: ['14', '00'],
  eb_date_str: '',
  eb_time: '23:59',
  eb_time_picker: ['23', '59']
})

const afterRead = async (file) => {
  file.status = 'uploading'
  file.message = '上傳中...'
  try {
    const res = await commonApi.upload(file.file)
    form.value.image_url = res.url
    file.status = 'done'
    file.message = '上傳成功'
  } catch (err) {
    file.status = 'failed'
    file.message = '上傳失敗'
    const errorMsg = err.response?.data?.detail || err.message || '未知錯誤'
    showDialog({ title: '上傳失敗', message: '錯誤詳情: ' + errorMsg })
  }
}

// Smart Date Input Logic
const handleDateInput = (val, field) => {
  // Remove non-digits
  const digits = val.replace(/\D/g, '')
  
  // Auto-format YYYYMMDD -> YYYY-MM-DD
  if (digits.length >= 8) {
    const yyyy = digits.slice(0, 4)
    const mm = digits.slice(4, 6)
    const dd = digits.slice(6, 8)
    // Only update if looks valid
    if (parseInt(mm) <= 12 && parseInt(dd) <= 31) {
      if (field === 'start') form.value.start_date_str = `${yyyy}-${mm}-${dd}`
      if (field === 'end') form.value.end_date_str = `${yyyy}-${mm}-${dd}`
      if (field === 'eb') form.value.eb_date_str = `${yyyy}-${mm}-${dd}`
    }
  }
}

const onConfirmStartDate = (date) => {
  form.value.start_date_str = formatDate(date)
  showStartCalendar.value = false
}

const onConfirmEndDate = (date) => {
  form.value.end_date_str = formatDate(date)
  showEndCalendar.value = false
}

const onConfirmEbDate = (date) => {
  form.value.eb_date_str = formatDate(date)
  showEbCalendar.value = false
}

const formatDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const combineDateTime = (dateStr, timeStr) => {
  if (!dateStr) return null
  return `${dateStr}T${timeStr}:00`
}

const onSubmit = async () => {
  if (!form.value.title || !form.value.start_date_str) {
    showToast('請填寫完整資訊')
    return
  }

  submitting.value = true
  const toast = showLoadingToast({
    message: '儲存中...',
    forbidClick: true,
    duration: 0
  })

  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      location: form.value.location,
      price: Number(form.value.price) || 0,
      capacity: form.value.capacity ? Number(form.value.capacity) : null,
      is_public: form.value.is_public,
      image_url: form.value.image_url,
      start_at: combineDateTime(form.value.start_date_str, form.value.start_time),
      end_at: combineDateTime(form.value.end_date_str, form.value.end_time),
      early_bird_price: form.value.early_bird_price ? Number(form.value.early_bird_price) : null,
      early_bird_deadline: combineDateTime(form.value.eb_date_str, form.value.eb_time),
      community_id: 1 // Default community for now
    }

    if (isEdit.value) {
      await eventApi.update(route.params.id, payload)
      toast.close()
      showSuccessToast('更新成功')
    } else {
      await eventApi.create(payload, 1) // Assume createdBy=1 (System Admin) for now, or check authStore
      toast.close()
      showSuccessToast('建立成功')
    }
    
    // Wait for toast
    setTimeout(() => {
        router.back()
    }, 1500)
    
  } catch (err) {
    toast.close()
    showFailToast('儲存失敗: ' + (err.response?.data?.detail || err.message))
  } finally {
    submitting.value = false
  }
}

const onDelete = () => {
  showDialog({
    title: '刪除活動',
    message: '確定要刪除此活動嗎？無法復原。',
    showCancelButton: true
  }).then(async () => {
    try {
      await eventApi.delete(route.params.id)
      showToast('已刪除')
      router.back()
    } catch (err) {
      showToast('刪除失敗')
    }
  })
}

const fetchEvent = async (id) => {
  try {
    const data = await eventApi.get(id)
    // Populate form
    form.value.title = data.title
    form.value.description = data.description
    form.value.location = data.location
    form.value.price = data.price
    form.value.capacity = data.capacity
    form.value.is_public = data.is_public
    form.value.early_bird_price = data.early_bird_price
    form.value.image_url = data.image_url

    if (data.image_url) {
        fileList.value = [{ url: data.image_url, isImage: true }]
    }

    // Parse Dates
    if (data.start_at) {
        const d = new Date(data.start_at)
        form.value.start_date_str = formatDate(d)
        form.value.start_time = formatTime(d)
        form.value.start_time_picker = form.value.start_time.split(':')
    }
    if (data.end_at) {
        const d = new Date(data.end_at)
        form.value.end_date_str = formatDate(d)
        form.value.end_time = formatTime(d)
        form.value.end_time_picker = form.value.end_time.split(':')
    }
    if (data.early_bird_deadline) {
        const d = new Date(data.early_bird_deadline)
        form.value.eb_date_str = formatDate(d)
        form.value.eb_time = formatTime(d)
        form.value.eb_time_picker = form.value.eb_time.split(':')
    }
  } catch (err) {
    showToast('載入活動失敗')
    router.back()
  }
}

const formatTime = (date) => {
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(async () => {
  // Set default dates to today/tomorrow if creating
  if (!isEdit.value) {
    const today = new Date()
    form.value.start_date_str = formatDate(today)
    form.value.end_date_str = formatDate(today)
  } else {
    await fetchEvent(route.params.id)
  }
})
</script>

<style scoped>
.event-edit-page {
  background: #f5f7fa;
  min-height: 100vh;
}
.form-content {
  padding: 16px 0;
}
.upload-section {
  display: flex;
  justify-content: center;
  padding: 16px;
  background: white;
  margin: 0 16px 16px;
  border-radius: 12px;
}
.section-divider {
  font-size: 14px;
  color: #969799;
  padding: 16px 16px 8px;
  background-color: #fff;
}
.action-buttons {
  padding: 24px 16px;
}
.mt-2 {
  margin-top: 12px;
}
.field-help {
  font-size: 12px;
  color: #999;
  padding: 4px 16px 12px;
}
</style>
