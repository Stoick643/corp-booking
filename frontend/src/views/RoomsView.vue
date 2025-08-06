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

    <!-- Room Filters -->
    <div class="row mb-4">
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
    <div class="row g-4">
      <div 
        v-for="room in filteredRooms" 
        :key="room.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <RoomCard 
          :room="room"
          @navigate="navigateToDesks"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredRooms.length === 0 && !store.isLoading" class="row">
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import RoomCard from '../components/RoomCard.vue'
import { apiService } from '../services/api.js'
import { store } from '../stores/booking.js'

export default {
  name: 'RoomsView',
  components: {
    RoomCard
  },
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
    const selectedFilter = ref('all')

    // Computed properties
    const currentAreaName = computed(() => 
      store.currentArea?.name || `Area ${props.areaId}`
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

    // Load rooms from API
    const loadRooms = async () => {
      try {
        store.setLoading(true)
        store.clearError()
        
        const data = await apiService.fetchAreaRooms(props.areaId)
        rooms.value = data
        store.setRooms(data)
        
        console.log(`Loaded ${data.length} rooms for area ${props.areaId}`)
      } catch (error) {
        console.error('Failed to load rooms:', error)
        store.setError('Failed to load rooms. Please try again.')
      } finally {
        store.setLoading(false)
      }
    }

    // Load area data if not in store
    const loadAreaIfNeeded = async () => {
      if (!store.currentArea || store.currentArea.id !== parseInt(props.areaId)) {
        try {
          const area = await apiService.fetchArea(props.areaId)
          store.setCurrentArea(area)
        } catch (error) {
          console.error('Failed to load area:', error)
        }
      }
    }

    // Navigation handlers
    const navigateToDesks = (roomId) => {
      const room = rooms.value.find(r => r.id === roomId)
      if (room) {
        store.setCurrentRoom(room)
        router.push(`/areas/${props.areaId}/rooms/${roomId}`)
      }
    }

    const goBackToAreas = () => {
      store.setCurrentArea(null)
      router.push('/')
    }

    // Watch for area ID changes
    watch(() => props.areaId, () => {
      loadAreaIfNeeded()
      loadRooms()
    })

    // Initialize component
    onMounted(() => {
      loadAreaIfNeeded()
      loadRooms()
    })

    return {
      rooms,
      selectedFilter,
      filteredRooms,
      currentAreaName,
      bookableRoomsCount,
      roomsWithDesksCount,
      totalDesksInArea,
      navigateToDesks,
      goBackToAreas,
      store
    }
  }
}
</script>

<style scoped>
.rooms-view {
  max-width: 1200px;
  margin: 0 auto;
}

.btn-group {
  --bs-btn-padding-y: 0.375rem;
  --bs-btn-padding-x: 0.75rem;
}

.card {
  height: 100%;
}
</style>