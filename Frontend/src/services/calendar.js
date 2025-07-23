import apiService from './apiService'

const medicationService = {
  // Generate calendar data for a specific month/year
  async generateCalendarData(month, year) {
    try {
      const userId = sessionStorage.getItem('user_id');
      const role = sessionStorage.getItem('role');
      if (!userId) throw new Error('No user_id in sessionStorage');
      // Prepare request body
      const body = { month, year };
      if (role === 'care_giver' || role === 'caregiver') {
        body.user_id = parseInt(userId);
      }
      // POST to /sc/status-report
      const response = await apiService.api.post('/sc/status-report', body);
      const result = response.data;
      // result is an object: { 'YYYY-MM-DD': { taken, missed, details: {...} }, ... }
      // Build calendar days array
      const daysInMonth = new Date(year, month, 0).getDate();
      const firstDay = new Date(year, month - 1, 1);
      // Monday as first day of week
      const startingDayOfWeek = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
      const today = new Date();
      const medicationDays = [];
      // Add empty cells for days before the first day of the month
      for (let i = 0; i < startingDayOfWeek; i++) {
        medicationDays.push({
          label: '',
          date: null,
          medicationData: null
        });
      }
      // Fill in each day
      for (let day = 1; day <= daysInMonth; day++) {
        const currentDate = new Date(year, month - 1, day);
        const dateStr = currentDate.toISOString().split('T')[0];
        const isToday = currentDate.toDateString() === today.toDateString();
        const isFuture = currentDate > today;
        const isPast = currentDate < today;
        let taken = 0, missed = 0, pending = 0, completionRate = 0;
        if (result[dateStr]) {
          taken = result[dateStr].taken || 0;
          missed = result[dateStr].missed || 0;
          // Pending: count slots that are neither taken nor missed (null)
          const details = result[dateStr].details || {};
          pending = Object.values(details).filter(v => v === null).length;
          completionRate = taken + missed > 0 ? (taken / (taken + missed)) * 100 : 0;
        } else if (isFuture) {
          pending = 1; // At least one pending for future days
        }
        medicationDays.push({
          label: day.toString(),
          date: dateStr,
          medicationData: {
            taken,
            missed,
            pending,
            isToday,
            isFuture,
            isPast,
            completionRate
          }
        });
      }
      return medicationDays;
    } catch (err) {
      // Fallback to mock data if API fails
      return await this.generateFallbackData();
    }
  },

  // Fallback data for when API fails
  async generateFallbackData() {
    const today = new Date();
    const fallbackDays = [];
    // Generate 42 days (6 weeks) of fallback data
    for (let i = 0; i < 42; i++) {
      if (i < 7) {
        fallbackDays.push({
          label: '',
          date: null,
          medicationData: null
        });
      } else {
        const day = i - 6;
        fallbackDays.push({
          label: day.toString(),
          date: `2025-01-${day.toString().padStart(2, '0')}`,
          medicationData: {
            taken: Math.floor(Math.random() * 3),
            missed: Math.floor(Math.random() * 2),
            pending: Math.floor(Math.random() * 2),
            isToday: day === today.getDate(),
            isFuture: day > today.getDate(),
            isPast: day < today.getDate()
          }
        });
      }
    }
    return fallbackDays;
  },

  // Get medication details for a specific day (mock)
  async getDayMedications(date) {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      date,
      medications: [
        { name: 'Vitamin D', time: '8:00 AM', status: 'taken', person: 'Mom' },
        { name: 'Blood Pressure Med', time: '12:00 PM', status: 'missed', person: 'Dad' },
        { name: 'Diabetes Med', time: '6:00 PM', status: 'pending', person: 'Uncle' },
      ]
    };
  },

  // ... keep all other existing methods (getMedicationReport, getAllMedicines, getUpcomingMedicines, sendReminder, processCalendarData, etc.) ...
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

  // The original generateCalendarData and generateFallbackData are now replaced by the above implementations
}

export default medicationService
