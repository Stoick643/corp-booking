<template>
  <div id="app">
    <!-- Navigation Bar -->
    <NavigationBar />
    
    <!-- Main Content -->
    <main class="container-fluid py-4">
      <!-- Global Error Alert -->
      <div v-if="store.error" class="alert alert-danger alert-dismissible" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        {{ store.error }}
        <button 
          type="button" 
          class="btn-close" 
          @click="store.clearError()"
          aria-label="Close"
        ></button>
      </div>

      <!-- Loading Spinner -->
      <div v-if="store.isLoading" class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Router View -->
      <router-view v-else />
    </main>
  </div>
</template>

<script>
import NavigationBar from './components/NavigationBar.vue'
import { store } from './stores/booking.js'

export default {
  name: 'App',
  components: {
    NavigationBar
  },
  setup() {
    return {
      store
    }
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  background-color: #f8f9fa;
}

main {
  padding-top: 80px; /* Account for fixed navbar */
}
</style>