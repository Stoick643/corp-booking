<template>
  <div class="simple-test">
    <h1>Simple Test View</h1>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <h2>Areas ({{ areas.length }})</h2>
      <ul>
        <li v-for="area in areas" :key="area.id">
          {{ area.name }} ({{ area.room_count }} rooms, {{ area.desk_count }} desks)
        </li>
      </ul>
    </div>
    <div v-if="error" class="alert alert-danger">
      Error: {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiService } from '../services/api.js'

export default {
  name: 'SimpleTest',
  setup() {
    const areas = ref([])
    const loading = ref(false)
    const error = ref(null)
    let componentId = Math.random().toString(36).substr(2, 9)

    console.log(`SimpleTest[${componentId}]: Component setup() called`)

    const loadAreas = async () => {
      try {
        console.log(`SimpleTest[${componentId}]: Starting to load areas...`)
        loading.value = true
        error.value = null
        
        const data = await apiService.fetchAreas()
        console.log(`SimpleTest[${componentId}]: Loaded ${data.length} areas`)
        areas.value = data
      } catch (err) {
        console.error(`SimpleTest[${componentId}]: Error:`, err)
        error.value = err.message
      } finally {
        loading.value = false
        console.log(`SimpleTest[${componentId}]: Finished loading`)
      }
    }

    onMounted(() => {
      console.log(`SimpleTest[${componentId}]: Component mounted`)
      loadAreas()
    })

    onUnmounted(() => {
      console.log(`SimpleTest[${componentId}]: Component unmounted`)
    })

    return {
      areas,
      loading,
      error
    }
  }
}
</script>

<style scoped>
.simple-test {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
}

.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>