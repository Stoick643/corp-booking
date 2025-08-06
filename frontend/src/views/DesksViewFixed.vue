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
      <button type="button" class="btn btn-sm btn-outline-danger ms-3" @click="loadDesks">
        <i class="bi bi-arrow-clockwise me-1"></i>
        Retry
      </button>
    </div>

    <!-- Desk Filters and Legend -->
    <div v-else class="row mb-4">
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
    <div v-if="!isLoading && !error" class="row g-3">
      <div 
        v-for="desk in filteredDesks" 
        :key="desk.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <div 
          class="card h-100 desk-card"
          :class="getDeskCardClass(desk)"
          @click="handleDeskClick(desk)"
          :role="desk.status === 'available' ? 'button' : undefined"
          :tabindex="desk.status === 'available' ? 0 : undefined"
        >
          <!-- Card Header with Status -->
          <div class="card-header py-2" :class="getDeskHeaderClass(desk)">
            <div class="d-flex justify-content-between align-items-center">
              <small class="fw-bold mb-0">
                <i :class="getDeskIcon(desk)" class="me-1"></i>
                {{ desk.identifier }}
              </small>
              <span class="badge badge-sm" :class="getDeskBadgeClass(desk)">
                {{ getDeskStatusText(desk) }}
              </span>
            </div>
          </div>

          <!-- Card Body -->
          <div class="card-body d-flex flex-column p-3">
            <!-- Desk Position (if available) -->
            <div v-if="desk.pos_x !== null && desk.pos_y !== null" class="position-info mb-2">
              <small class="text-muted d-flex align-items-center">
                <i class="bi bi-geo me-1"></i>
                Position: {{ desk.pos_x }}, {{ desk.pos_y }}
              </small>
            </div>

            <!-- Room and Area Info -->
            <div class="location-info mb-3">
              <small class="text-muted d-block">
                <i class="bi bi-door-open me-1"></i>
                {{ desk.room_name }}
              </small>
              <small class="text-muted d-block">
                <i class="bi bi-building me-1"></i>
                {{ desk.area_name }}
              </small>
            </div>

            <!-- Status Description -->
            <div class="status-description mb-3">
              <p class="small mb-0" :class="getDeskDescriptionClass(desk)">
                {{ getDeskDescription(desk) }}
              </p>
            </div>

            <!-- Action Button -->
            <div class="mt-auto">
              <div class="d-grid">
                <button 
                  class="btn btn-sm"
                  :class="getDeskActionButtonClass(desk)"
                  :disabled="desk.status !== 'available'"
                  @click.stop="handleDeskClick(desk)"
                >
                  <i :class="getDeskActionIcon(desk)" class="me-1"></i>
                  {{ getDeskActionText(desk) }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!isLoading && !error && filteredDesks.length === 0" class="row">
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService } from '../services/api.js'

export default {
  name: 'DesksViewFixed',
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
    const currentArea = ref(null)
    const currentRoom = ref(null)
    const selectedFilter = ref('all')
    const isLoading = ref(false)
    const error = ref(null)

    console.log('DesksViewFixed: Component setup() called, areaId:', props.areaId, 'roomId:', props.roomId)

    // Computed properties
    const currentAreaName = computed(() => 
      currentArea.value?.name || `Area ${props.areaId}`
    )

    const currentRoomName = computed(() => 
      currentRoom.value?.name || `Room ${props.roomId}`
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

    // Helper functions for desk display
    const getDeskCardClass = (desk) => ({
      'desk-available': desk.status === 'available',
      'desk-permanent': desk.status === 'permanent',
      'desk-disabled': desk.status === 'disabled',
      'border-success': desk.status === 'available',
      'border-warning': desk.status === 'permanent',
      'border-danger': desk.status === 'disabled',
      'opacity-75': desk.status === 'disabled'
    })

    const getDeskHeaderClass = (desk) => {
      if (desk.status === 'available') return 'bg-success text-white'
      if (desk.status === 'permanent') return 'bg-warning text-dark'
      if (desk.status === 'disabled') return 'bg-danger text-white'
      return 'bg-secondary text-white'
    }

    const getDeskBadgeClass = (desk) => {
      if (desk.status === 'available') return 'bg-light text-success'
      if (desk.status === 'permanent') return 'bg-light text-warning'
      if (desk.status === 'disabled') return 'bg-light text-danger'
      return 'bg-light text-secondary'
    }

    const getDeskDescriptionClass = (desk) => {
      if (desk.status === 'available') return 'text-success'
      if (desk.status === 'permanent') return 'text-warning'
      if (desk.status === 'disabled') return 'text-danger'
      return 'text-muted'
    }

    const getDeskActionButtonClass = (desk) => {
      if (desk.status === 'available') return 'btn-success'
      if (desk.status === 'permanent') return 'btn-outline-warning'
      if (desk.status === 'disabled') return 'btn-outline-danger'
      return 'btn-outline-secondary'
    }

    const getDeskIcon = (desk) => {
      if (desk.status === 'available') return 'bi bi-check-circle-fill'
      if (desk.status === 'permanent') return 'bi bi-person-fill'
      if (desk.status === 'disabled') return 'bi bi-x-circle-fill'
      return 'bi bi-question-circle'
    }

    const getDeskStatusText = (desk) => {
      if (desk.status === 'available') return 'Available'
      if (desk.status === 'permanent') return 'Permanent'
      if (desk.status === 'disabled') return 'Disabled'
      return 'Unknown'
    }

    const getDeskDescription = (desk) => {
      if (desk.status === 'available') return 'This desk is available for booking.'
      if (desk.status === 'permanent') return 'This desk has a permanent assignment.'
      if (desk.status === 'disabled') return 'This desk is currently out of service.'
      return 'Status unknown.'
    }

    const getDeskActionText = (desk) => {
      if (desk.status === 'available') return 'Book Desk'
      if (desk.status === 'permanent') return 'Assigned'
      if (desk.status === 'disabled') return 'Unavailable'
      return 'N/A'
    }

    const getDeskActionIcon = (desk) => {
      if (desk.status === 'available') return 'bi bi-calendar-plus'
      if (desk.status === 'permanent') return 'bi bi-person-check'
      if (desk.status === 'disabled') return 'bi bi-exclamation-triangle'
      return 'bi bi-question'
    }

    // Load desks from API
    const loadDesks = async () => {
      if (isLoading.value) return

      try {
        console.log('DesksViewFixed: Starting to load desks for room:', props.roomId)
        isLoading.value = true
        error.value = null
        
        // Load area, room, and desks data
        const [areaData, roomData, desksData] = await Promise.all([
          apiService.fetchArea(props.areaId),
          apiService.fetchRoom(props.roomId), 
          apiService.fetchRoomDesks(props.roomId)
        ])
        
        console.log('DesksViewFixed: Loaded area:', areaData.name)
        console.log('DesksViewFixed: Loaded room:', roomData.name)
        console.log('DesksViewFixed: Loaded desks:', desksData.length)
        
        currentArea.value = areaData
        currentRoom.value = roomData
        desks.value = desksData
      } catch (err) {
        console.error('DesksViewFixed: Failed to load desks:', err)
        error.value = 'Failed to load desks. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    // Event handlers
    const handleDeskClick = (desk) => {
      if (desk.status === 'available') {
        console.log('DesksViewFixed: One-click booking not available in room view')
        alert('💡 Tip: For one-click booking, use the Area Workspace view instead!\n\nGo to Areas → Select Area → View all desks with instant booking.')
      }
    }

    const goBackToRooms = () => {
      console.log('DesksViewFixed: Going back to rooms')
      router.push(`/areas/${props.areaId}`)
    }

    // Initialize component
    onMounted(() => {
      console.log('DesksViewFixed: Component mounted')
      loadDesks()
    })

    return {
      desks,
      currentAreaName,
      currentRoomName,
      selectedFilter,
      filteredDesks,
      availableCount,
      permanentCount,
      disabledCount,
      isLoading,
      error,
      getDeskCardClass,
      getDeskHeaderClass,
      getDeskBadgeClass,
      getDeskDescriptionClass,
      getDeskActionButtonClass,
      getDeskIcon,
      getDeskStatusText,
      getDeskDescription,
      getDeskActionText,
      getDeskActionIcon,
      handleDeskClick,
      goBackToRooms,
      loadDesks
    }
  }
}
</script>

<style scoped>
.desks-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.desk-card {
  transition: all 0.3s ease;
}

.desk-card[role="button"] {
  cursor: pointer;
}

.desk-card[role="button"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.desk-available[role="button"]:hover {
  box-shadow: 0 6px 20px rgba(25, 135, 84, 0.2);
}

.position-info {
  font-family: 'Courier New', monospace;
}

.location-info {
  border-bottom: 1px solid rgba(0,0,0,0.1);
  padding-bottom: 0.5rem;
}

.status-description {
  font-style: italic;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.2rem 0.4rem;
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

.progress {
  background-color: rgba(0,0,0,0.1);
}

.desk-disabled {
  pointer-events: none;
}
</style>