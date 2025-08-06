<template>
  <div 
    class="card h-100 room-card"
    :class="cardClasses"
    @click="handleClick"
    role="button"
    tabindex="0"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Card Header -->
    <div class="card-header" :class="headerClasses">
      <div class="d-flex justify-content-between align-items-center">
        <h6 class="card-title mb-0 text-truncate">
          <i :class="roomIcon" class="me-2"></i>
          {{ room.name }}
        </h6>
        <span 
          class="badge"
          :class="statusBadgeClass"
        >
          {{ roomStatusText }}
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
            <h5 class="stat-number text-success mb-1">{{ availableDesks }}</h5>
            <small class="stat-label text-muted">Available</small>
          </div>
        </div>
      </div>

      <!-- Room Type Info -->
      <div class="room-info mb-3">
        <div class="d-flex align-items-center mb-2">
          <i class="bi bi-bookmark me-2 text-muted"></i>
          <small class="text-muted">{{ roomTypeText }}</small>
        </div>
        <div class="d-flex align-items-center">
          <i class="bi bi-building me-2 text-muted"></i>
          <small class="text-muted">{{ room.area_name }}</small>
        </div>
      </div>

      <!-- Occupancy Bar (if has desks) -->
      <div v-if="room.desk_count > 0" class="occupancy-section mb-3">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <small class="text-muted">Capacity</small>
          <small class="text-muted">{{ occupancyPercentage }}%</small>
        </div>
        <div class="progress" style="height: 6px;">
          <div 
            class="progress-bar"
            :class="occupancyBarClass"
            :style="{ width: occupancyPercentage + '%' }"
            role="progressbar"
          ></div>
        </div>
      </div>

      <!-- Action Button -->
      <div class="mt-auto">
        <div class="d-grid">
          <button 
            class="btn"
            :class="actionButtonClass"
            :disabled="!canNavigate"
            @click.stop="handleClick"
          >
            <i :class="actionIcon" class="me-1"></i>
            {{ actionText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'RoomCard',
  props: {
    room: {
      type: Object,
      required: true
    }
  },
  emits: ['navigate'],
  setup(props, { emit }) {
    // Computed properties for room status and appearance
    const hasDesks = computed(() => props.room.desk_count > 0)
    const isBookable = computed(() => props.room.is_bookable)
    const canNavigate = computed(() => hasDesks.value)
    
    // Estimate available desks (in real app, this would come from API)
    const availableDesks = computed(() => 
      Math.max(0, Math.floor(props.room.desk_count * 0.7))
    )

    const occupancyPercentage = computed(() => {
      if (!hasDesks.value) return 0
      return Math.round(((props.room.desk_count - availableDesks.value) / props.room.desk_count) * 100)
    })

    // Styling computed properties
    const cardClasses = computed(() => ({
      'border-success': canNavigate.value && availableDesks.value > 0,
      'border-warning': hasDesks.value && availableDesks.value === 0,
      'border-secondary': !hasDesks.value
    }))

    const headerClasses = computed(() => {
      if (!hasDesks.value) return 'bg-light text-dark'
      return availableDesks.value > 0 ? 'bg-success text-white' : 'bg-warning text-dark'
    })

    const statusBadgeClass = computed(() => {
      if (!hasDesks.value) return 'bg-secondary'
      if (isBookable.value) return 'bg-primary'
      return 'bg-info'
    })

    const occupancyBarClass = computed(() => {
      const percentage = occupancyPercentage.value
      if (percentage < 50) return 'bg-success'
      if (percentage < 80) return 'bg-warning'
      return 'bg-danger'
    })

    const actionButtonClass = computed(() => {
      if (!canNavigate.value) return 'btn-outline-secondary'
      return availableDesks.value > 0 ? 'btn-success' : 'btn-warning'
    })

    // Text computed properties
    const roomIcon = computed(() => {
      if (isBookable.value) return 'bi bi-calendar-check'
      return hasDesks.value ? 'bi bi-person-workspace' : 'bi bi-door-closed'
    })

    const roomTypeText = computed(() => {
      if (!hasDesks.value) return 'Meeting Room'
      if (props.room.desk_count === 1) return 'Private Office'
      if (props.room.desk_count <= 4) return 'Shared Office'
      return 'Open Office'
    })

    const roomStatusText = computed(() => {
      if (isBookable.value) return 'Bookable'
      return hasDesks.value ? 'Workspace' : 'Meeting'
    })

    const actionText = computed(() => {
      if (!canNavigate.value) return 'No Desks'
      return availableDesks.value > 0 ? 'View Desks' : 'Fully Occupied'
    })

    const actionIcon = computed(() => {
      if (!canNavigate.value) return 'bi bi-x-circle'
      return 'bi bi-arrow-right'
    })

    // Event handlers
    const handleClick = () => {
      if (canNavigate.value) {
        emit('navigate', props.room.id)
      }
    }

    return {
      hasDesks,
      isBookable,
      canNavigate,
      availableDesks,
      occupancyPercentage,
      cardClasses,
      headerClasses,
      statusBadgeClass,
      occupancyBarClass,
      actionButtonClass,
      roomIcon,
      roomTypeText,
      roomStatusText,
      actionText,
      actionIcon,
      handleClick
    }
  }
}
</script>

<style scoped>
.room-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.room-card:focus {
  outline: 2px solid var(--bs-primary);
  outline-offset: 2px;
}

.room-card.border-secondary {
  cursor: default;
}

.room-card.border-secondary:hover {
  transform: none;
  box-shadow: none;
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

.room-info {
  border-top: 1px solid rgba(0,0,0,0.1);
  border-bottom: 1px solid rgba(0,0,0,0.1);
  padding: 0.75rem 0;
}

.occupancy-section .progress {
  background-color: rgba(0,0,0,0.1);
}

.card-header {
  border-bottom: none;
}

.badge {
  font-size: 0.65rem;
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .room-card {
    transition: none;
  }
  
  .room-card:hover {
    transform: none;
  }
}
</style>