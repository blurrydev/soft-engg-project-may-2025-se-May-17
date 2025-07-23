<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <div class="greeting"></div>
      <Navbar/>
    </header>

    <div class="header">
      <div class="date-section">
        <p class="today-label">Today</p>
        <p class="date">{{ formattedDate }}</p>
      </div>

      <div class="greeting-row">
        <button class="sos-button" @click="sendSOS" :disabled="sosLoading">
          {{ sosLoading ? '...' : 'SOS' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-state">
      <h2>Something went wrong</h2>
      <p>{{ error }}</p>
    </div>

    <div v-else class="main-content">
      <div class="left-panel">
        <p class="motivational-quote">"The best way to predict the future is to create it."</p>
        <h2 class="greeting">Goodmorning, {{ userName }}</h2>

        <h3 class="subheading">Upcoming Medication</h3>
        <div v-if="loading" class="upcoming-med-card placeholder">Loading...</div>
        <div v-else-if="nextMedication" class="upcoming-med-card">
          <span class="icon pill-icon">💊</span>
          <span class="med-name">{{ nextMedication.medicineName }}</span>
          <span class="med-dosage">{{ nextMedication.dosage }}</span>
          <span class="med-time"><span class="icon clock-icon">⏰</span>{{ nextMedication.time }}</span>
        </div>
        <div v-else class="upcoming-med-card empty">All medications for today are complete.</div>

        <h3 class="subheading today-meds-title">Today's medications</h3>
        <div v-if="loading" class="todays-meds-container placeholder">Loading schedule...</div>

        <div v-else class="todays-meds-container">
          <div class="meds-category">
            <div class="category-header"><span class="category-icon">☀️</span> Daytime Meds</div>
            <p v-if="daytimeMeds.length === 0" class="no-meds-text">No daytime medications.</p>
            <div v-else>
              <div v-for="med in daytimeMeds" :key="med.id" class="med-card day">
                <span class="icon pill-icon">💊</span>
                <span class="med-name">{{ med.medicine_title || med.medicineName }}</span>
                <span class="med-dosage">{{ med.dosage }}</span>
                <span class="med-time"><span class="icon clock-icon">⏰</span>{{ med.time || med.reminder_slot }}</span>
              </div>
            </div>
          </div>

          <div class="meds-category">
            <div class="category-header"><span class="category-icon">🌙</span> Nighttime Meds</div>
            <p v-if="nighttimeMeds.length === 0" class="no-meds-text">No nighttime medications.</p>
            <div v-else>
              <div v-for="med in nighttimeMeds" :key="med.id" class="med-card night">
                <span class="icon pill-icon">💊</span>
                <span class="med-name">{{ med.medicine_title || med.title || '-' }}</span>
                <span class="med-dosage">{{ med.dosage || '-' }}</span>
                <span class="med-time">{{ med.reminder_slot || med.time || '-' }}</span>

              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <MusicPlayer />
        <AppCalendar />
      </div>

      <div v-if="sosMessage" class="sos-alert" @click="sosMessage = ''">{{ sosMessage }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
// import { useRoute } from 'vue-router';
// import { getDependentDetails, getUpcomingMedication, getTodaysMedsForDependent } from '@/services/mockApi.js';
import Navbar from './Navbar.vue';
import AppCalendar from './AppCalendar.vue';
import apiService from '@/services/apiService'
import MusicPlayer from './MusicPlayer.vue';

// const route = useRoute();

const userName = ref('User');
const nextMedication = ref(null);
const daytimeMeds = ref([]);
const nighttimeMeds = ref([]);
const loading = ref(true);
const error = ref(null);
const sosLoading = ref(false);
const sosMessage = ref('');

const formattedDate = computed(() =>
  new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
);

async function getUpcomingMedication() {
  try {
    const res = await apiService.get('/sc/upcoming-medications');
    const data = res.data;

    if (res.status === 200) {
      return {
        success: true,
        meds: data.upcoming_medications || [],
        count: data.count || 0
      };
    } else {
      return {
        success: false,
        message: data.error || data.message || "Failed to get medications"
      };
    }
  } catch (err) {
    console.error("🔴 Error fetching upcoming medications:", err);
    return {
      success: false,
      message: err.message
    };
  }
}

async function fetchAllDataForSenior() {
  loading.value = true;
  error.value = null;
  try {
    const response = await getUpcomingMedication();
    if (!response.success) throw new Error(response.message);

    // Hardcode or fetch the user's name from another API if required
    userName.value = 'You';

    // Set upcoming medications for the day
    nextMedication.value = response.meds[0]
      ? {
          medicineName: response.meds[0].medicine_title,
          dosage: response.meds[0].dosage,
          time: response.meds[0].reminder_slot,
        }
      : null;

    // Day/Night split – example logic
    const daySlots = ['Breakfast', 'Lunch'];
    daytimeMeds.value = response.meds.filter(med =>
      daySlots.some(slot => med.reminder_slot && med.reminder_slot.includes(slot))
    );
    nighttimeMeds.value = response.meds.filter(
      med => med.reminder_slot && med.reminder_slot.includes('Dinner')
    );
  } catch (err) {
    error.value = 'Could not load dashboard data. Please try again later.';
  } finally {
    loading.value = false;
  }
}



async function sendSOS() {
  sosLoading.value = true
  sosMessage.value = ''

  try {
    const res = await apiService.post('/sc/send-sos') // Use Axios service

    if (res.status === 200 && res.data.status === 'SOS sent successfully') {
      // Optional: log sent alerts
      console.log('✅ SOS Alert Sent:', res.data.alerts_sent)

      sosMessage.value = '🚨 SOS Alert sent to your caregivers.'
    } else {
      sosMessage.value = res.data.message || '⚠️ Could not send SOS alert.'
    }
  } catch (err) {
    console.error('❌ Error sending SOS:', err)

    sosMessage.value =
      err.response?.data?.error || '❌ Failed to send SOS alert.'
  } finally {
    sosLoading.value = false
    setTimeout(() => {
      sosMessage.value = ''
    }, 4000)
  }
}

onMounted(() => {
  fetchAllDataForSenior();
});
</script>

<style scoped>
.dashboard-wrapper {
  background-color: #eef7f2;
  min-height: 100vh;
  font-family: "Georgia", serif;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.date-section {
  text-align: center;
}

.today-label {
  font-weight: bold;
  font-size: 1rem;
  color: #555;
  margin-bottom: 0.2rem;
}

.date {
  font-size: 1rem;
  color: #777;
}

.greeting {
  font-family: 'Georgia', serif;
  font-size: 2.2rem;
  margin: 0.5rem 0 1rem;
  color: #2c3e50;
  text-align: center;
}

.subheading {
  font-weight: bold;
  color: #333;
  font-size: 1.3rem;
  margin: 2rem 0 1rem;
}

.today-meds-title {
  margin-top: 2rem;
}

.upcoming-med-card {
  padding: 1.2rem 2rem;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  border: 2px solid #6498f8;
  background-color: #96ace9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  color: #3c3c3c;
}

.upcoming-med-card .med-name {
  flex-grow: 1;
}

.upcoming-med-card .med-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.upcoming-med-card .poke-button {
  background-color: #d9534f;
  color: white;
  font-weight: bold;
  padding: 0.4rem 1.2rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  cursor: pointer;
}

.icon {
  font-size: 1.3rem;
}

.main-content {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
}

.left-panel {
  flex: 2;
  min-width: 0;
}

.right-panel {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.todays-meds-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.meds-category {
  background-color: #ffffff;
  padding: 1.5rem 2rem;
  border-radius: 20px;
  border: 1px solid #dbe8d9;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.category-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.3rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1rem;
}

.category-icon {
  font-size: 1.5rem;
}

.no-meds-text {
  font-style: italic;
  color: #666;
}

.med-card {
  padding: 1rem 1.8rem;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 1.2rem;
  font-size: 1.05rem;
  font-weight: 500;
  margin-bottom: 1rem;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.08);
}

.med-card .med-name {
  flex-grow: 1;
}

.med-card .med-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.med-card.day {
  background-color: #fff9c4;
  color: #5d4037;
  border: 1px solid #f4e04d;
}

.med-card.night {
  background-color: #f3e8fd;
  color: #4a148c;
  border: 1px solid #c69be4;
}

.music-player {
  background-color: #eeddf2;
  border: 1px solid #d3b9d9;
  padding: 1rem 1.5rem;
  border-radius: 20px;
  text-align: center;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #4a148c;
}

.calendar-placeholder {
  border: 1px solid #ccc;
  background: #fdfdfd;
  padding: 1.5rem;
  border-radius: 15px;
  text-align: center;
  color: #555;
  font-style: italic;
  flex-grow: 1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.sos-button {
  background-color: #d9534f;
  color: white;
  border: none;
  padding: 0.6rem 1.4rem;
  border-radius: 50px;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.sos-button:disabled {
  background-color: #e7a1a1;
  cursor: not-allowed;
}

.sos-alert {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  border-radius: 8px;
  z-index: 1000;
}

.error-state {
  text-align: center;
  padding: 3rem;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 15px;
  border: 1px solid #f5c6cb;
}
</style>
