<template>
  <div class="rooms-view">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex align-items-center mb-2">
          <button 
            class="btn btn-outline-secondary me-3"
            @click="goBackToAreas"
          >
            <i class="bi bi-arrow-left me-1"></i>
            Back to Areas
          </button>
          <div>
            <h1 class="h3 mb-0">
              <i class="bi bi-door-open me-2"></i>
              Rooms in {{ currentAreaName }}
            </h1>
          </div>
        </div>
        <p class="text-muted">
          Select a room to view available desks for booking.
        </p>
      </div>
    </div>

    <!-- Loading Spinner -->
    <div v-if="isLoading" class="loading-spinner">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button type="button" class="btn btn-sm btn-outline-danger ms-3" @click="loadRooms">
        <i class="bi bi-arrow-clockwise me-1"></i>
        Retry
      </button>
    </div>

    <!-- Room Filters -->
    <div v-else class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-body py-2">
            <div class="row align-items-center">
              <div class="col-md-6">
                <div class="btn-group" role="group" aria-label="Room type filter">
                  <input type="radio" class="btn-check" name="roomFilter" id="all" value="all" v-model="selectedFilter">
                  <label class="btn btn-outline-primary btn-sm" for="all">All Rooms</label>
                  
                  <input type="radio" class="btn-check" name="roomFilter" id="bookable" value="bookable" v-model="selectedFilter">
                  <label class="btn btn-outline-primary btn-sm" for="bookable">Bookable Only</label>
                  
                  <input type="radio" class="btn-check" name="roomFilter" id="with-desks" value="with-desks" v-model="selectedFilter">
                  <label class="btn btn-outline-primary btn-sm" for="with-desks">With Desks</label>
                </div>
              </div>
              <div class="col-md-6 text-md-end">
                <small class="text-muted">
                  {{ filteredRooms.length }} of {{ rooms.length }} rooms shown
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Rooms Grid -->
    <div v-if="!isLoading && !error" class="row g-4">
      <div 
        v-for="room in filteredRooms" 
        :key="room.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <div class="card h-100 room-card" @click="navigateToDesks(room.id)">
          <!-- Card Header -->
          <div class="card-header" :class="getRoomHeaderClass(room)">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="card-title mb-0 text-truncate">
                <i :class="getRoomIcon(room)" class="me-2"></i>
                {{ room.name }}
              </h6>
              <span class="badge" :class="getRoomBadgeClass(room)">
                {{ getRoomStatus(room) }}
              </span>
            </div>
          </div>

          <!-- Card Body -->
          <div class="card-body d-flex flex-column">
            <!-- Room Stats -->
            <div class="row text-center mb-3">
              <div class="col-6">
                <div class="stat-item">
                  <h5 class="stat-number text-primary mb-1">{{ room.desk_count }}</h5>
                  <small class="stat-label text-muted">Desks</small>
                </div>
              </div>
              <div class="col-6">
                <div class="stat-item">
                  <h5 class="stat-number text-success mb-1">{{ getAvailableDesks(room) }}</h5>
                  <small class="stat-label text-muted">Available</small>
                </div>
              </div>
            </div>

            <!-- Action Button -->
            <div class="mt-auto">
              <div class="d-grid">
                <button 
                  class="btn"
                  :class="getActionButtonClass(room)"
                  :disabled="!canNavigateToRoom(room)"
                >
                  <i :class="getActionIcon(room)" class="me-1"></i>
                  {{ getActionText(room) }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!isLoading && !error && filteredRooms.length === 0" class="row">
      <div class="col-12 text-center py-5">
        <i class="bi bi-door-closed display-1 text-muted"></i>
        <h4 class="mt-3 text-muted">No Rooms Found</h4>
        <p class="text-muted">
          {{ rooms.length === 0 ? 
            'No rooms are available in this area.' : 
            'No rooms match the current filter criteria.' 
          }}
        </p>
        <button 
          v-if="selectedFilter !== 'all'"
          class="btn btn-outline-primary"
          @click="selectedFilter = 'all'"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Rooms Summary -->
    <div v-if="rooms.length > 0" class="row mt-5">
      <div class="col-12">
        <div class="card bg-light">
          <div class="card-body">
            <h6 class="card-title">
              <i class="bi bi-info-circle me-1"></i>
              Room Summary for {{ currentAreaName }}
            </h6>
            <div class="row text-center">
              <div class="col-3">
                <h5 class="text-primary">{{ rooms.length }}</h5>
                <small class="text-muted">Total Rooms</small>
              </div>
              <div class="col-3">
                <h5 class="text-success">{{ bookableRoomsCount }}</h5>
                <small class="text-muted">Bookable</small>
              </div>
              <div class="col-3">
                <h5 class="text-info">{{ roomsWithDesksCount }}</h5>
                <small class="text-muted">With Desks</small>
              </div>
              <div class="col-3">
                <h5 class="text-warning">{{ totalDesksInArea }}</h5>
                <small class="text-muted">Total Desks</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService } from '../services/api.js'

export default {
  name: 'RoomsViewFixed',
  props: {
    areaId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    const rooms = ref([])
    const currentArea = ref(null)
    const selectedFilter = ref('all')
    const isLoading = ref(false)
    const error = ref(null)

    console.log('RoomsViewFixed: Component setup() called, areaId:', props.areaId)

    // Computed properties
    const currentAreaName = computed(() => 
      currentArea.value?.name || `Area ${props.areaId}`
    )

    const filteredRooms = computed(() => {
      switch (selectedFilter.value) {
        case 'bookable':
          return rooms.value.filter(room => room.is_bookable)
        case 'with-desks':
          return rooms.value.filter(room => room.desk_count > 0)
        default:
          return rooms.value
      }
    })

    const bookableRoomsCount = computed(() =>
      rooms.value.filter(room => room.is_bookable).length
    )

    const roomsWithDesksCount = computed(() =>
      rooms.value.filter(room => room.desk_count > 0).length
    )

    const totalDesksInArea = computed(() =>
      rooms.value.reduce((sum, room) => sum + room.desk_count, 0)
    )

    // Helper functions for room display
    const getAvailableDesks = (room) => Math.max(0, Math.floor(room.desk_count * 0.7))
    const canNavigateToRoom = (room) => room.desk_count > 0
    
    const getRoomHeaderClass = (room) => {
      if (!canNavigateToRoom(room)) return 'bg-light text-dark'
      return getAvailableDesks(room) > 0 ? 'bg-success text-white' : 'bg-warning text-dark'
    }

    const getRoomBadgeClass = (room) => {
      if (!canNavigateToRoom(room)) return 'bg-secondary'
      return room.is_bookable ? 'bg-primary' : 'bg-info'
    }

    const getRoomIcon = (room) => {
      if (room.is_bookable) return 'bi bi-calendar-check'
      return canNavigateToRoom(room) ? 'bi bi-person-workspace' : 'bi bi-door-closed'
    }

    const getRoomStatus = (room) => {
      if (room.is_bookable) return 'Bookable'
      return canNavigateToRoom(room) ? 'Workspace' : 'Meeting'
    }

    const getActionButtonClass = (room) => {
      if (!canNavigateToRoom(room)) return 'btn-outline-secondary'
      return getAvailableDesks(room) > 0 ? 'btn-success' : 'btn-warning'
    }

    const getActionIcon = (room) => {
      if (!canNavigateToRoom(room)) return 'bi bi-x-circle'
      return 'bi bi-arrow-right'
    }

    const getActionText = (room) => {
      if (!canNavigateToRoom(room)) return 'No Desks'
      return getAvailableDesks(room) > 0 ? 'View Desks' : 'Fully Occupied'
    }

    // Load rooms from API
    const loadRooms = async () => {
      if (isLoading.value) return

      try {
        console.log('RoomsViewFixed: Starting to load rooms for area:', props.areaId)
        isLoading.value = true
        error.value = null
        
        // Load area info and rooms in parallel
        const [areaData, roomsData] = await Promise.all([
          apiService.fetchArea(props.areaId),
          apiService.fetchAreaRooms(props.areaId)
        ])
        
        console.log('RoomsViewFixed: Loaded area:', areaData.name)
        console.log('RoomsViewFixed: Loaded rooms:', roomsData.length)
        
        currentArea.value = areaData
        rooms.value = roomsData
      } catch (err) {
        console.error('RoomsViewFixed: Failed to load rooms:', err)
        error.value = 'Failed to load rooms. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    // Navigation handlers
    const navigateToDesks = (roomId) => {
      if (canNavigateToRoom(rooms.value.find(r => r.id === roomId))) {
        console.log('RoomsViewFixed: Navigating to room:', roomId)
        router.push(`/areas/${props.areaId}/rooms/${roomId}`)
      }
    }

    const goBackToAreas = () => {
      console.log('RoomsViewFixed: Going back to areas')
      router.push('/')
    }

    // Initialize component
    onMounted(() => {
      console.log('RoomsViewFixed: Component mounted')
      loadRooms()
    })

    return {
      rooms,
      currentAreaName,
      selectedFilter,
      filteredRooms,
      bookableRoomsCount,
      roomsWithDesksCount,
      totalDesksInArea,
      isLoading,
      error,
      getRoomHeaderClass,
      getRoomBadgeClass,
      getRoomIcon,
      getRoomStatus,
      getActionButtonClass,
      getActionIcon,
      getActionText,
      getAvailableDesks,
      canNavigateToRoom,
      navigateToDesks,
      goBackToAreas,
      loadRooms
    }
  }
}
</script>

<style scoped>
.rooms-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.room-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.stat-item {
  padding: 0.25rem;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1;
}

.stat-label {
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  font-size: 0.7rem;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.btn-group {
  --bs-btn-padding-y: 0.375rem;
  --bs-btn-padding-x: 0.75rem;
}
</style>