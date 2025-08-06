<template>
  <div class="date-selector">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h6 class="mb-0">
          <i class="bi bi-calendar3 me-2"></i>
          Select Date
        </h6>
      </div>
      <div class="card-body p-3">
        <!-- Current Selection Display -->
        <div class="current-selection mb-3">
          <div class="selected-date-display p-2 bg-light rounded">
            <small class="text-muted d-block">Selected Date</small>
            <strong class="text-primary">{{ formatDateForDisplay(selectedDate) }}</strong>
          </div>
        </div>

        <!-- Quick Date Buttons -->
        <div class="quick-dates mb-3">
          <small class="text-muted d-block mb-2">Quick Select</small>
          <div class="d-grid gap-1">
            <button 
              v-for="quickDate in quickDates"
              :key="quickDate.value.toISOString()"
              class="btn btn-sm"
              :class="isSameDate(selectedDate, quickDate.value) ? 'btn-primary' : 'btn-outline-primary'"
              @click="selectDate(quickDate.value)"
            >
              {{ quickDate.label }}
            </button>
          </div>
        </div>

        <!-- Calendar Navigation -->
        <div class="calendar-nav d-flex justify-content-between align-items-center mb-2">
          <button 
            class="btn btn-sm btn-outline-secondary"
            @click="navigateMonth(-1)"
            :disabled="!canNavigateMonth(-1)"
          >
            <i class="bi bi-chevron-left"></i>
          </button>
          <strong class="month-year">{{ currentMonthDisplay }}</strong>
          <button 
            class="btn btn-sm btn-outline-secondary"
            @click="navigateMonth(1)"
            :disabled="!canNavigateMonth(1)"
          >
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>

        <!-- Calendar Grid -->
        <div class="calendar-grid">
          <!-- Day Headers -->
          <div class="day-headers">
            <div 
              v-for="day in dayHeaders"
              :key="day"
              class="day-header"
            >
              {{ day }}
            </div>
          </div>

          <!-- Calendar Days -->
          <div class="days-grid">
            <button
              v-for="day in calendarDays"
              :key="day.key"
              class="day-button"
              :class="getDayButtonClass(day)"
              :disabled="!day.selectable"
              @click="selectDate(day.date)"
            >
              {{ day.day }}
            </button>
          </div>
        </div>

        <!-- Date Info -->
        <div class="date-info mt-3 pt-2 border-top">
          <small class="text-muted">
            <i class="bi bi-info-circle me-1"></i>
            You can book up to 3 weeks in advance
          </small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'DateSelector',
  emits: ['date-selected'],
  setup(_, { emit }) {
    const selectedDate = ref(new Date())
    const currentMonth = ref(new Date())
    
    // Set selectedDate to today initially
    selectedDate.value.setHours(0, 0, 0, 0)
    currentMonth.value.setHours(0, 0, 0, 0)

    console.log('DateSelector: Component setup() called')

    // Day headers for calendar
    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    // Current month display
    const currentMonthDisplay = computed(() => {
      return currentMonth.value.toLocaleDateString('en-US', { 
        month: 'long', 
        year: 'numeric' 
      })
    })

    // Quick date options
    const quickDates = computed(() => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      
      const nextWeek = new Date(today)
      nextWeek.setDate(nextWeek.getDate() + 7)

      return [
        { label: 'Today', value: new Date(today) },
        { label: 'Tomorrow', value: tomorrow },
        { label: 'Next Week', value: nextWeek }
      ].filter(item => isDateSelectable(item.value))
    })

    // Calendar days for current month
    const calendarDays = computed(() => {
      const year = currentMonth.value.getFullYear()
      const month = currentMonth.value.getMonth()
      
      // First day of the month
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      
      // Start from Sunday of the week containing the first day
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())
      
      const days = []
      const current = new Date(startDate)
      
      // Generate 42 days (6 weeks) for complete calendar grid
      for (let i = 0; i < 42; i++) {
        const day = {
          date: new Date(current),
          day: current.getDate(),
          isCurrentMonth: current.getMonth() === month,
          selectable: isDateSelectable(current),
          key: current.getTime()
        }
        days.push(day)
        current.setDate(current.getDate() + 1)
      }
      
      return days
    })

    // Check if a date is selectable (within 3 weeks, not past)
    const isDateSelectable = (date) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const checkDate = new Date(date)
      checkDate.setHours(0, 0, 0, 0)
      
      // Must be today or future
      if (checkDate < today) return false
      
      // Must be within 3 weeks (21 days)
      const threeWeeksFromToday = new Date(today)
      threeWeeksFromToday.setDate(threeWeeksFromToday.getDate() + 21)
      
      return checkDate <= threeWeeksFromToday
    }

    // Check if two dates are the same day
    const isSameDate = (date1, date2) => {
      return date1.toDateString() === date2.toDateString()
    }

    // Format date for display
    const formatDateForDisplay = (date) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      if (isSameDate(date, today)) {
        return 'Today'
      }
      
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      
      if (isSameDate(date, tomorrow)) {
        return 'Tomorrow'
      }
      
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short', 
        day: 'numeric'
      })
    }

    // Select a date
    const selectDate = (date) => {
      if (!isDateSelectable(date)) return
      
      console.log('DateSelector: Date selected:', date)
      selectedDate.value = new Date(date)
      selectedDate.value.setHours(0, 0, 0, 0)
      
      emit('date-selected', new Date(selectedDate.value))
    }

    // Navigate calendar months
    const navigateMonth = (direction) => {
      console.log('DateSelector: Navigating month:', direction)
      const newMonth = new Date(currentMonth.value)
      newMonth.setMonth(newMonth.getMonth() + direction)
      currentMonth.value = newMonth
    }

    // Check if month navigation is allowed
    const canNavigateMonth = (direction) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const testMonth = new Date(currentMonth.value)
      testMonth.setMonth(testMonth.getMonth() + direction)
      
      if (direction < 0) {
        // Can't go before current month
        return testMonth.getMonth() >= today.getMonth() && testMonth.getFullYear() >= today.getFullYear()
      } else {
        // Can't go beyond 3 weeks limit
        const threeWeeksFromToday = new Date(today)
        threeWeeksFromToday.setDate(threeWeeksFromToday.getDate() + 21)
        
        return testMonth.getMonth() <= threeWeeksFromToday.getMonth() && testMonth.getFullYear() <= threeWeeksFromToday.getFullYear()
      }
    }

    // Get CSS classes for day buttons
    const getDayButtonClass = (day) => {
      const classes = []
      
      if (!day.isCurrentMonth) {
        classes.push('other-month')
      }
      
      if (isSameDate(day.date, selectedDate.value)) {
        classes.push('selected')
      }
      
      if (isSameDate(day.date, new Date())) {
        classes.push('today')
      }
      
      if (!day.selectable) {
        classes.push('disabled')
      }
      
      return classes
    }

    // Initialize component
    onMounted(() => {
      console.log('DateSelector: Component mounted, initial date:', selectedDate.value)
      // Emit initial selection
      emit('date-selected', new Date(selectedDate.value))
    })

    return {
      selectedDate,
      currentMonth,
      dayHeaders,
      currentMonthDisplay,
      quickDates,
      calendarDays,
      isDateSelectable,
      isSameDate,
      formatDateForDisplay,
      selectDate,
      navigateMonth,
      canNavigateMonth,
      getDayButtonClass
    }
  }
}
</script>

<style scoped>
.date-selector {
  width: 280px;
}

.selected-date-display {
  border: 1px solid #dee2e6;
}

.quick-dates .btn {
  text-align: left;
}

.calendar-nav {
  font-size: 0.9rem;
}

.calendar-grid {
  font-size: 0.85rem;
}

.day-headers {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 5px;
}

.day-header {
  text-align: center;
  padding: 5px;
  font-weight: 600;
  color: #6c757d;
  background-color: #f8f9fa;
  border-radius: 3px;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}

.day-button {
  aspect-ratio: 1;
  border: 1px solid #dee2e6;
  background: white;
  color: #212529;
  font-size: 0.8rem;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.2s ease;
}

.day-button:hover:not(:disabled) {
  background-color: #e9ecef;
  border-color: #adb5bd;
}

.day-button.selected {
  background-color: #0d6efd;
  color: white;
  border-color: #0d6efd;
}

.day-button.today {
  font-weight: bold;
  border-color: #0d6efd;
}

.day-button.today.selected {
  background-color: #0d6efd;
}

.day-button.other-month {
  color: #adb5bd;
}

.day-button.disabled {
  color: #adb5bd;
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.date-info {
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .date-selector {
    width: 100%;
  }
}
</style>