<template>
  <div class="areas-view">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="h3 mb-2">
          <i class="bi bi-building me-2"></i>
          Workspace Booking
        </h1>
        <p class="text-muted">
          Select an office area to view available desks for booking.
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
      <button type="button" class="btn btn-sm btn-outline-danger ms-3" @click="loadAreas">
        <i class="bi bi-arrow-clockwise me-1"></i>
        Retry
      </button>
    </div>

    <!-- Areas Grid -->
    <div v-else class="row g-4">
      <div 
        v-for="area in areas" 
        :key="area.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <div class="card h-100 area-card" @click="navigateToAreaDesks(area.id)">
          <!-- Card Header with Area Name -->
          <div class="card-header bg-primary text-white">
            <h5 class="card-title mb-0">
              <i class="bi bi-geo-alt-fill me-2"></i>
              {{ area.name }}
            </h5>
          </div>

          <!-- Card Body with Statistics -->
          <div class="card-body d-flex flex-column">
            <div class="row text-center mb-3">
              <div class="col-6">
                <div class="stat-item">
                  <h4 class="stat-number text-success mb-1">{{ area.room_count }}</h4>
                  <small class="stat-label text-muted">Rooms</small>
                </div>
              </div>
              <div class="col-6">
                <div class="stat-item">
                  <h4 class="stat-number text-info mb-1">{{ area.desk_count }}</h4>
                  <small class="stat-label text-muted">Desks</small>
                </div>
              </div>
            </div>

            <div class="mt-auto">
              <div class="d-grid">
                <button class="btn btn-outline-primary">
                  <i class="bi bi-arrow-right me-1"></i>
                  View Rooms
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div v-if="areas.length > 0" class="row mt-5">
      <div class="col-12">
        <div class="card bg-light">
          <div class="card-body">
            <div class="row text-center">
              <div class="col-4">
                <h4 class="text-primary">{{ areas.length }}</h4>
                <small class="text-muted">Office Areas</small>
              </div>
              <div class="col-4">
                <h4 class="text-success">{{ totalRooms }}</h4>
                <small class="text-muted">Total Rooms</small>
              </div>
              <div class="col-4">
                <h4 class="text-info">{{ totalDesks }}</h4>
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
import { useRouter } from 'vue-router'
import { apiService } from '../services/api.js'

export default {
  name: 'AreasViewFixed',
  setup() {
    const router = useRouter()
    const areas = ref([])
    const isLoading = ref(false)
    const error = ref(null)

    console.log('AreasViewFixed: Component setup() called')

    // Computed properties for summary stats
    const totalRooms = computed(() => 
      areas.value.reduce((sum, area) => sum + area.room_count, 0)
    )

    const totalDesks = computed(() => 
      areas.value.reduce((sum, area) => sum + area.desk_count, 0)
    )

    // Load areas from API (NO STORE DEPENDENCY)
    const loadAreas = async () => {
      if (isLoading.value) return

      try {
        console.log('AreasViewFixed: Starting to load areas...')
        isLoading.value = true
        error.value = null
        
        const data = await apiService.fetchAreas()
        console.log('AreasViewFixed: Loaded areas:', data.length)
        
        areas.value = data
      } catch (err) {
        console.error('AreasViewFixed: Failed to load areas:', err)
        error.value = 'Failed to load office areas. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    // Navigation handler - direct to area desks (NO STORE DEPENDENCY)
    const navigateToAreaDesks = (areaId) => {
      console.log('AreasViewFixed: Navigating to area desks:', areaId)
      router.push(`/areas/${areaId}/desks`)
    }

    // Initialize component
    onMounted(() => {
      console.log('AreasViewFixed: Component mounted')
      loadAreas()
    })

    return {
      areas,
      isLoading,
      error,
      totalRooms,
      totalDesks,
      loadAreas,
      navigateToAreaDesks
    }
  }
}
</script>

<style scoped>
.areas-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.area-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.area-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.stat-item {
  padding: 0.5rem;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1;
}

.stat-label {
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}
</style>