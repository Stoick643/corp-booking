<template>
  <div class="desks-view">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex align-items-center mb-2">
          <button 
            class="btn btn-outline-secondary me-3"
            @click="goBackToRooms"
          >
            <i class="bi bi-arrow-left me-1"></i>
            Back to Rooms
          </button>
          <div>
            <h1 class="h3 mb-0">
              <i class="bi bi-person-workspace me-2"></i>
              Desks in {{ currentRoomName }}
            </h1>
          </div>
        </div>
        <p class="text-muted">
          Select an available desk to make a booking.
          <span class="badge bg-secondary ms-2">{{ currentAreaName }}</span>
        </p>
      </div>
    </div>

    <!-- Desk Filters and Legend -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-body py-3">
            <div class="row align-items-center">
              <div class="col-md-6">
                <div class="btn-group" role="group" aria-label="Desk status filter">
                  <input type="radio" class="btn-check" name="deskFilter" id="all-desks" value="all" v-model="selectedFilter">
                  <label class="btn btn-outline-primary btn-sm" for="all-desks">All</label>
                  
                  <input type="radio" class="btn-check" name="deskFilter" id="available-desks" value="available" v-model="selectedFilter">
                  <label class="btn btn-outline-success btn-sm" for="available-desks">Available</label>
                  
                  <input type="radio" class="btn-check" name="deskFilter" id="permanent-desks" value="permanent" v-model="selectedFilter">
                  <label class="btn btn-outline-warning btn-sm" for="permanent-desks">Permanent</label>
                  
                  <input type="radio" class="btn-check" name="deskFilter" id="disabled-desks" value="disabled" v-model="selectedFilter">
                  <label class="btn btn-outline-danger btn-sm" for="disabled-desks">Disabled</label>
                </div>
              </div>
              <div class="col-md-6">
                <!-- Status Legend -->
                <div class="d-flex flex-wrap gap-3 justify-content-md-end">
                  <small class="d-flex align-items-center">
                    <span class="status-indicator bg-success me-1"></span>
                    Available ({{ availableCount }})
                  </small>
                  <small class="d-flex align-items-center">
                    <span class="status-indicator bg-warning me-1"></span>
                    Permanent ({{ permanentCount }})
                  </small>
                  <small class="d-flex align-items-center">
                    <span class="status-indicator bg-danger me-1"></span>
                    Disabled ({{ disabledCount }})
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Desks Grid -->
    <div class="row g-3">
      <div 
        v-for="desk in filteredDesks" 
        :key="desk.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <DeskCard 
          :desk="desk"
          @book="navigateToBooking"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredDesks.length === 0 && !store.isLoading" class="row">
      <div class="col-12 text-center py-5">
        <i class="bi bi-laptop display-1 text-muted"></i>
        <h4 class="mt-3 text-muted">No Desks Found</h4>
        <p class="text-muted">
          {{ desks.length === 0 ? 
            'No desks are available in this room.' : 
            `No ${selectedFilter === 'all' ? '' : selectedFilter} desks found.` 
          }}
        </p>
        <button 
          v-if="selectedFilter !== 'all'"
          class="btn btn-outline-primary"
          @click="selectedFilter = 'all'"
        >
          Show All Desks
        </button>
      </div>
    </div>

    <!-- Room Summary -->
    <div v-if="desks.length > 0" class="row mt-5">
      <div class="col-12">
        <div class="card bg-light">
          <div class="card-body">
            <h6 class="card-title">
              <i class="bi bi-info-circle me-1"></i>
              Desk Summary for {{ currentRoomName }}
            </h6>
            <div class="row text-center">
              <div class="col-3">
                <h5 class="text-primary">{{ desks.length }}</h5>
                <small class="text-muted">Total Desks</small>
              </div>
              <div class="col-3">
                <h5 class="text-success">{{ availableCount }}</h5>
                <small class="text-muted">Available</small>
              </div>
              <div class="col-3">
                <h5 class="text-warning">{{ permanentCount }}</h5>
                <small class="text-muted">Permanent</small>
              </div>
              <div class="col-3">
                <h5 class="text-danger">{{ disabledCount }}</h5>
                <small class="text-muted">Disabled</small>
              </div>
            </div>
            <div class="progress mt-3" style="height: 8px;">
              <div 
                class="progress-bar bg-success" 
                :style="{ width: (availableCount/desks.length)*100 + '%' }"
              ></div>
              <div 
                class="progress-bar bg-warning" 
                :style="{ width: (permanentCount/desks.length)*100 + '%' }"
              ></div>
              <div 
                class="progress-bar bg-danger" 
                :style="{ width: (disabledCount/desks.length)*100 + '%' }"
              ></div>
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
import DeskCard from '../components/DeskCard.vue'
import { apiService } from '../services/api.js'
import { store } from '../stores/booking.js'

export default {
  name: 'DesksView',
  components: {
    DeskCard
  },
  props: {
    areaId: {
      type: String,
      required: true
    },
    roomId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    const desks = ref([])
    const selectedFilter = ref('all')

    // Computed properties
    const currentAreaName = computed(() => 
      store.currentArea?.name || `Area ${props.areaId}`
    )

    const currentRoomName = computed(() => 
      store.currentRoom?.name || `Room ${props.roomId}`
    )

    const filteredDesks = computed(() => {
      if (selectedFilter.value === 'all') {
        return desks.value
      }
      return desks.value.filter(desk => desk.status === selectedFilter.value)
    })

    // Status counts
    const availableCount = computed(() =>
      desks.value.filter(desk => desk.status === 'available').length
    )

    const permanentCount = computed(() =>
      desks.value.filter(desk => desk.status === 'permanent').length
    )

    const disabledCount = computed(() =>
      desks.value.filter(desk => desk.status === 'disabled').length
    )

    // Load desks from API
    const loadDesks = async () => {
      try {
        store.setLoading(true)
        store.clearError()
        
        const data = await apiService.fetchRoomDesks(props.roomId)
        desks.value = data
        store.setDesks(data)
        
        console.log(`Loaded ${data.length} desks for room ${props.roomId}`)
      } catch (error) {
        console.error('Failed to load desks:', error)
        store.setError('Failed to load desks. Please try again.')
      } finally {
        store.setLoading(false)
      }
    }

    // Load room data if not in store
    const loadRoomIfNeeded = async () => {
      if (!store.currentRoom || store.currentRoom.id !== parseInt(props.roomId)) {
        try {
          const room = await apiService.fetchRoom(props.roomId)
          store.setCurrentRoom(room)
        } catch (error) {
          console.error('Failed to load room:', error)
        }
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
    const navigateToBooking = (deskId) => {
      const desk = desks.value.find(d => d.id === deskId)
      if (desk && desk.status === 'available') {
        store.setCurrentDesk(desk)
        router.push(`/desks/${deskId}/book`)
      }
    }

    const goBackToRooms = () => {
      store.setCurrentRoom(null)
      router.push(`/areas/${props.areaId}`)
    }

    // Watch for route parameter changes
    watch(() => [props.areaId, props.roomId], () => {
      loadAreaIfNeeded()
      loadRoomIfNeeded()
      loadDesks()
    })

    // Initialize component
    onMounted(() => {
      loadAreaIfNeeded()
      loadRoomIfNeeded()
      loadDesks()
    })

    return {
      desks,
      selectedFilter,
      filteredDesks,
      currentAreaName,
      currentRoomName,
      availableCount,
      permanentCount,
      disabledCount,
      navigateToBooking,
      goBackToRooms,
      store
    }
  }
}
</script>

<style scoped>
.desks-view {
  max-width: 1200px;
  margin: 0 auto;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.btn-group {
  --bs-btn-padding-y: 0.375rem;
  --bs-btn-padding-x: 0.75rem;
}

.progress {
  background-color: rgba(0,0,0,0.1);
}

.card {
  height: 100%;
}
</style>