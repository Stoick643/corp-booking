<template>
  <div 
    class="card h-100 area-card" 
    :class="{ 'border-primary': isSelected }"
    @click="handleClick"
    role="button"
    tabindex="0"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
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

      <!-- Additional Info -->
      <div class="mt-auto">
        <div class="d-flex justify-content-between align-items-center">
          <small class="text-muted">
            <i class="bi bi-clock me-1"></i>
            Updated {{ formatDate(area.updated_at) }}
          </small>
          <div class="area-status">
            <span class="badge bg-success">Active</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Card Footer with Action -->
    <div class="card-footer bg-transparent">
      <div class="d-grid">
        <button 
          class="btn btn-outline-primary"
          @click.stop="handleClick"
        >
          <i class="bi bi-arrow-right me-1"></i>
          View Rooms
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'AreaCard',
  props: {
    area: {
      type: Object,
      required: true
    },
    isSelected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['navigate'],
  setup(props, { emit }) {
    // Format date for display
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })
    }

    // Handle click events
    const handleClick = () => {
      emit('navigate', props.area.id)
    }

    return {
      formatDate,
      handleClick
    }
  }
}
</script>

<style scoped>
.area-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.area-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: var(--bs-primary);
}

.area-card:focus {
  outline: 2px solid var(--bs-primary);
  outline-offset: 2px;
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

.card-header {
  border-bottom: none;
}

.card-footer {
  border-top: 1px solid rgba(0,0,0,0.125);
}

.badge {
  font-size: 0.7rem;
}

.btn-outline-primary:hover {
  transform: none; /* Prevent double transform effect */
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .area-card {
    transition: none;
  }
  
  .area-card:hover {
    transform: none;
  }
}
</style>