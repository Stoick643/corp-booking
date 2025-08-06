import axios from 'axios'

// Configure Axios instance for Django API
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor for debugging
api.interceptors.request.use(request => {
  console.log('API Request:', request.method.toUpperCase(), request.url)
  return request
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.config.url, 'Data length:', response.data?.length || 'N/A')
    return response
  },
  error => {
    console.error('API Error:', {
      status: error.response?.status,
      message: error.message,
      url: error.config?.url,
      data: error.response?.data
    })
    throw error
  }
)

// API service methods
export const apiService = {
  // Areas API
  async fetchAreas() {
    const response = await api.get('/areas/')
    return response.data
  },

  async fetchArea(areaId) {
    const response = await api.get(`/areas/${areaId}/`)
    return response.data
  },

  async fetchAreaRooms(areaId) {
    const response = await api.get(`/areas/${areaId}/rooms/`)
    return response.data
  },

  async fetchAreaDesks(areaId) {
    const response = await api.get(`/areas/${areaId}/desks/`)
    return response.data
  },

  // Rooms API
  async fetchRooms() {
    const response = await api.get('/rooms/')
    return response.data
  },

  async fetchRoom(roomId) {
    const response = await api.get(`/rooms/${roomId}/`)
    return response.data
  },

  async fetchRoomDesks(roomId) {
    const response = await api.get(`/rooms/${roomId}/desks/`)
    return response.data
  },

  // Desks API
  async fetchDesks() {
    const response = await api.get('/desks/')
    return response.data
  },

  async fetchDesk(deskId) {
    const response = await api.get(`/desks/${deskId}/`)
    return response.data
  },

  // Users API
  async fetchUsers() {
    const response = await api.get('/users/')
    return response.data
  },

  // Reservations API
  async fetchReservations() {
    const response = await api.get('/reservations/')
    return response.data
  },

  async createReservation(reservationData) {
    const response = await api.post('/reservations/', reservationData)
    return response.data
  },

  async updateReservation(reservationId, updateData) {
    const response = await api.patch(`/reservations/${reservationId}/`, updateData)
    return response.data
  },

  async deleteReservation(reservationId) {
    const response = await api.delete(`/reservations/${reservationId}/`)
    return response.data
  }
}

export default api