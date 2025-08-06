<template>
  <form @submit.prevent="submitForm" novalidate>
    <!-- User Information -->
    <div class="mb-4">
      <h6 class="text-muted mb-3">
        <i class="bi bi-person me-2"></i>
        User Information
      </h6>
      <div class="row">
        <div class="col-md-6">
          <div class="mb-3">
            <label for="userName" class="form-label">Name *</label>
            <input
              type="text"
              class="form-control"
              id="userName"
              v-model="form.userName"
              :class="{ 'is-invalid': errors.userName }"
              placeholder="Enter your full name"
              required
            >
            <div v-if="errors.userName" class="invalid-feedback">
              {{ errors.userName }}
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="mb-3">
            <label for="userEmail" class="form-label">Email *</label>
            <input
              type="email"
              class="form-control"
              id="userEmail"
              v-model="form.userEmail"
              :class="{ 'is-invalid': errors.userEmail }"
              placeholder="your.email@company.com"
              required
            >
            <div v-if="errors.userEmail" class="invalid-feedback">
              {{ errors.userEmail }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Details -->
    <div class="mb-4">
      <h6 class="text-muted mb-3">
        <i class="bi bi-calendar me-2"></i>
        Booking Details
      </h6>
      
      <div class="row">
        <div class="col-md-6">
          <div class="mb-3">
            <label for="bookingDate" class="form-label">Date *</label>
            <input
              type="date"
              class="form-control"
              id="bookingDate"
              v-model="form.date"
              :class="{ 'is-invalid': errors.date }"
              :min="minDate"
              :max="maxDate"
              required
            >
            <div v-if="errors.date" class="invalid-feedback">
              {{ errors.date }}
            </div>
            <div class="form-text">
              Select a date between today and {{ formatDate(maxDate) }}
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="mb-3">
            <label for="bookingTime" class="form-label">Preferred Time</label>
            <select
              class="form-select"
              id="bookingTime"
              v-model="form.preferredTime"
            >
              <option value="">Any time</option>
              <option value="morning">Morning (8:00 - 12:00)</option>
              <option value="afternoon">Afternoon (12:00 - 17:00)</option>
              <option value="evening">Evening (17:00 - 20:00)</option>
            </select>
            <div class="form-text">
              Optional - helps with desk allocation
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Information -->
    <div class="mb-4">
      <h6 class="text-muted mb-3">
        <i class="bi bi-chat-text me-2"></i>
        Additional Information
      </h6>
      
      <div class="mb-3">
        <label for="notes" class="form-label">Notes (Optional)</label>
        <textarea
          class="form-control"
          id="notes"
          rows="3"
          v-model="form.notes"
          :class="{ 'is-invalid': errors.notes }"
          placeholder="Any special requirements or notes for this booking..."
          maxlength="500"
        ></textarea>
        <div v-if="errors.notes" class="invalid-feedback">
          {{ errors.notes }}
        </div>
        <div class="form-text">
          {{ form.notes.length }}/500 characters
        </div>
      </div>
      
      <div class="mb-3">
        <div class="form-check">
          <input
            class="form-check-input"
            type="checkbox"
            id="acceptTerms"
            v-model="form.acceptTerms"
            :class="{ 'is-invalid': errors.acceptTerms }"
          >
          <label class="form-check-label" for="acceptTerms">
            I accept the <a href="#" class="text-decoration-none">booking terms and conditions</a> *
          </label>
          <div v-if="errors.acceptTerms" class="invalid-feedback">
            {{ errors.acceptTerms }}
          </div>
        </div>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="d-flex gap-3">
      <button
        type="submit"
        class="btn btn-success"
        :disabled="isSubmitting"
      >
        <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-calendar-plus me-2"></i>
        {{ isSubmitting ? 'Creating Reservation...' : 'Book Desk' }}
      </button>
      
      <button
        type="button"
        class="btn btn-outline-secondary"
        @click="resetForm"
        :disabled="isSubmitting"
      >
        <i class="bi bi-arrow-clockwise me-2"></i>
        Reset Form
      </button>
      
      <button
        type="button"
        class="btn btn-outline-danger"
        @click="$emit('cancel')"
        :disabled="isSubmitting"
      >
        <i class="bi bi-x-circle me-2"></i>
        Cancel
      </button>
    </div>
  </form>
</template>

<script>
import { reactive, computed, onMounted } from 'vue'

export default {
  name: 'BookingForm',
  props: {
    desk: {
      type: Object,
      default: () => ({})
    },
    isSubmitting: {
      type: Boolean,
      default: false
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    // Form data
    const form = reactive({
      userName: '',
      userEmail: '',
      date: '',
      preferredTime: '',
      notes: '',
      acceptTerms: false
    })

    // Form errors
    const errors = reactive({})

    // Date constraints
    const today = new Date()
    const minDate = computed(() => {
      return today.toISOString().split('T')[0]
    })

    const maxDate = computed(() => {
      const maxDate = new Date()
      maxDate.setDate(today.getDate() + 30)
      return maxDate.toISOString().split('T')[0]
    })

    // Form validation
    const validateForm = () => {
      // Clear existing errors
      Object.keys(errors).forEach(key => delete errors[key])

      let isValid = true

      // Validate required fields
      if (!form.userName.trim()) {
        errors.userName = 'Name is required'
        isValid = false
      } else if (form.userName.trim().length < 2) {
        errors.userName = 'Name must be at least 2 characters'
        isValid = false
      }

      if (!form.userEmail.trim()) {
        errors.userEmail = 'Email is required'
        isValid = false
      } else if (!isValidEmail(form.userEmail)) {
        errors.userEmail = 'Please enter a valid email address'
        isValid = false
      }

      if (!form.date) {
        errors.date = 'Date is required'
        isValid = false
      } else if (!isValidDate(form.date)) {
        errors.date = 'Please select a valid future date'
        isValid = false
      } else if (isWeekend(form.date)) {
        errors.date = 'Bookings are not available on weekends'
        isValid = false
      }

      if (form.notes.length > 500) {
        errors.notes = 'Notes cannot exceed 500 characters'
        isValid = false
      }

      if (!form.acceptTerms) {
        errors.acceptTerms = 'You must accept the terms and conditions'
        isValid = false
      }

      return isValid
    }

    // Validation helpers
    const isValidEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    }

    const isValidDate = (dateString) => {
      const selectedDate = new Date(dateString)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      return selectedDate >= today
    }

    const isWeekend = (dateString) => {
      const date = new Date(dateString)
      const day = date.getDay()
      return day === 0 || day === 6 // Sunday = 0, Saturday = 6
    }

    // Form submission
    const submitForm = () => {
      if (!validateForm()) {
        return
      }

      const bookingData = {
        user: {
          name: form.userName.trim(),
          email: form.userEmail.trim()
        },
        date: form.date,
        preferredTime: form.preferredTime,
        notes: form.notes.trim(),
        deskId: props.desk?.id
      }

      emit('submit', bookingData)
    }

    // Form reset
    const resetForm = () => {
      form.userName = ''
      form.userEmail = ''
      form.date = ''
      form.preferredTime = ''
      form.notes = ''
      form.acceptTerms = false
      
      // Clear errors
      Object.keys(errors).forEach(key => delete errors[key])
    }

    // Utility functions
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    // Initialize form with some defaults
    onMounted(() => {
      // Set default date to tomorrow if it's not weekend
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      
      if (!isWeekend(tomorrow.toISOString().split('T')[0])) {
        form.date = tomorrow.toISOString().split('T')[0]
      } else {
        // If tomorrow is weekend, set to next Monday
        const nextMonday = new Date()
        nextMonday.setDate(tomorrow.getDate() + (8 - tomorrow.getDay()) % 7)
        form.date = nextMonday.toISOString().split('T')[0]
      }

      // Pre-fill demo user data
      form.userName = 'Demo User'
      form.userEmail = 'demo.user@company.com'
    })

    return {
      form,
      errors,
      minDate,
      maxDate,
      submitForm,
      resetForm,
      formatDate
    }
  }
}
</script>

<style scoped>
.form-control:focus,
.form-select:focus,
.form-check-input:focus {
  border-color: var(--bs-success);
  box-shadow: 0 0 0 0.2rem rgba(25, 135, 84, 0.25);
}

.btn-success {
  min-width: 150px;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.form-text {
  font-size: 0.8rem;
}

.form-check-label a {
  color: var(--bs-primary);
}

.form-check-label a:hover {
  color: var(--bs-primary);
  text-decoration: underline !important;
}

h6 {
  border-bottom: 1px solid rgba(0,0,0,0.1);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem !important;
}
</style>