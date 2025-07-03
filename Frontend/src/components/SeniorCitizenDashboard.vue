<template>
  <div class="dashboard-container">
    <div class="header">
      <div class="date-section">
        <p class="today-label">Today</p>
        <p class="date">{{ formattedDate }}</p>
      </div>
      <div class="header-icons">
        <button class="sos-button" @click="sendSOS" :disabled="sosLoading">
          {{ sosLoading ? '...' : 'SOS' }}
        </button>
        <span>🔔</span>
        <router-link to="/senior-stats">
          <span>📈</span>
        </router-link>
        <router-link to="/profile">
          <span>👤</span>
        </router-link>
        <button class="logout-button" @click="logout">Logout</button>

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
          <!-- Daytime Meds -->
          <div class="meds-category">
            <div class="category-header"><span class="category-icon">☀️</span> Daytime Meds</div>
            <div v-if="daytimeMeds.length === 0" class="med-card-day empty">No daytime medications.</div>
            <div v-else v-for="med in daytimeMeds" :key="med.id" class="med-card-day">
              <span class="icon pill-icon">💊</span>
              <span class="med-name">{{ med.medicineName }}</span>
              <span class="med-dosage">{{ med.dosage }}</span>
              <span class="med-time"><span class="icon clock-icon">⏰</span>{{ med.time }}</span>
            </div>
          </div>
          <!-- Nighttime Meds -->
          <div class="meds-category">
            <div class="category-header"><span class="category-icon">🌙</span> Nighttime Meds</div>
            <div v-if="nighttimeMeds.length === 0" class="med-card-night empty">No nighttime medications.</div>
            <div v-else v-for="med in nighttimeMeds" :key="med.id" class="med-card-night">
              <span class="icon pill-icon">💊</span>
              <span class="med-name">{{ med.medicineName }}</span>
              <span class="med-dosage">{{ med.dosage }}</span>
              <span class="med-time"><span class="icon clock-icon">⏰</span>{{ med.time }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="music-player">
          <span class="icon">🎵</span> Background Music <span class="controls">⏮️ ▶️ ⏭️</span>
        </div>
        <div class="calendar-placeholder">
          <p>Great Job tracking your medication!</p>
          (Calendar component will be implemented here)
        </div>
      </div>
    </div>

    <div v-if="sosMessage" class="sos-alert" @click="sosMessage = ''">{{ sosMessage }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router'; // Import useRouter

// Correctly import the functions with their actual names from mockApi.js
import { 
  getDependentDetails, 
  getUpcomingMedication, 
  getTodaysMedsForDependent 
} from '@/services/mockApi.js';

const route = useRoute();
const router = useRouter(); // Instantiate the router for navigation

const userName = ref('User');
const nextMedication = ref(null);
const daytimeMeds = ref([]);
const nighttimeMeds = ref([]);
const loading = ref(true);
const error = ref(null);

const sosLoading = ref(false);
const sosMessage = ref('');

const formattedDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
});

// This function is now defined at the top level, visible to the template
function logout() {
  sessionStorage.clear();
  router.push('/login'); // Use the router instance for navigation
}

async function fetchAllDataForSenior(seniorId) {
  loading.value = true;
  error.value = null;
  try {
    // Use the corrected function names in the Promise.all call
    const [details, nextMed, allMeds] = await Promise.all([
      getDependentDetails(seniorId),
      getUpcomingMedication(seniorId),
      getTodaysMedsForDependent(seniorId)
    ]);

    if (!details) {
      throw new Error(`No dependent found with ID: ${seniorId}`);
    }

    userName.value = details.firstName;
    nextMedication.value = nextMed;
    daytimeMeds.value = allMeds.daytime;
    nighttimeMeds.value = allMeds.nighttime;

  } catch (err) {
    console.error(`Failed to fetch dashboard data for senior ${seniorId}:`, err);
    error.value = 'Could not load dashboard data. Please try again later.';
  } finally {
    loading.value = false;
  }
}

// sendSOS function needs to be defined at the top level too
async function sendSOS() {
  sosLoading.value = true;
  sosMessage.value = '';
  await new Promise(resolve => setTimeout(resolve, 1000));
  sosMessage.value = 'SOS Alert has been sent to your caregivers.';
  sosLoading.value = false;
  setTimeout(() => { sosMessage.value = '' }, 4000);
}

onMounted(() => {
  const dep_id = route.params.dep_id;
  if (dep_id) {
    fetchAllDataForSenior(dep_id);
  } else {
    error.value = "No dependent ID found in the URL. Cannot load dashboard.";
    loading.value = false;
  }
});
</script>

<style scoped>
/* --- General Layout & Font --- */
.dashboard-container {
  background-color: #eaf5e9;
  font-family: "Times New Roman", serif;
  line-height: 1.6;
  padding: 2.5rem 3rem;
  border-radius: 25px;
  border: 1px solid #cce2c9;
  max-width: 1300px;
  margin: auto;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

/* --- Header Section --- */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
}
.date-section .today-label, .date-section .date {
  font-size: 1rem; color: #555; margin: 0;
}
.header-icons {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.header-icons span {
  font-size: 1.6rem;
  cursor: pointer;
  color: #444;
}
.sos-button {
  background-color: #d9534f;
  color: white;
  border: none;
  padding: 0.8rem 1.8rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* --- Main Content Layout --- */
.main-content {
  display: flex;
  gap: 3rem;
}
.left-panel { flex: 2; min-width: 0; }
.right-panel { flex: 1; min-width: 320px; display: flex; flex-direction: column; gap: 1.5rem; }

/* --- Typography & Section Spacing --- */
.motivational-quote { font-style: italic; color: #666; text-align: center; margin: 0 auto 2.5rem auto; max-width: 80%; }
.greeting { font-family: 'Georgia', serif; font-weight: 500; font-size: 2.5rem; margin: 0 0 1rem 0; color: #333; }
.subheading { font-weight: bold; color: #444; margin-top: 2.5rem; margin-bottom: 1rem; font-size: 1.2rem; border-bottom: 1px solid #d0e0cf; padding-bottom: 0.5rem; }
.today-meds-title { margin-top: 3.5rem; }

/* --- Base Medication Card Style (for individual pills) --- */
[class*="-med-card"] {
  padding: 1rem 1.8rem;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 1rem;
  border: 1px solid transparent; /* Keep layout consistent, but hide border */
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
[class*="-med-card"] .med-name { flex-grow: 1; }
[class*="-med-card"] .med-time { display: flex; align-items: center; gap: 0.5rem; }
.icon { font-size: 1.4rem; }
.upcoming-med-card { background-color: #cde1ff; border-color: #a0b5d0; color: #2c3e50; }

/* --- NEW and MODIFIED Styles for the Day/Night Sections --- */

.todays-meds-container {
  display: flex;
  flex-direction: column;
  gap: 2rem; /* Increased space between the Daytime and Nighttime boxes */
}

/* This is the new container box for Daytime and Nighttime sections */
.meds-category {
  background-color: #f7fbf6; /* A slightly off-white to create a "box" effect */
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
  margin-bottom: 1.5rem; /* More space between header and first pill */
}
.category-icon { font-size: 1.5rem; }

/* Styling for the pills INSIDE the new boxes */
.med-card-day {
  background-color: #fff9c4; /* Soft Yellow */
  color: #5d4037;
  border-color: #fadf98; /* Subtle border for definition */
  box-shadow: none; /* Remove shadow to make it feel "inside" the box */
}
.med-card-night {
  background-color: #e1bee7; /* Soft Purple */
  color: #4a148c;
  border-color: #d3b9d9; /* Subtle border for definition */
  box-shadow: none; /* Remove shadow */
}
.med-card-day .pill-icon, .upcoming-med-card .pill-icon { color: #d9534f; }
.med-card-night .pill-icon { color: #8e24aa; }


/* --- Right Panel Widgets --- */
.music-player { background-color: #eeddf2; border: 1px solid #d3b9d9; padding: 1rem 1.5rem; border-radius: 20px; text-align: center; font-weight: bold; display: flex; align-items: center; justify-content: space-between; color: #4a148c; }
.calendar-placeholder { border: 1px solid #ccc; background: #fdfdfd; padding: 1.5rem; border-radius: 15px; text-align: center; color: #555; font-style: italic; flex-grow: 1; }
.calendar-placeholder p { font-style: normal; font-weight: bold; color: #333; }

/* --- Alerts & Error States --- */
.sos-alert { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: #2c3e50; color: white; padding: 1rem 2rem; border-radius: 8px; z-index: 1000; }
.error-state { text-align: center; padding: 4rem; color: #d9534f; background-color: #f8d7da; border-radius: 15px; border: 1px solid #d9534f; }
</style>