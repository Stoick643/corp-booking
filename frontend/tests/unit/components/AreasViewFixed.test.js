import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import AreasViewFixed from '../../../src/views/AreasViewFixed.vue'
import { apiService } from '../../../src/services/api.js'

// Mock the API service
vi.mock('../../../src/services/api.js', () => ({
  apiService: {
    fetchAreas: vi.fn()
  }
}))

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/areas/:areaId', component: { template: '<div>Rooms</div>' } }
  ]
})

describe('AreasViewFixed', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const mountComponent = async () => {
    wrapper = mount(AreasViewFixed, {
      global: {
        plugins: [router]
      }
    })
    await wrapper.vm.$nextTick()
    return wrapper
  }

  describe('Component Rendering', () => {
    it('renders the page header correctly', async () => {
      apiService.fetchAreas.mockResolvedValue([])
      
      await mountComponent()
      
      expect(wrapper.find('h1').text()).toBe('Office Areas')
      expect(wrapper.find('p.text-muted').text()).toContain('Select an office area')
    })

    it('shows loading spinner when loading', async () => {
      apiService.fetchAreas.mockImplementation(() => new Promise(() => {})) // Never resolves
      
      await mountComponent()
      
      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
      expect(wrapper.find('.spinner-border').exists()).toBe(true)
    })

    it('shows error message when API fails', async () => {
      apiService.fetchAreas.mockRejectedValue(new Error('API Error'))
      
      await mountComponent()
      
      // Wait for error to be processed
      await new Promise(resolve => setTimeout(resolve, 50))
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.alert-danger').exists()).toBe(true)
      expect(wrapper.find('.alert-danger').text()).toContain('Failed to load office areas')
    })
  })

  describe('Areas Data Display', () => {
    const mockAreas = [
      { id: 1, name: 'North Wing', room_count: 5, desk_count: 15 },
      { id: 2, name: 'South Wing', room_count: 4, desk_count: 12 },
      { id: 3, name: 'East Wing', room_count: 6, desk_count: 18 }
    ]

    it('displays areas correctly when data is loaded', async () => {
      apiService.fetchAreas.mockResolvedValue(mockAreas)
      
      await mountComponent()
      
      // Wait for data to load
      await new Promise(resolve => setTimeout(resolve, 50))
      await wrapper.vm.$nextTick()
      
      const areaCards = wrapper.findAll('.area-card')
      expect(areaCards).toHaveLength(3)
      
      // Check first area
      const firstCard = areaCards[0]
      expect(firstCard.find('.card-title').text()).toContain('North Wing')
      expect(firstCard.find('.stat-number').text()).toBe('5')
    })

    it('calculates summary statistics correctly', async () => {
      apiService.fetchAreas.mockResolvedValue(mockAreas)
      
      await mountComponent()
      
      // Wait for data to load
      await new Promise(resolve => setTimeout(resolve, 50))
      await wrapper.vm.$nextTick()
      
      const summaryStats = wrapper.findAll('.card.bg-light h4')
      expect(summaryStats[0].text()).toBe('3') // Total areas
      expect(summaryStats[1].text()).toBe('15') // Total rooms (5+4+6)
      expect(summaryStats[2].text()).toBe('45') // Total desks (15+12+18)
    })
  })

  describe('Navigation', () => {
    it('navigates to rooms when area is clicked', async () => {
      const mockAreas = [
        { id: 1, name: 'North Wing', room_count: 5, desk_count: 15 }
      ]
      apiService.fetchAreas.mockResolvedValue(mockAreas)
      
      const pushSpy = vi.spyOn(router, 'push')
      
      await mountComponent()
      
      // Wait for data to load
      await new Promise(resolve => setTimeout(resolve, 50))
      await wrapper.vm.$nextTick()
      
      const areaCard = wrapper.find('.area-card')
      await areaCard.trigger('click')
      
      expect(pushSpy).toHaveBeenCalledWith('/areas/1')
    })
  })

  describe('Error Handling', () => {
    it('can retry after error', async () => {
      apiService.fetchAreas
        .mockRejectedValueOnce(new Error('API Error'))
        .mockResolvedValueOnce([{ id: 1, name: 'Test Area', room_count: 1, desk_count: 3 }])
      
      await mountComponent()
      
      // Wait for initial error
      await new Promise(resolve => setTimeout(resolve, 50))
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.alert-danger').exists()).toBe(true)
      
      // Click retry button
      const retryButton = wrapper.find('.btn-outline-danger')
      await retryButton.trigger('click')
      
      // Wait for retry to complete
      await new Promise(resolve => setTimeout(resolve, 50))
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.alert-danger').exists()).toBe(false)
      expect(wrapper.findAll('.area-card')).toHaveLength(1)
    })
  })

  describe('Component Lifecycle', () => {
    it('calls loadAreas on mount', async () => {
      apiService.fetchAreas.mockResolvedValue([])
      
      await mountComponent()
      
      expect(apiService.fetchAreas).toHaveBeenCalledOnce()
    })

    it('does not call API multiple times if already loading', async () => {
      let resolvePromise
      apiService.fetchAreas.mockImplementation(() => new Promise(resolve => {
        resolvePromise = resolve
      }))
      
      await mountComponent()
      
      // Try to trigger loadAreas again
      await wrapper.vm.loadAreas()
      
      expect(apiService.fetchAreas).toHaveBeenCalledOnce()
      
      // Resolve the promise
      resolvePromise([])
    })
  })
})