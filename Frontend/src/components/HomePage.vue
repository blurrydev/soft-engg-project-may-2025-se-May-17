<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <div class="greeting"></div>
      <Navbar/>
    </header>

    <main class="main-content">
      <div class="medications-column">
        <div class="header-section">
          <p class="date">{{ formattedDate }}</p>
          <h5 class="greeting">Greetings, {{ caregiverName }}</h5>
        </div>

        <h4 class="subheading">Next Medications in this Time Slot</h4>

        <div v-if="loading" class="loading-state">
          <p>Loading dependents' schedules...</p>
        </div>
        
        <div v-else-if="processedDependents.length === 0" class="loading-state">
          <p>No upcoming medications for any dependents in this time period.</p>
        </div>

        <div v-else>
          <div v-for="(dependent, index) in processedDependents" :key="dependent.id" class="chart-card">
            <header class="dependent-header">
              <h3>{{ dependent.relation }}'s Next Medication</h3>
              <a href="#" class="view-all-link" @click.prevent="openMedicationModal(dependent)">View All</a>
            </header>

            <div v-if="dependent.medications.length > 0" :class="['med-info-card', cardColors[index % cardColors.length]]">
              <span class="pill-icon">💊</span>
              <span class="med-name">{{ dependent.medications[0].medicine_title }}</span>
              <span class="med-dosage">{{ dependent.medications[0].dosage }}</span>
              <span class="med-time"><span class="icon">⏰</span>{{ dependent.medications[0].reminder_slot }}</span>
              <button class="poke-button" :disabled="!isPokeEnabled(dependent.medications[0].reminder_slot)" @click="poke(dependent.relation)">POKE</button>
            </div>
          </div>
        </div>
      </div>

      <div class="calendar-column">
        <AppCalendar />
      </div>
    </main>

    <!-- Medication Modal -->
    <div v-if="isModalVisible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h4 class="modal-title">{{ selectedDependent.relation }}'s medications</h4>

        <div v-if="isModalLoading" class="modal-loading">Loading medications...</div>

        <div v-else class="modal-meds-list">
          <div class="modal-meds-category">
            <div class="category-header"><span class="category-icon">☀️</span> Daytime Meds</div>
            <p v-if="modalMeds.daytime.length === 0" class="no-meds-text">No daytime medications scheduled.</p>
            <div v-else v-for="med in modalMeds.daytime" :key="med.id" class="modal-med-card day">
              <span class="pill-icon">💊</span>
              <span class="med-name">{{ med.medicineName }}</span>
              <span class="med-dosage">{{ med.dosage }}</span>
              <span class="med-time"><span class="icon">⏰</span>{{ med.time }}</span>
            </div>
          </div>

          <div class="modal-meds-category">
            <div class="category-header"><span class="category-icon">🌙</span> Nighttime Meds</div>
            <p v-if="modalMeds.nighttime.length === 0" class="no-meds-text">No nighttime medications scheduled.</p>
            <div v-else v-for="med in modalMeds.nighttime" :key="med.id" class="modal-med-card night">
              <span class="pill-icon">💊</span>
              <span class="med-name">{{ med.medicineName }}</span>
              <span class="med-dosage">{{ med.dosage }}</span>
              <span class="med-time"><span class="icon">⏰</span>{{ med.time }}</span>
            </div>
          </div>
        </div>
        <button class="modal-close-button" @click="closeModal">Close</button>
      </div>
    </div>

    <div v-if="pokeMessage" class="poke-alert" @click="pokeMessage = ''">
      {{ pokeMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import AppCalendar from '@/components/AppCalendar.vue';
import Navbar from './Navbar.vue';

import { getUpcomingMedicationsForCaregiver, getDependentsDetails, getTodaysMedsForDependent } from '@/services/mockApi.js';

const route = useRoute();


const upcomingMedications = ref([]);
const dependentsInfo = ref([]);
const caregiverName = ref(sessionStorage.getItem('user_name') || 'User');
const loading = ref(true);
const pokeMessage = ref('');
const cardColors = ref(['color-yellow', 'color-purple', 'color-blue']);
const isModalVisible = ref(false);
const isModalLoading = ref(false);
const selectedDependent = ref(null);
const modalMeds = ref({ daytime: [], nighttime: [] });

const formattedDate = computed(() => new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }));



const processedDependents = computed(() => {
  if (dependentsInfo.value.length === 0) return [];
  return dependentsInfo.value.map(dep => ({
    ...dep,
    medications: upcomingMedications.value.filter(med => med.user_id === dep.id),
  })).filter(dep => dep.medications.length > 0);
});

async function fetchData(caregiverId) {
  loading.value = true;
  try {
    const response = await getUpcomingMedicationsForCaregiver(caregiverId);
    upcomingMedications.value = response.upcoming_medications;
    const ids = [...new Set(response.upcoming_medications.map(med => med.user_id))];
    dependentsInfo.value = ids.length > 0 ? await getDependentsDetails(ids) : [];
  } catch (error) {
    console.error("Fetch error:", error);
  } finally {
    loading.value = false;
  }
}

function isPokeEnabled(slot) {
  const hour = new Date().getHours();
  if (!slot) return false;
  const slotLower = slot.toLowerCase();
  if (slotLower.includes('breakfast')) return hour >= 4 && hour <= 10;
  if (slotLower.includes('lunch')) return hour >= 10 && hour <= 15;
  if (slotLower.includes('dinner')) return hour >= 16 && hour <= 23;
  return false;
}

function poke(relation) {
  pokeMessage.value = `A reminder notification has been sent to ${relation}.`;
  setTimeout(() => { pokeMessage.value = '' }, 4000);
}

async function openMedicationModal(dependent) {
  if (!dependent) return;
  selectedDependent.value = dependent;
  isModalVisible.value = true;
  isModalLoading.value = true;
  try {
    modalMeds.value = await getTodaysMedsForDependent(dependent.id);
  } catch (error) {
    console.error(error);
    modalMeds.value = { daytime: [], nighttime: [] };
  } finally {
    isModalLoading.value = false;
  }
}

function closeModal() {
  isModalVisible.value = false;
  selectedDependent.value = null;
}

onMounted(() => {
  const caregiverId = route.params.userId;
  if (caregiverId) {
    if (caregiverId === 'user_101') caregiverName.value = 'John';
    fetchData(caregiverId);
  }
});
</script>

<style scoped>
.dashboard-wrapper {
  background-color: #f0f8f1;
  min-height: 100vh;
  font-family: "Times New Roman", serif;
  padding: 0;
}

.topbar {
  background-color: #0097a7;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.topbar .icon {
  font-size: 1.4rem;
  cursor: pointer;
}

.right-icons {
  display: flex;
  gap: 1.5rem;
  font-size: 1.5rem;
  align-items: center;
}

.logout-button {
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}

.header-section {
  padding: 2rem 3rem 0;
}

.date {
  font-size: 1rem;
  color: #555;
  margin-bottom: 0.5rem;
}

.greeting {
  font-size: 2.2rem;
  color: #333;
  margin-top: 0;
}

.main-content {
  display: flex;
  gap: 3rem;
  padding: 2rem 3rem;
}

.medications-column {
  flex: 3;
}

.calendar-column {
  flex: 2;
  min-width: 350px;
}

.subheading {
  font-size: 1.4rem;
  font-weight: bold;
  color: #333;
  margin: 2rem 0 1.5rem;
}

.chart-card {
  background-color: white;
  border-radius: 18px;
  padding: 1.5rem;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.med-info-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 500;
  border: 2px solid;
}

.pill-icon, .icon {
  font-size: 1.4rem;
}

.med-name {
  flex-grow: 1;
  font-weight: bold;
}

.color-yellow { background-color: #fffde7; border-color: #fbc02d; }
.color-purple { background-color: #f3e5f5; border-color: #ab47bc; }
.color-blue { background-color: #e3f2fd; border-color: #42a5f5; }

.poke-button {
  background-color: #d9534f;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0.6rem 1.5rem;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
}

.poke-button:disabled {
  background-color: #ed6e7b;
  cursor: not-allowed;
  opacity: 0.9;
}

.poke-alert {
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

.dependent-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
}

.view-all-link {
  font-size: 1rem;
  color: #007bff;
  font-weight: bold;
  text-decoration: none;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #ffffff;
  padding: 2rem 2.5rem;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
}

.modal-title {
  text-align: center;
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.modal-loading {
  text-align: center;
  font-style: italic;
  font-size: 1.2rem;
  padding: 2rem;
}

.modal-meds-category {
  margin-bottom: 1.5rem;
}

.modal-med-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 50px;
  font-size: 1rem;
  border: 2px solid;
  margin-bottom: 0.75rem;
}

.modal-med-card.day { background-color: #fffde7; border-color: #fbc02d; }
.modal-med-card.night { background-color: #f3e5f5; border-color: #ab47bc; }

.modal-close-button {
  background-color: #0d6efd;
  color: white;
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  cursor: pointer;
  margin-top: 2rem;
  display: block;
  margin-left: auto;
  margin-right: auto;
}
</style>
