<template>
  <div class="container mt-5">
    <!-- Success Alert -->
    <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
      {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''" aria-label="Close">X</button>
    </div>
    <!-- Error Alert -->
    <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
      {{ errorMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''" aria-label="Close">X</button>
    </div>
  </div>
  <div class="dashboard-wrapper">
    <div class="header">
      <div class="date-section">
        <p class="today-label">Today</p>
        <p class="date">{{ currentDate }}</p>
        <h2 class="greeting">Good Morning, {{ userName }}</h2>
        <h4 class="subheading">Upcoming Medications</h4>
      </div>
      <div class="icons">
        <span>
    <!-- SOS Button -->
    <button class="btn btn-danger" @click="sendSOS" :disabled="loading">
      {{ loading ? 'Sending...' : 'Send SOS' }}
    </button></span>
        <span>🔔</span>
        <span>📈</span>
        <span>👤</span>
        <button class="logout-button" @click="logout">Logout</button>
      </div>
    </div>

    <div class="content-row">
      <div class="medications-list">
        <div v-if="upcomingMeds.length === 0" class="no-med">No upcoming medications</div>
        <div v-for="(med, index) in upcomingMeds" :key="index" class="med-card">
          <span class="pill-icon">💊</span>
          <span class="med-name">{{ med.medicine_name }}</span>
          <span class="med-dosage">{{ med.dosage }}</span>
          <span class="med-time">⏰ {{ med.time }}</span>
        </div>
      </div>

      
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import axios from '@/services/apiService';
import { useRouter } from 'vue-router';

const router = useRouter();

const currentDate = new Date().toDateString();
const userName = sessionStorage.getItem("first_name") || 'User';
const upcomingMeds = ref([]);

// SOS State
const loading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

// Fetch upcoming medications
async function fetchUpcomingMeds() {
  try {
    const response = await axios.get('/upcoming-medications');
    upcomingMeds.value = response.data.upcoming_medications;
  } catch (error) {
    console.error("Error fetching upcoming medications", error);
  }
}

// Send SOS mock
async function sendSOS() {
  loading.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    // Simulated delay for frontend-only demo
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Simulated success
    successMessage.value = 'SOS alert sent successfully!';
  } catch (error) {
    errorMessage.value = 'Failed to send SOS alert.';
  } finally {
    loading.value = false;
  }
}

// Logout
function logout() {
  sessionStorage.clear();
  router.push('/login');
}

onMounted(() => {
  fetchUpcomingMeds();
});
</script>

<style scoped>
.dashboard-wrapper {
  background-color: #d6eed6;
  font-family: "Times New Roman", serif;
  padding: 2rem;
  border-radius: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.date-section {
  color: #333;
}

.greeting {
  margin-top: 1rem;
  font-size: 1.5rem;
}

.subheading {
  font-weight: bold;
  margin-top: 1rem;
}

.icons {
  display: flex;
  align-items: center;
}

.icons span {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.logout-button {
  background-color: #444;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-family: "Times New Roman", serif;
}

.logout-button:hover {
  background-color: #222;
}

.content-row {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
}

.medications-list {
  flex: 2;
}

.med-card {
  background-color: #cfe2ff;
  border-left: 6px solid #4a90e2;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 1rem;
}

.pill-icon {
  font-size: 1.3rem;
}

.med-name, .med-dosage, .med-time {
  margin: 0 1rem;
}

.no-med {
  font-style: italic;
  color: #777;
}
.alert {
  position: relative;
  padding-right: 2.5rem; /* Make room for the close button */
}

.btn-close {
  position: absolute;
  top: 0.75rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.2rem;
  opacity: 0.5;
  cursor: pointer;
}

.btn-close:hover {
  opacity: 1;
}



.green { background-color: green; color: white; }
.red { background-color: red; color: white; }
.default { background-color: lightgray; }
.mom { background-color: lightgreen; }
</style>
