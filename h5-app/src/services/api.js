import axios from 'axios'

// 建立 axios 實例
const api = axios.create({
    baseURL: '/api',
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
})

// 請求攔截器 - 自動附加 token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// 回應攔截器 - 處理錯誤
api.interceptors.response.use(
    (response) => response.data,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            window.location.hash = '#/login'
        }
        return Promise.reject(error)
    }
)

// --- Auth API ---
export const authApi = {
    login(identifier, password) {
        return api.post('/auth/login', { identifier, password })
    },
    register(data) {
        return api.post('/auth/register', data)
    },
}

// --- User API ---
export const userApi = {
    getProfile(userId) {
        return api.get(`/users/${userId}`)
    },
    updateProfile(userId, data) {
        return api.patch(`/users/${userId}`, data)
    },
    listUsers() {
        return api.get('/users')
    },
}

// --- Membership API ---
export const membershipApi = {
    list(params = {}) {
        return api.get('/memberships', { params })
    },
    create(data) {
        return api.post('/memberships', data)
    },
    update(id, data) {
        return api.patch(`/memberships/${id}`, data)
    },
}

// --- Event API ---
export const eventApi = {
    list(params = {}) {
        return api.get('/events', { params })
    },
    get(eventId) {
        return api.get(`/events/${eventId}`)
    },
    create(data, createdBy) {
        return api.post(`/events?created_by=${createdBy}`, data)
    },
    register(eventId, userId) {
        return api.post(`/events/${eventId}/register`, { event_id: eventId, user_id: userId })
    },
    update(id, data) {
        return api.put(`/events/${id}`, data)
    },
    delete(id) {
        return api.delete(`/events/${id}`)
    },
}

// --- Announcement API ---
export const announcementApi = {
    list(params = {}) {
        return api.get('/announcements', { params })
    },
    get(id) {
        return api.get(`/announcements/${id}`)
    },
    create(data, createdBy) {
        return api.post(`/announcements?created_by=${createdBy}`, data)
    },
}

// --- Payment API ---
export const paymentApi = {
    list(params = {}) {
        return api.get('/payments', { params })
    },
    create(data) {
        return api.post('/payments', data)
    },
    update(id, data) {
        return api.patch(`/payments/${id}`, data)
    },
}

// --- Community API ---
export const communityApi = {
    list() {
        return api.get('/communities')
    },
    get(id) {
        return api.get(`/communities/${id}`)
    },
    getByName(name) {
        return api.get('/communities/by-name', { params: { name } })
    },
}

// --- Dashboard API ---
export const dashboardApi = {
    getStats(params = {}) {
        return api.get('/stats/dashboard', { params })
    },
}

export default api
