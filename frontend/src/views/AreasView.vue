<template>
  <div class="areas-view">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="h3 mb-2">
          <i class="bi bi-building me-2"></i>
          Office Areas
        </h1>
        <p class="text-muted">
          Select an office area to browse available rooms and desks for booking.
        </p>
      </div>
    </div>

    <!-- Areas Grid -->
    <div class="row g-4">
      <div 
        v-for="area in areas" 
        :key="area.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <AreaCard 
          :area="area"
          @navigate="navigateToRooms"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="areas.length === 0 && !store.isLoading" class="row">
      <div class="col-12 text-center py-5">
        <i class="bi bi-building-slash display-1 text-muted"></i>
        <h4 class="mt-3 text-muted">No Areas Available</h4>
        <p class="text-muted">No office areas are currently configured.</p>
      </div>
    </div>

    <!-- Summary Stats (when areas are loaded) -->
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AreaCard from '../components/AreaCard.vue'
import { apiService } from '../services/api.js'
import { store } from '../stores/booking.js'

export default {
  name: 'AreasView',
  components: {
    AreaCard
  },
  setup() {
    const router = useRouter()
    const areas = ref([])
    const isLoading = ref(false) // Local loading guard
    const abortController = ref(null) // For cleanup

    console.log('AreasView: Component setup() called')
    console.log('AreasView: Current route:', router.currentRoute.value.path)

    // Watch for route changes
    watch(() => router.currentRoute.value.path, (newPath, oldPath) => {
      console.log('AreasView: Route changed from', oldPath, 'to', newPath)
    })

    // Computed properties for summary stats
    const totalRooms = computed(() => 
      areas.value.reduce((sum, area) => sum + area.room_count, 0)
    )

    const totalDesks = computed(() => 
      areas.value.reduce((sum, area) => sum + area.desk_count, 0)
    )

    // Load areas from API with guard against multiple calls
    const loadAreas = async () => {
      // Prevent multiple simultaneous calls
      if (isLoading.value) {
        console.log('AreasView: loadAreas already in progress, skipping...')
        return
      }

      // Cancel any existing request
      if (abortController.value) {
        abortController.value.abort()
      }

      try {
        console.log('AreasView: Starting to load areas...')
        isLoading.value = true
        store.setLoading(true)
        store.clearError()
        
        // Create new abort controller for this request
        abortController.value = new AbortController()
        
        console.log('AreasView: Making API call to fetch areas...')
        const data = await apiService.fetchAreas()
        console.log('AreasView: API call successful, received data:', data)
        
        // Check if component is still mounted before updating state
        if (abortController.value && !abortController.value.signal.aborted) {
          areas.value = data
          store.setAreas(data)
          console.log('AreasView: Loaded areas:', data.length)
        } else {
          console.log('AreasView: Component was unmounted, not updating state')
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('AreasView: API call was aborted')
          return
        }
        
        console.error('AreasView: Failed to load areas:', error)
        console.error('AreasView: Error details:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        })
        store.setError(`Failed to load office areas: ${error.message}`)
      } finally {
        console.log('AreasView: Finished loading areas, setting loading to false')
        isLoading.value = false
        store.setLoading(false)
        abortController.value = null
      }
    }

    // Navigation handler
    const navigateToRooms = (areaId) => {
      const area = areas.value.find(a => a.id === areaId)
      if (area) {
        store.setCurrentArea(area)
        router.push(`/areas/${areaId}`)
      }
    }

    // Initialize component
    onMounted(() => {
      console.log('AreasView: Component mounted, calling loadAreas()')
      loadAreas()
    })

    // Add unmount logging to track component lifecycle
    onUnmounted(() => {
      console.log('AreasView: Component unmounted, cleaning up...')
      if (abortController.value) {
        console.log('AreasView: Aborting pending API request')
        abortController.value.abort()
        abortController.value = null
      }
      isLoading.value = false
      store.setLoading(false)
    })

    return {
      areas,
      totalRooms,
      totalDesks,
      navigateToRooms,
      store
    }
  }
}
</script>

<style scoped>
.areas-view {
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  height: 100%;
}
</style>