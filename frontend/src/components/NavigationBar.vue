<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
    <div class="container-fluid">
      <!-- Brand -->
      <router-link to="/" class="navbar-brand">
        <i class="bi bi-building me-2"></i>
        Corporate Workspace
      </router-link>

      <!-- Breadcrumb Navigation -->
      <nav aria-label="breadcrumb" class="d-none d-md-block">
        <ol class="breadcrumb bg-transparent mb-0">
          <li 
            v-for="(crumb, index) in breadcrumbs" 
            :key="crumb.path"
            class="breadcrumb-item"
            :class="{ 'active': index === breadcrumbs.length - 1 }"
          >
            <router-link 
              v-if="index < breadcrumbs.length - 1"
              :to="crumb.path"
              class="text-light text-decoration-none"
            >
              {{ crumb.name }}
            </router-link>
            <span v-else class="text-light opacity-75">
              {{ crumb.name }}
            </span>
          </li>
        </ol>
      </nav>

      <!-- Mobile Menu Toggle (placeholder for future features) -->
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navigation Items (placeholder for future features like user menu) -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <span class="navbar-text">
              <i class="bi bi-person-circle me-1"></i>
              Guest User
            </span>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { store } from '../stores/booking.js'

export default {
  name: 'NavigationBar',
  setup() {
    const breadcrumbs = computed(() => store.getBreadcrumbs())

    return {
      breadcrumbs
    }
  }
}
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.breadcrumb {
  margin: 0;
}

.breadcrumb-item a:hover {
  text-decoration: underline !important;
}

.navbar-brand {
  font-weight: 600;
  font-size: 1.25rem;
}

.navbar-text {
  color: rgba(255, 255, 255, 0.75) !important;
}
</style>