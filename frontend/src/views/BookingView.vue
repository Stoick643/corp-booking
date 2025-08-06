<template>
  <div class="booking-view">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex align-items-center mb-2">
          <button 
            class="btn btn-outline-secondary me-3"
            @click="goBackToDesks"
          >
            <i class="bi bi-arrow-left me-1"></i>
            Back to Desks
          </button>
          <div>
            <h1 class="h3 mb-0">
              <i class="bi bi-calendar-plus me-2"></i>
              Book Desk {{ currentDeskIdentifier }}
            </h1>
          </div>
        </div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">{{ currentAreaName }}</li>
            <li class="breadcrumb-item">{{ currentRoomName }}</li>
            <li class="breadcrumb-item active">{{ currentDeskIdentifier }}</li>
          </ol>
        </nav>
      </div>
    </div>

    <div class="row">
      <!-- Booking Form -->
      <div class="col-12 col-lg-8">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi bi-clipboard-check me-2"></i>
              Reservation Details
            </h5>
          </div>
          <div class="card-body">
            <BookingForm 
              :desk="currentDesk"
              @submit="handleBookingSubmit"
              @cancel="goBackToDesks"
              :is-submitting="isSubmitting"
            />
          </div>
        </div>
      </div>

      <!-- Desk Information Sidebar -->
      <div class="col-12 col-lg-4">
        <!-- Desk Details -->
        <div class="card mb-4">
          <div class="card-header bg-success text-white">
            <h6 class="card-title mb-0">
              <i class="bi bi-info-circle me-1"></i>
              Desk Information
            </h6>
          </div>
          <div class="card-body">
            <div class="desk-info">
              <div class="info-item mb-3">
                <label class="fw-bold text-muted small">Desk ID</label>
                <div>{{ currentDeskIdentifier }}</div>
              </div>
              
              <div class="info-item mb-3">
                <label class="fw-bold text-muted small">Room</label>
                <div>{{ currentRoomName }}</div>
              </div>
              
              <div class="info-item mb-3">
                <label class="fw-bold text-muted small">Area</label>
                <div>{{ currentAreaName }}</div>
              </div>
              
              <div v-if="hasPosition" class="info-item mb-3">
                <label class="fw-bold text-muted small">Position</label>
                <div class="font-monospace">
                  X: {{ currentDesk?.pos_x }}, Y: {{ currentDesk?.pos_y }}
                </div>
              </div>
              
              <div class="info-item">
                <label class="fw-bold text-muted small">Status</label>
                <div>
                  <span class="badge bg-success">
                    <i class="bi bi-check-circle-fill me-1"></i>
                    Available
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Booking Guidelines -->
        <div class="card">
          <div class="card-header">
            <h6 class="card-title mb-0">
              <i class="bi bi-exclamation-circle me-1"></i>
              Booking Guidelines
            </h6>
          </div>
          <div class="card-body">
            <ul class="list-unstyled mb-0">
              <li class="mb-2">
                <i class="bi bi-calendar-check text-success me-2"></i>
                <small>Bookings can be made up to 30 days in advance</small>
              </li>
              <li class="mb-2">
                <i class="bi bi-clock text-info me-2"></i>
                <small>Please check in within 15 minutes of arrival</small>
              </li>
              <li class="mb-2">
                <i class="bi bi-arrow-clockwise text-warning me-2"></i>
                <small>Cancellations allowed up to 2 hours before</small>
              </li>
              <li class="mb-2">
                <i class="bi bi-shield-check text-primary me-2"></i>
                <small>Follow office health and safety protocols</small>
              </li>
              <li>
                <i class="bi bi-people text-secondary me-2"></i>
                <small>Respect shared workspace etiquette</small>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div 
      class="modal fade" 
      id="bookingSuccessModal" 
      tabindex="-1"
      ref="successModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title">
              <i class="bi bi-check-circle-fill me-2"></i>
              Booking Confirmed
            </h5>
            <button 
              type="button" 
              class="btn-close btn-close-white" 
              data-bs-dismiss="modal"
            ></button>
          </div>
          <div class="modal-body">
            <div class="text-center">
              <i class="bi bi-calendar-check-fill display-3 text-success mb-3"></i>
              <h5>Reservation Successful!</h5>
              <p class="text-muted">
                Your desk has been reserved. Please remember to check in 
                when you arrive.
              </p>
              <div class="booking-summary bg-light p-3 rounded">
                <div class="row text-center">
                  <div class="col-6">
                    <strong>Desk</strong><br>
                    <small class="text-muted">{{ currentDeskIdentifier }}</small>
                  </div>
                  <div class="col-6">
                    <strong>Date</strong><br>
                    <small class="text-muted">{{ formatDate(bookingConfirmation?.date) }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              data-bs-dismiss="modal"
              @click="goBackToDesks"
            >
              Back to Desks
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="goToAreas"
            >
              Browse More Areas
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BookingForm from '../components/BookingForm.vue'
import { apiService } from '../services/api.js'
import { store } from '../stores/booking.js'

export default {
  name: 'BookingView',
  components: {
    BookingForm
  },
  props: {
    deskId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    const isSubmitting = ref(false)
    const bookingConfirmation = ref(null)
    const successModal = ref(null)

    // Computed properties
    const currentDesk = computed(() => 
      store.currentDesk || store.getDeskById(props.deskId)
    )

    const currentDeskIdentifier = computed(() => 
      currentDesk.value?.identifier || `Desk ${props.deskId}`
    )

    const currentRoomName = computed(() => 
      store.currentRoom?.name || currentDesk.value?.room_name || 'Unknown Room'
    )

    const currentAreaName = computed(() => 
      store.currentArea?.name || currentDesk.value?.area_name || 'Unknown Area'
    )

    const hasPosition = computed(() => 
      currentDesk.value?.pos_x !== null && currentDesk.value?.pos_y !== null
    )

    // Load desk data if not in store
    const loadDeskIfNeeded = async () => {
      if (!currentDesk.value) {
        try {
          const desk = await apiService.fetchDesk(props.deskId)
          store.setCurrentDesk(desk)
        } catch (error) {
          console.error('Failed to load desk:', error)
          store.setError('Failed to load desk information.')
        }
      }
    }

    // Handle booking submission
    const handleBookingSubmit = async (bookingData) => {
      try {
        isSubmitting.value = true
        store.clearError()
        
        console.log('Submitting booking:', bookingData)
        
        const reservation = await apiService.createReservation({
          desk: parseInt(props.deskId),
          date: bookingData.date,
          notes: bookingData.notes || ''
        })
        
        bookingConfirmation.value = reservation
        console.log('Booking successful:', reservation)
        
        // Show success modal
        const modal = new bootstrap.Modal(successModal.value)
        modal.show()
        
      } catch (error) {
        console.error('Booking failed:', error)
        let errorMessage = 'Failed to create reservation. Please try again.'
        
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail
        } else if (error.response?.data?.non_field_errors) {
          errorMessage = error.response.data.non_field_errors[0]
        } else if (error.response?.status === 400) {
          errorMessage = 'Invalid booking data. Please check your input.'
        }
        
        store.setError(errorMessage)
      } finally {
        isSubmitting.value = false
      }
    }

    // Navigation handlers
    const goBackToDesks = () => {
      // Extract room and area IDs from current context or desk data
      const areaId = store.currentArea?.id || currentDesk.value?.room?.area
      const roomId = store.currentRoom?.id || currentDesk.value?.room
      
      if (areaId && roomId) {
        router.push(`/areas/${areaId}/rooms/${roomId}`)
      } else {
        router.push('/')
      }
    }

    const goToAreas = () => {
      store.setCurrentArea(null)
      store.setCurrentRoom(null)
      store.setCurrentDesk(null)
      router.push('/')
    }

    // Utility functions
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    // Initialize component
    onMounted(() => {
      loadDeskIfNeeded()
    })

    return {
      currentDesk,
      currentDeskIdentifier,
      currentRoomName,
      currentAreaName,
      hasPosition,
      isSubmitting,
      bookingConfirmation,
      successModal,
      handleBookingSubmit,
      goBackToDesks,
      goToAreas,
      formatDate
    }
  }
}
</script>

<style scoped>
.booking-view {
  max-width: 1200px;
  margin: 0 auto;
}

.desk-info .info-item {
  border-bottom: 1px solid rgba(0,0,0,0.1);
  padding-bottom: 0.75rem;
}

.desk-info .info-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.booking-summary {
  border: 1px solid rgba(0,0,0,0.125);
}

.list-unstyled li {
  display: flex;
  align-items: flex-start;
}

.breadcrumb {
  background: none;
  padding: 0;
  margin: 0;
}
</style>