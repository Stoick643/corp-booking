<template>
  <div 
    class="card h-100 desk-card"
    :class="cardClasses"
    @click="handleClick"
    :role="isBookable ? 'button' : undefined"
    :tabindex="isBookable ? 0 : undefined"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Card Header with Status -->
    <div class="card-header py-2" :class="headerClasses">
      <div class="d-flex justify-content-between align-items-center">
        <small class="fw-bold mb-0">
          <i :class="statusIcon" class="me-1"></i>
          {{ desk.identifier }}
        </small>
        <span 
          class="badge badge-sm"
          :class="statusBadgeClass"
        >
          {{ statusText }}
        </span>
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body d-flex flex-column p-3">
      <!-- Desk Position (if available) -->
      <div v-if="hasPosition" class="position-info mb-2">
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
        <p class="small mb-0" :class="descriptionTextClass">
          {{ statusDescription }}
        </p>
      </div>

      <!-- Action Button -->
      <div class="mt-auto">
        <div class="d-grid">
          <button 
            class="btn btn-sm"
            :class="actionButtonClass"
            :disabled="!isBookable"
            @click.stop="handleClick"
          >
            <i :class="actionIcon" class="me-1"></i>
            {{ actionText }}
          </button>
        </div>
      </div>
    </div>

    <!-- Current Booking Info (placeholder for future enhancement) -->
    <div v-if="hasCurrentBooking" class="card-footer py-2 bg-light">
      <small class="text-muted">
        <i class="bi bi-person me-1"></i>
        Reserved by User
      </small>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'DeskCard',
  props: {
    desk: {
      type: Object,
      required: true
    }
  },
  emits: ['book'],
  setup(props, { emit }) {
    // Computed properties for desk status
    const isAvailable = computed(() => props.desk.status === 'available')
    const isPermanent = computed(() => props.desk.status === 'permanent')
    const isDisabled = computed(() => props.desk.status === 'disabled')
    const isBookable = computed(() => isAvailable.value)
    
    const hasPosition = computed(() => 
      props.desk.pos_x !== null && props.desk.pos_y !== null
    )

    const hasCurrentBooking = computed(() => 
      // Placeholder - in real app this would check for active reservations
      false
    )

    // Styling computed properties
    const cardClasses = computed(() => ({
      'desk-available': isAvailable.value,
      'desk-permanent': isPermanent.value, 
      'desk-disabled': isDisabled.value,
      'border-success': isAvailable.value,
      'border-warning': isPermanent.value,
      'border-danger': isDisabled.value,
      'opacity-75': isDisabled.value
    }))

    const headerClasses = computed(() => {
      if (isAvailable.value) return 'bg-success text-white'
      if (isPermanent.value) return 'bg-warning text-dark'
      if (isDisabled.value) return 'bg-danger text-white'
      return 'bg-secondary text-white'
    })

    const statusBadgeClass = computed(() => {
      if (isAvailable.value) return 'bg-light text-success'
      if (isPermanent.value) return 'bg-light text-warning'
      if (isDisabled.value) return 'bg-light text-danger'
      return 'bg-light text-secondary'
    })

    const descriptionTextClass = computed(() => {
      if (isAvailable.value) return 'text-success'
      if (isPermanent.value) return 'text-warning'
      if (isDisabled.value) return 'text-danger'
      return 'text-muted'
    })

    const actionButtonClass = computed(() => {
      if (isAvailable.value) return 'btn-success'
      if (isPermanent.value) return 'btn-outline-warning'
      if (isDisabled.value) return 'btn-outline-danger'
      return 'btn-outline-secondary'
    })

    // Text and icon computed properties
    const statusIcon = computed(() => {
      if (isAvailable.value) return 'bi bi-check-circle-fill'
      if (isPermanent.value) return 'bi bi-person-fill'
      if (isDisabled.value) return 'bi bi-x-circle-fill'
      return 'bi bi-question-circle'
    })

    const statusText = computed(() => {
      if (isAvailable.value) return 'Available'
      if (isPermanent.value) return 'Permanent'
      if (isDisabled.value) return 'Disabled'
      return 'Unknown'
    })

    const statusDescription = computed(() => {
      if (isAvailable.value) return 'This desk is available for booking.'
      if (isPermanent.value) return 'This desk has a permanent assignment.'
      if (isDisabled.value) return 'This desk is currently out of service.'
      return 'Status unknown.'
    })

    const actionText = computed(() => {
      if (isAvailable.value) return 'Book Desk'
      if (isPermanent.value) return 'Assigned'
      if (isDisabled.value) return 'Unavailable'
      return 'N/A'
    })

    const actionIcon = computed(() => {
      if (isAvailable.value) return 'bi bi-calendar-plus'
      if (isPermanent.value) return 'bi bi-person-check'
      if (isDisabled.value) return 'bi bi-exclamation-triangle'
      return 'bi bi-question'
    })

    // Event handlers
    const handleClick = () => {
      if (isBookable.value) {
        emit('book', props.desk.id)
      }
    }

    return {
      isAvailable,
      isPermanent,
      isDisabled,
      isBookable,
      hasPosition,
      hasCurrentBooking,
      cardClasses,
      headerClasses,
      statusBadgeClass,
      descriptionTextClass,
      actionButtonClass,
      statusIcon,
      statusText,
      statusDescription,
      actionText,
      actionIcon,
      handleClick
    }
  }
}
</script>

<style scoped>
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

.desk-card[role="button"]:focus {
  outline: 2px solid var(--bs-primary);
  outline-offset: 2px;
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

.badge-sm {
  font-size: 0.65rem;
  padding: 0.2rem 0.4rem;
}

.card-header {
  border-bottom: none;
}

.card-footer {
  border-top: 1px solid rgba(0,0,0,0.125);
  font-size: 0.8rem;
}

/* Status-specific styling */
.desk-disabled {
  pointer-events: none;
}

.desk-permanent .card-body {
  background-color: rgba(255, 193, 7, 0.05);
}

.desk-available .card-body {
  background-color: rgba(25, 135, 84, 0.05);
}

.desk-disabled .card-body {
  background-color: rgba(220, 53, 69, 0.05);
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .desk-card {
    transition: none;
  }
  
  .desk-card:hover {
    transform: none;
  }
}
</style>