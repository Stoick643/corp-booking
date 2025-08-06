import { createRouter, createWebHistory } from 'vue-router'
import AreasView from '../views/AreasView.vue'
import AreasViewFixed from '../views/AreasViewFixed.vue'
import AreaWorkspaceView from '../views/AreaWorkspaceView.vue'
import RoomsView from '../views/RoomsView.vue'
import RoomsViewFixed from '../views/RoomsViewFixed.vue'
import DesksView from '../views/DesksView.vue'
import DesksViewFixed from '../views/DesksViewFixed.vue'
import SimpleTest from '../views/SimpleTest.vue'

const routes = [
  {
    path: '/',
    name: 'areas',
    component: AreasViewFixed,
    meta: { 
      title: 'Office Areas',
      breadcrumb: 'Areas'
    }
  },
  {
    path: '/broken',
    name: 'broken',
    component: AreasView,
    meta: { 
      title: 'Broken Areas View',
      breadcrumb: 'Broken'
    }
  },
  {
    path: '/test',
    name: 'test',
    component: SimpleTest,
    meta: { 
      title: 'Simple Test',
      breadcrumb: 'Test'
    }
  },
  {
    path: '/areas/:areaId/desks',
    name: 'area-desks',
    component: AreaWorkspaceView,
    props: true,
    meta: { 
      title: 'Area Desks',
      breadcrumb: 'Desks'
    }
  },
  {
    path: '/areas/:areaId',
    name: 'rooms',
    component: RoomsViewFixed,
    props: true,
    meta: { 
      title: 'Rooms',
      breadcrumb: 'Rooms'
    }
  },
  {
    path: '/areas/:areaId/rooms/:roomId',
    name: 'desks',
    component: DesksViewFixed,
    props: true,
    meta: { 
      title: 'Desks',
      breadcrumb: 'Desks'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guards
router.beforeEach((to, from, next) => {
  // Update document title
  document.title = `${to.meta.title || 'Booking'} - Corporate Workspace`
  next()
})

export default router