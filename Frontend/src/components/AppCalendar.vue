<template>
  <div class="calendar-wrapper">
    <div class="calendar-header">
      <button @click="goToPreviousMonth" class="arrow-button">⟨</button>
      <h3 class="calendar-title">{{ monthNames[currentMonth - 1] }} {{ currentYear }}</h3>
      <button @click="goToNextMonth" class="arrow-button">⟩</button>
    </div>

    <div class="toggle-buttons">
      <button
        v-for="dep in dependents"
        :key="dep.id"
        @click="selectDependent(dep.id)"
        :class="{ active: selectedDependent === dep.id }"
      >
        {{ dep.name }}
      </button>
    </div>

    <div class="weekday-row">
      <div v-for="day in daysOfWeek" :key="day" class="weekday">{{ day }}</div>
    </div>

    <div class="calendar-grid">
      <div
        v-for="(day, index) in visibleCalendarData"
        :key="index"
        :class="['calendar-cell', {
          today: day.medicationData?.isToday,
          future: day.medicationData?.isFuture,
          past: day.medicationData?.isPast
        }]"
      >
        <div class="cell-label">{{ day.label }}</div>
        <div class="cell-data">
          <template v-if="day.medicationData">
            <span class="taken">✅ {{ day.medicationData.taken || 0 }}</span>
            <span class="missed">❌ {{ day.medicationData.missed || 0 }}</span>
            <span class="pending">🕒 {{ day.medicationData.pending || 0 }}</span>
          </template>
          <template v-else>
            <span class="future-placeholder">-</span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import medicationService from '@/services/calendar.js';
import apiService from '@/services/apiService.js';

const currentDate = new Date();
const currentMonth = ref(currentDate.getMonth() + 1);
const currentYear = ref(currentDate.getFullYear());
const selectedDependent = ref(null);
const calendarData = ref([]);
const dependents = ref([]);

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

// Add computed property for daysInMonth
const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 0).getDate();
});

// Add computed property for visible calendar cells
const visibleCalendarData = computed(() => {
  return calendarData.value.filter(
    day => day.label === '' || parseInt(day.label) <= daysInMonth.value
  );
});

async function loadDependents() {
  try {
    const response = await apiService.get('/sc/my-dependents');
    // API returns { dependents: [ { id, firstName, lastName, ... } ] }
    dependents.value = response.data.dependents.map(dep => ({
      id: dep.id,
      name: dep.firstName + ' ' + dep.lastName
    }));
    if (dependents.value.length > 0 && !selectedDependent.value) {
      selectedDependent.value = dependents.value[0].id;
    }
  } catch (error) {
    console.error('Failed to load dependents:', error);
  }
}

async function loadCalendarData() {
  try {
    if (!selectedDependent.value) return;
    calendarData.value = await medicationService.generateCalendarData(currentMonth.value, currentYear.value, selectedDependent.value);
  } catch (error) {
    console.error('Failed to load calendar data:', error);
  }
}

function goToPreviousMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12;
    currentYear.value--;
  } else {
    currentMonth.value--;
  }
  loadCalendarData();
}

function goToNextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1;
    currentYear.value++;
  } else {
    currentMonth.value++;
  }
  loadCalendarData();
}

function selectDependent(depId) {
  selectedDependent.value = depId;
  loadCalendarData();
}

onMounted(async () => {
  const role = sessionStorage.getItem('role');
  if (role === 'care_giver') {
    await loadDependents();
    await loadCalendarData();
  }
});
watch([currentMonth, currentYear, selectedDependent], loadCalendarData);
</script>

<style scoped>
.calendar-wrapper {
  padding: 1rem;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-family: 'Times New Roman', serif;
}

.calendar-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.arrow-button {
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #0d6efd;
  transition: transform 0.2s ease;
}

.arrow-button:hover {
  transform: scale(1.3);
}

.calendar-title {
  font-size: 1.5rem;
  color: #2c3e50;
}

.toggle-buttons {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.toggle-buttons button {
  padding: 0.4rem 1rem;
  border: 1px solid #0d6efd;
  background-color: #f4f4f4;
  border-radius: 8px;
  cursor: pointer;
}

.toggle-buttons .active {
  background-color: #0d6efd;
  color: white;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

.calendar-cell {
  background-color: #f4f4f4;
  border-radius: 10px;
  padding: 0.5rem;
  text-align: center;
  border: 1px solid #ddd;
  font-size: 0.95rem;
}

.calendar-cell.today {
  border: 2px solid #0d6efd;
  background-color: #e6f0ff;
}

.calendar-cell.future {
  opacity: 0.6;
}

.calendar-cell.past {
  background-color: #fefefe;
}

.cell-label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.cell-data {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.taken { color: green; }
.missed { color: red; }
.pending { color: orange; }
</style>
