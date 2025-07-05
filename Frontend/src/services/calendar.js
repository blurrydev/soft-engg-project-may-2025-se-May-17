import apiService from './apiService'

const medicationService = {
  async getMedicationReport(month, year, userId) {
    try {
      const response = await apiService.api.post('/sc/status-report', {
        month,
        year,
        user_id: userId
      })
      return response.data
    } catch (error) {
      console.error('Error fetching medication report:', error)
      throw error
    }
  },

  async getAllMedicines() {
    try {
      const response = await apiService.api.get('/sc/medicines')
      return response.data
    } catch (error) {
      console.error('Error fetching medicines:', error)
      throw error
    }
  },

  async getUpcomingMedicines() {
    try {
      const response = await apiService.api.get('/sc/upcoming-medications')
      return response.data
    } catch (error) {
      console.error('Error fetching upcoming medicines:', error)
      throw error
    }
  },

  async sendReminder(userId, medicineId) {
    try {
      const response = await apiService.api.post('/sc/send-reminder', {
        user_id: userId,
        medicine_id: medicineId
      })
      return response.data
    } catch (error) {
      console.error('Error sending reminder:', error)
      throw error
    }
  },

  processCalendarData(statusData) {
    const processedData = {}
    if (!statusData || !Array.isArray(statusData)) return processedData

    statusData.forEach(dayData => {
      const date = new Date(dayData.date).getDate()
      let taken = 0, missed = 0, pending = 0
      const slots = ['breakfast_before', 'breakfast_after', 'lunch_before', 'lunch_after', 'dinner_before', 'dinner_after']

      slots.forEach(slot => {
        if (Object.prototype.hasOwnProperty.call(dayData, slot)) {
          if (dayData[slot] === true) taken++
          else if (dayData[slot] === false) missed++
          else if (dayData[slot] === null) pending++
        }
      })

      processedData[date] = {
        taken,
        missed,
        pending,
        date: dayData.date,
        details: dayData
      }
    })

    return processedData
  },

  async generateCalendarData(month, year, userId) {
    try {
      const reportData = await this.getMedicationReport(month, year, userId)
      const processedData = this.processCalendarData(reportData.daily_status || [])
      const data = []
      const today = new Date()
      const currentDay = today.getDate()
      const currentMonth = today.getMonth() + 1
      const currentYear = today.getFullYear()

      const firstDayOfMonth = new Date(year, month - 1, 1)
      const startDay = firstDayOfMonth.getDay() === 0 ? 6 : firstDayOfMonth.getDay() - 1 // Monday start
      const daysInMonth = new Date(year, month, 0).getDate()

      // Fill empty cells for alignment
      for (let i = 0; i < startDay; i++) {
        data.push({ label: '', date: '', medicationData: null })
      }

      for (let i = 1; i <= daysInMonth; i++) {
        const dayDate = new Date(year, month - 1, i)
        const isToday = (i === currentDay && month === currentMonth && year === currentYear)
        const isFutureDay = dayDate > today

        let medicationData = null

        if (processedData[i]) {
          medicationData = {
            taken: processedData[i].taken,
            missed: processedData[i].missed,
            pending: processedData[i].pending,
            isToday,
            isFuture: isFutureDay,
            isPast: !isToday && !isFutureDay,
            details: processedData[i].details
          }
        } else if (isFutureDay) {
          medicationData = {
            taken: 0,
            missed: 0,
            pending: 3,
            isFuture: true
          }
        } else {
          medicationData = {
            taken: 0,
            missed: 0,
            pending: 0,
            isPast: true
          }
        }

        data.push({
          date: i,
          label: i.toString(),
          medicationData
        })
      }

      return data
    } catch (error) {
      console.error('Error generating calendar data:', error)
      return this.generateFallbackData()
    }
  },

  generateFallbackData() {
    const data = []
    const today = new Date()
    const currentDay = today.getDate()
    const startDay = new Date(today.getFullYear(), today.getMonth(), 1).getDay()
    const offset = startDay === 0 ? 6 : startDay - 1

    for (let i = 0; i < offset; i++) {
      data.push({ label: '', date: '', medicationData: null })
    }

    for (let i = 1; i <= 30; i++) {
      const dayDate = new Date(today.getFullYear(), today.getMonth(), i)
      const isToday = (i === currentDay)
      const isFutureDay = dayDate > today

      let medicationData = null

      if (isFutureDay) {
        medicationData = { taken: 0, missed: 0, pending: 3, isFuture: true }
      } else if (isToday) {
        medicationData = { taken: 2, missed: 1, pending: 1, isToday: true }
      } else {
        medicationData = {
          taken: Math.floor(Math.random() * 4) + 1,
          missed: Math.floor(Math.random() * 2),
          pending: 0,
          isPast: true
        }
      }

      data.push({
        date: i,
        label: i.toString(),
        medicationData
      })
    }

    return data
  }
}

export default medicationService
