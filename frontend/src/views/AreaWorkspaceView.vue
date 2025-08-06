<template>
  <div class="area-workspace-view">
    <div class="row">
      <!-- Left Sidebar: Date Selector -->
      <div class="col-md-3 col-lg-2">
        <DateSelector @date-selected="onDateSelected" />
      </div>
      
      <!-- Main Content Area -->
      <div class="col-md-9 col-lg-10">
        <!-- Page Header -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="d-flex align-items-center">
                <button 
                  class="btn btn-outline-secondary me-3"
                  @click="goBackToAreas"
                >
                  <i class="bi bi-arrow-left me-1"></i>
                  Back to Areas
                </button>
                <div>
                  <h1 class="h3 mb-0">
                    <i class="bi bi-person-workspace me-2"></i>
                    {{ currentAreaName }} - {{ selectedDateDisplay }}
                  </h1>
                </div>
              </div>
              
              <!-- View Mode Toggle -->
              <div class="view-mode-toggle">
                <div class="btn-group" role="group" aria-label="View mode">
                  <input 
                    type="radio" 
                    class="btn-check" 
                    name="viewMode" 
                    id="schematic-view" 
                    value="schematic" 
                    v-model="viewMode"
                  >
                  <label class="btn btn-outline-primary" for="schematic-view">
                    <i class="bi bi-grid-3x3-gap me-1"></i>
                    Schematic
                  </label>
                  
                  <input 
                    type="radio" 
                    class="btn-check" 
                    name="viewMode" 
                    id="map-view" 
                    value="map" 
                    v-model="viewMode"
                    :disabled="!isMapViewAvailable"
                  >
                  <label class="btn btn-outline-primary" for="map-view">
                    <i class="bi bi-map me-1"></i>
                    Map View
                  </label>
                </div>
              </div>
            </div>
            <p class="text-muted">
              Select an available desk to make a booking. Selected date: <strong>{{ selectedDateDisplay }}</strong>
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
      <button type="button" class="btn btn-sm btn-outline-danger ms-3" @click="loadAreaDesks">
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
                  
                  <input type="radio" class="btn-check" name="deskFilter" id="reserved-desks" value="reserved" v-model="selectedFilter">
                  <label class="btn btn-outline-info btn-sm" for="reserved-desks">Reserved</label>
                  
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
                    <span class="status-indicator bg-info me-1"></span>
                    Reserved ({{ reservedCount }})
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

    <!-- Desks Grouped by Room -->
    <div v-if="!isLoading && !error" class="rooms-container">
      <div 
        v-for="(roomGroup, roomName) in groupedDesks" 
        :key="roomName"
        class="room-section mb-4"
        :class="getRoomSectionClass(roomName)"
      >
        <!-- Room Header -->
        <div class="room-header mb-3">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="room-title mb-0">
              <i class="bi bi-door-open me-2"></i>
              {{ roomName }}
            </h5>
            <span class="badge bg-primary">
              {{ roomGroup.length }} desk{{ roomGroup.length !== 1 ? 's' : '' }}
            </span>
          </div>
        </div>

        <!-- Room Desks Grid -->
        <div class="row g-3">
          <div 
            v-for="desk in roomGroup" 
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
          </div> <!-- End col for desk -->
        </div> <!-- End row for room desks -->
      </div> <!-- End room-section -->
    </div> <!-- End room loop -->
    </div> <!-- End rooms-container -->

    <!-- Empty State -->
    <div v-if="!isLoading && !error && Object.keys(groupedDesks).length === 0" class="row">
      <div class="col-12 text-center py-5">
        <i class="bi bi-laptop display-1 text-muted"></i>
        <h4 class="mt-3 text-muted">No Desks Found</h4>
        <p class="text-muted">
          {{ desks.length === 0 ? 
            'No desks are available in this area.' : 
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

    <!-- Area Summary -->
    <div v-if="desks.length > 0" class="row mt-5">
      <div class="col-12">
        <div class="card bg-light">
          <div class="card-body">
            <h6 class="card-title">
              <i class="bi bi-info-circle me-1"></i>
              Desk Summary for {{ currentAreaName }}
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
                <h5 class="text-info">{{ reservedCount }}</h5>
                <small class="text-muted">Reserved</small>
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
                class="progress-bar bg-info" 
                :style="{ width: (reservedCount/desks.length)*100 + '%' }"
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
      </div> <!-- End main content area col-md-9 col-lg-10 -->
    </div> <!-- End row -->
  </div> <!-- End area-workspace-view -->
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService } from '../services/api.js'
import DateSelector from '../components/DateSelector.vue'

export default {
  name: 'AreaWorkspaceView',
  components: {
    DateSelector
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
    const desks = ref([])
    const currentArea = ref(null)
    const selectedFilter = ref('all')
    const selectedDate = ref(new Date())
    const viewMode = ref('schematic')
    const isMapViewAvailable = ref(false)
    const isLoading = ref(false)
    const error = ref(null)
    
    // Set selectedDate to today initially
    selectedDate.value.setHours(0, 0, 0, 0)

    console.log('AreaWorkspaceView: Component setup() called, areaId:', props.areaId)

    // Computed properties
    const currentAreaName = computed(() => 
      currentArea.value?.name || `Area ${props.areaId}`
    )
    
    const selectedDateDisplay = computed(() => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      if (selectedDate.value.toDateString() === today.toDateString()) {
        return 'Today'
      }
      
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      
      if (selectedDate.value.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow'
      }
      
      return selectedDate.value.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short', 
        day: 'numeric'
      })
    })

    const filteredDesks = computed(() => {
      if (selectedFilter.value === 'all') {
        return desks.value
      }
      return desks.value.filter(desk => desk.status === selectedFilter.value)
    })

    // Group filtered desks by room
    const groupedDesks = computed(() => {
      return filteredDesks.value.reduce((groups, desk) => {
        const roomName = desk.room_name || 'Unknown Room'
        if (!groups[roomName]) {
          groups[roomName] = []
        }
        groups[roomName].push(desk)
        return groups
      }, {})
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
    
    const reservedCount = computed(() =>
      desks.value.filter(desk => desk.status === 'reserved').length
    )

    // Room section styling with different colors for visual separation
    const getRoomSectionClass = (roomName) => {
      // Generate consistent color based on room name
      const roomTypes = ['office', 'meeting', 'open', 'conference', 'lounge', 'kitchen', 'break']
      const colorClasses = [
        'room-color-blue',
        'room-color-green', 
        'room-color-orange',
        'room-color-purple',
        'room-color-teal',
        'room-color-pink',
        'room-color-indigo'
      ]
      
      let colorIndex = 0
      for (let i = 0; i < roomName.length; i++) {
        colorIndex += roomName.charCodeAt(i)
      }
      colorIndex = colorIndex % colorClasses.length
      
      return colorClasses[colorIndex]
    }

    // Helper functions for desk display (updated with reserved status)
    const getDeskCardClass = (desk) => ({
      'desk-available': desk.status === 'available',
      'desk-reserved': desk.status === 'reserved',
      'desk-permanent': desk.status === 'permanent',
      'desk-disabled': desk.status === 'disabled',
      'border-success': desk.status === 'available',
      'border-info': desk.status === 'reserved',
      'border-warning': desk.status === 'permanent',
      'border-danger': desk.status === 'disabled',
      'opacity-75': desk.status === 'disabled'
    })

    const getDeskHeaderClass = (desk) => {
      if (desk.status === 'available') return 'bg-success text-white'
      if (desk.status === 'reserved') return 'bg-info text-white'
      if (desk.status === 'permanent') return 'bg-warning text-dark'
      if (desk.status === 'disabled') return 'bg-danger text-white'
      return 'bg-secondary text-white'
    }

    const getDeskBadgeClass = (desk) => {
      if (desk.status === 'available') return 'bg-light text-success'
      if (desk.status === 'reserved') return 'bg-light text-info'
      if (desk.status === 'permanent') return 'bg-light text-warning'
      if (desk.status === 'disabled') return 'bg-light text-danger'
      return 'bg-light text-secondary'
    }

    const getDeskDescriptionClass = (desk) => {
      if (desk.status === 'available') return 'text-success'
      if (desk.status === 'reserved') return 'text-info'
      if (desk.status === 'permanent') return 'text-warning'
      if (desk.status === 'disabled') return 'text-danger'
      return 'text-muted'
    }

    const getDeskActionButtonClass = (desk) => {
      if (desk.status === 'available') return 'btn-success'
      if (desk.status === 'reserved') return 'btn-outline-info'
      if (desk.status === 'permanent') return 'btn-outline-warning'
      if (desk.status === 'disabled') return 'btn-outline-danger'
      return 'btn-outline-secondary'
    }

    const getDeskIcon = (desk) => {
      if (desk.status === 'available') return 'bi bi-check-circle-fill'
      if (desk.status === 'reserved') return 'bi bi-calendar-check-fill'
      if (desk.status === 'permanent') return 'bi bi-person-fill'
      if (desk.status === 'disabled') return 'bi bi-x-circle-fill'
      return 'bi bi-question-circle'
    }

    const getDeskStatusText = (desk) => {
      if (desk.status === 'available') return 'Available'
      if (desk.status === 'reserved') return 'Reserved'
      if (desk.status === 'permanent') return 'Permanent'
      if (desk.status === 'disabled') return 'Disabled'
      return 'Unknown'
    }

    const getDeskDescription = (desk) => {
      if (desk.status === 'available') return 'This desk is available for booking.'
      if (desk.status === 'reserved') return 'This desk is already booked.'
      if (desk.status === 'permanent') return 'This desk has a permanent assignment.'
      if (desk.status === 'disabled') return 'This desk is currently out of service.'
      return 'Status unknown.'
    }

    const getDeskActionText = (desk) => {
      if (desk.status === 'available') return 'Book Desk'
      if (desk.status === 'reserved') return 'Booked'
      if (desk.status === 'permanent') return 'Assigned'
      if (desk.status === 'disabled') return 'Unavailable'
      return 'N/A'
    }

    const getDeskActionIcon = (desk) => {
      if (desk.status === 'available') return 'bi bi-calendar-plus'
      if (desk.status === 'reserved') return 'bi bi-calendar-check'
      if (desk.status === 'permanent') return 'bi bi-person-check'
      if (desk.status === 'disabled') return 'bi bi-exclamation-triangle'
      return 'bi bi-question'
    }

    // Load desks from API - using fetchAreaDesks instead of fetchRoomDesks
    const loadAreaDesks = async () => {
      if (isLoading.value) return

      try {
        console.log('AreaDesksView: Starting to load desks for area:', props.areaId)
        isLoading.value = true
        error.value = null
        
        // Load area info and all desks in area
        const [areaData, desksData] = await Promise.all([
          apiService.fetchArea(props.areaId),
          apiService.fetchAreaDesks(props.areaId)
        ])
        
        console.log('AreaDesksView: Loaded area:', areaData.name)
        console.log('AreaDesksView: Loaded desks:', desksData.length)
        
        currentArea.value = areaData
        desks.value = desksData
      } catch (err) {
        console.error('AreaWorkspaceView: Failed to load area desks:', err)
        error.value = 'Failed to load area desks. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    // Event handlers
    const handleDeskClick = async (desk) => {
      if (desk.status === 'available') {
        console.log('AreaWorkspaceView: Quick booking desk:', desk.id, 'for date:', selectedDate.value)
        
        try {
          // Call quick booking API
          const result = await apiService.createQuickReservation(desk.id, selectedDate.value)
          
          console.log('AreaWorkspaceView: Booking successful:', result)
          
          // Update the desk status in local state
          const deskIndex = desks.value.findIndex(d => d.id === desk.id)
          if (deskIndex !== -1) {
            desks.value[deskIndex] = {
              ...desks.value[deskIndex],
              status: 'reserved' // Update status to show it's booked
            }
          }
          
          // TODO: Show success notification
          alert(`✅ Success! Desk ${desk.identifier} booked for ${selectedDateDisplay.value}`)
          
        } catch (err) {
          console.error('AreaWorkspaceView: Booking failed:', err)
          
          // Extract error message
          const errorMessage = err.response?.data?.error || 
                              err.response?.data?.message || 
                              'Booking failed. Please try again.'
          
          // TODO: Show error notification  
          alert(`❌ Booking Error: ${errorMessage}`)
        }
      }
    }

    const goBackToAreas = () => {
      console.log('AreaWorkspaceView: Going back to areas')
      router.push('/')
    }

    // Date selection handler
    const onDateSelected = (date) => {
      console.log('AreaWorkspaceView: Date selected:', date)
      selectedDate.value = new Date(date)
      selectedDate.value.setHours(0, 0, 0, 0)
      // TODO: Reload desk availability for the new date
      // loadAreaDesksForDate(date)
    }

    // View mode functions
    const toggleViewMode = () => {
      viewMode.value = viewMode.value === 'schematic' ? 'map' : 'schematic'
      console.log('AreaWorkspaceView: View mode changed to:', viewMode.value)
    }

    const isViewModeAvailable = (mode) => {
      if (mode === 'map') {
        return isMapViewAvailable.value
      }
      return true
    }

    // Initialize component
    onMounted(() => {
      console.log('AreaWorkspaceView: Component mounted')
      loadAreaDesks()
    })

    return {
      desks,
      currentAreaName,
      selectedFilter,
      selectedDate,
      selectedDateDisplay,
      viewMode,
      isMapViewAvailable,
      filteredDesks,
      groupedDesks,
      availableCount,
      reservedCount,
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
      getRoomSectionClass,
      handleDeskClick,
      goBackToAreas,
      onDateSelected,
      toggleViewMode,
      isViewModeAvailable,
      loadAreaDesks
    }
  }
}
</script>

<style scoped>
.area-workspace-view {
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

/* Room section styling with color coding */
.room-section {
  padding: 1.5rem;
  border-radius: 12px;
  border: 2px solid;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  background: rgba(255, 255, 255, 0.9);
}

.room-header {
  border-bottom: 2px solid rgba(0,0,0,0.1);
  padding-bottom: 0.75rem;
}

.room-title {
  font-weight: 600;
  color: #333;
}

/* Room color classes for visual separation */
.room-color-blue {
  border-color: #0d6efd;
  background: rgba(13, 110, 253, 0.05);
}

.room-color-blue .room-header {
  border-bottom-color: rgba(13, 110, 253, 0.2);
}

.room-color-green {
  border-color: #198754;
  background: rgba(25, 135, 84, 0.05);
}

.room-color-green .room-header {
  border-bottom-color: rgba(25, 135, 84, 0.2);
}

.room-color-orange {
  border-color: #fd7e14;
  background: rgba(253, 126, 20, 0.05);
}

.room-color-orange .room-header {
  border-bottom-color: rgba(253, 126, 20, 0.2);
}

.room-color-purple {
  border-color: #6f42c1;
  background: rgba(111, 66, 193, 0.05);
}

.room-color-purple .room-header {
  border-bottom-color: rgba(111, 66, 193, 0.2);
}

.room-color-teal {
  border-color: #20c997;
  background: rgba(32, 201, 151, 0.05);
}

.room-color-teal .room-header {
  border-bottom-color: rgba(32, 201, 151, 0.2);
}

.room-color-pink {
  border-color: #d63384;
  background: rgba(214, 51, 132, 0.05);
}

.room-color-pink .room-header {
  border-bottom-color: rgba(214, 51, 132, 0.2);
}

.room-color-indigo {
  border-color: #6610f2;
  background: rgba(102, 16, 242, 0.05);
}

.room-color-indigo .room-header {
  border-bottom-color: rgba(102, 16, 242, 0.2);
}
</style>