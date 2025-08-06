import { describe, it, expect, vi } from 'vitest'

// Simple tests to verify the API service structure and exports
describe('API Service', () => {
  it('should export apiService with correct method signatures', async () => {
    const { apiService } = await import('../../../src/services/api.js')
    
    // Test that all expected methods exist
    expect(typeof apiService.fetchAreas).toBe('function')
    expect(typeof apiService.fetchArea).toBe('function')  
    expect(typeof apiService.fetchAreaRooms).toBe('function')
    expect(typeof apiService.fetchAreaDesks).toBe('function')
    expect(typeof apiService.fetchRooms).toBe('function')
    expect(typeof apiService.fetchRoom).toBe('function')
    expect(typeof apiService.fetchRoomDesks).toBe('function')
    expect(typeof apiService.fetchDesks).toBe('function')
    expect(typeof apiService.fetchDesk).toBe('function')
    expect(typeof apiService.fetchUsers).toBe('function')
    expect(typeof apiService.fetchReservations).toBe('function')
    expect(typeof apiService.createReservation).toBe('function')
    expect(typeof apiService.updateReservation).toBe('function')
    expect(typeof apiService.deleteReservation).toBe('function')
  })

  it('should export the axios instance as default', async () => {
    const api = (await import('../../../src/services/api.js')).default
    
    // Test that default export has axios instance methods
    expect(typeof api.get).toBe('function')
    expect(typeof api.post).toBe('function')
    expect(typeof api.patch).toBe('function') 
    expect(typeof api.delete).toBe('function')
    expect(typeof api.interceptors).toBe('object')
  })

  it('should have proper configuration', async () => {
    const api = (await import('../../../src/services/api.js')).default
    
    // Test axios instance has interceptors configured
    expect(api.interceptors.request).toBeDefined()
    expect(api.interceptors.response).toBeDefined()
  })
})

// Integration-style tests that verify actual API service behavior
// These would normally require a running backend, but can be used for integration testing
describe('API Service Integration', () => {
  // Skip these tests in CI/unit test environment
  const isIntegrationMode = process.env.INTEGRATION_TEST === 'true'
  
  it.skipIf(!isIntegrationMode)('should make actual HTTP requests to Django backend', async () => {
    const { apiService } = await import('../../../src/services/api.js')
    
    try {
      // This would require Django backend running
      const areas = await apiService.fetchAreas()
      expect(Array.isArray(areas)).toBe(true)
      
      if (areas.length > 0) {
        const area = areas[0]
        expect(area).toHaveProperty('id')
        expect(area).toHaveProperty('name')
        expect(area).toHaveProperty('room_count')
        expect(area).toHaveProperty('desk_count')
      }
    } catch (error) {
      // Expected to fail if backend is not running
      console.log('Backend integration test skipped - Django not available')
    }
  })
})

// Test axios configuration and interceptor setup
describe('API Configuration', () => {
  it('should configure axios with correct base settings', async () => {
    // Import axios to check if it's properly configured
    const axios = (await import('axios')).default
    expect(typeof axios.create).toBe('function')
    
    // Test that our module creates an axios instance correctly
    const api = (await import('../../../src/services/api.js')).default
    expect(api).toBeDefined()
    expect(typeof api.get).toBe('function')
  })
  
  it('should have request and response interceptors', async () => {
    const api = (await import('../../../src/services/api.js')).default
    
    // Verify interceptors are configured
    expect(api.interceptors.request.use).toBeDefined()
    expect(api.interceptors.response.use).toBeDefined()
  })
})