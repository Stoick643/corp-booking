import { reactive } from 'vue'

// Simple reactive store for booking application state
export const store = reactive({
  // Current navigation context
  currentArea: null,
  currentRoom: null,
  currentDesk: null,

  // Data caches
  areas: [],
  rooms: [],
  desks: [],
  reservations: [],

  // UI state
  isLoading: false,
  error: null,

  // Methods to update state
  setCurrentArea(area) {
    this.currentArea = area
    this.currentRoom = null
    this.currentDesk = null
  },

  setCurrentRoom(room) {
    this.currentRoom = room
    this.currentDesk = null
  },

  setCurrentDesk(desk) {
    this.currentDesk = desk
  },

  setAreas(areas) {
    this.areas = areas
  },

  setRooms(rooms) {
    this.rooms = rooms
  },

  setDesks(desks) {
    this.desks = desks
  },

  setReservations(reservations) {
    this.reservations = reservations
  },

  setLoading(loading) {
    console.log('Store: Setting loading to', loading)
    this.isLoading = loading
  },

  setError(error) {
    console.log('Store: Setting error to', error)
    this.error = error
    if (error) {
      console.error('Store Error:', error)
    }
  },

  clearError() {
    this.error = null
  },

  // Helper methods
  getAreaById(areaId) {
    return this.areas.find(area => area.id === parseInt(areaId))
  },

  getRoomById(roomId) {
    return this.rooms.find(room => room.id === parseInt(roomId))
  },

  getDeskById(deskId) {
    return this.desks.find(desk => desk.id === parseInt(deskId))
  },

  // Breadcrumb generation
  getBreadcrumbs() {
    const breadcrumbs = [{ name: 'Areas', path: '/' }]
    
    if (this.currentArea) {
      breadcrumbs.push({
        name: this.currentArea.name,
        path: `/areas/${this.currentArea.id}`
      })
    }

    if (this.currentRoom) {
      breadcrumbs.push({
        name: this.currentRoom.name,
        path: `/areas/${this.currentArea.id}/rooms/${this.currentRoom.id}`
      })
    }

    if (this.currentDesk) {
      breadcrumbs.push({
        name: `Desk ${this.currentDesk.identifier}`,
        path: `/desks/${this.currentDesk.id}/book`
      })
    }

    return breadcrumbs
  }
})