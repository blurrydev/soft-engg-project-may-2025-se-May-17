<template>
  <div class="dashboard-wrapper">
    <header class="header">
      <div class="date-section">
        <p class="date">{{ formattedDate }}</p>
        <h5 class="greeting">Greetings, {{ caregiverName }}</h5>
      </div>
      <div class="header-icons">
        <span>🔔</span>
        <router-link to="/caregiver-stats">
          <span>📈</span>
        </router-link>
        <router-link to="/profile">
        <span>👤</span>
        </router-link>
        <button class="logout-button" @click="logout">Logout</button>
      </div>
    </header>

    <main class="main-content">
      <div class="medications-column">
        <h2 class="subheading">Next Medications in this Time Slot</h2>

        <div v-if="loading" class="loading-state">
          <p>Loading dependents' schedules...</p>
        </div>
        
        <div v-else-if="processedDependents.length === 0" class="loading-state">
          <p>No upcoming medications for any dependents in this time period.</p>
        </div>

        <div v-else>
          <!-- Loop through the processed data -->
          <div v-for="(dependent, index) in processedDependents" :key="dependent.id" class="dependent-card">
            <header class="dependent-header">
              <h3>{{ dependent.relation }}'s Next Medication</h3>
                <a href="#" class="view-all-link" @click.prevent="openMedicationModal(dependent)">View All</a>
            </header>

            <!-- The API can return multiple meds per user in a slot, we show the first one -->
            <div v-if="dependent.medications.length > 0" :class="['med-info-card', cardColors[index % cardColors.length]]">
              <span class="pill-icon">💊</span>
              <span class="med-name">{{ dependent.medications[0].medicine_title }}</span>
              <span class="med-dosage">{{ dependent.medications[0].dosage }}</span>
              <span class="med-time">
                <span class="icon">⏰</span>
                <!-- Display the reminder slot from the new API response -->
                {{ dependent.medications[0].reminder_slot }}
              </span>
              <button
                class="poke-button"
                :disabled="!isPokeEnabled(dependent.medications[0].reminder_slot)"
                @click="poke(dependent.relation)">
                POKE
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="calendar-column">
        <div class="calendar-placeholder">(Calendar will be implemented here)</div>
      </div>
    </main>

        <!-- NEW: Medication Details Modal -->
    <div v-if="isModalVisible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2 class="modal-title">{{ selectedDependent.relation }}'s medications</h2>
        
        <div v-if="isModalLoading" class="modal-loading">Loading medications...</div>
        
        <div v-else class="modal-meds-list">
          <!-- Daytime Meds -->
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
          <!-- Nighttime Meds -->
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
import { useRoute, useRouter } from 'vue-router';
// Import the new and helper mock API functions
import { getUpcomingMedicationsForCaregiver, getDependentsDetails, getTodaysMedsForDependent } from '@/services/mockApi.js';

const route = useRoute();
const router = useRouter();

// This will hold the raw flat list from the API
const upcomingMedications = ref([]);
// This will hold the dependent user objects (Mom, Dad, etc.)
const dependentsInfo = ref([]);

const caregiverName = ref('User');
const loading = ref(true);
const pokeMessage = ref('');

const cardColors = ref(['color-yellow', 'color-purple', 'color-blue']);

const isModalVisible = ref(false);
const isModalLoading = ref(false);
const selectedDependent = ref(null);
const modalMeds = ref({ daytime: [], nighttime: [] });

const formattedDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
});

function logout() {
  sessionStorage.clear();
  router.push('/login'); // Use the router instance for navigation
}
// This computed property transforms the raw API data into a structure the template can use
const processedDependents = computed(() => {
  if (dependentsInfo.value.length === 0) return [];
  
  return dependentsInfo.value.map(dep => {
    // Filter the flat list to get meds just for this dependent
    const medsForThisDependent = upcomingMedications.value.filter(
      med => med.user_id === dep.id
    );
    return {
      ...dep, // a.k.a id, relation, firstName
      medications: medsForThisDependent,
    };
  }).filter(dep => dep.medications.length > 0); // Only show dependents with meds in this slot
});


async function fetchData(caregiverId) {
  loading.value = true;
  try {
    const response = await getUpcomingMedicationsForCaregiver(caregiverId);
    upcomingMedications.value = response.upcoming_medications;

    // Now get the details (like 'relation') for the dependents who have meds
    const dependentIdsWithMeds = [...new Set(response.upcoming_medications.map(med => med.user_id))];
    if (dependentIdsWithMeds.length > 0) {
        dependentsInfo.value = await getDependentsDetails(dependentIdsWithMeds);
    }

  } catch (error) {
    console.error("Failed to fetch dependent medication data:", error);
  } finally {
    loading.value = false;
  }
}
function isPokeEnabled(slot) {
  const hour = new Date().getHours();

  if (!slot) return false;

  const slotLower = slot.toLowerCase();

  if (slotLower.includes('breakfast')) {
    return hour >= 4 && hour <= 10;
  }
  if (slotLower.includes('lunch')) {
    return hour >= 10 && hour <= 15;
  }
  if (slotLower.includes('dinner')) {
    return hour >= 16 && hour <= 23;
  }

  // Default to disabled
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
    // Call the new API function
    modalMeds.value = await getTodaysMedsForDependent(dependent.id);
  } catch (error) {
    console.error(`Failed to load all-day meds for ${dependent.id}`, error);
    modalMeds.value = { daytime: [], nighttime: [] }; // Reset on error
  } finally {
    isModalLoading.value = false;
  }
}

function closeModal() {
  isModalVisible.value = false;
  selectedDependent.value = null; // Clean up state
}
// --- END MODAL FUNCTIONS ---
onMounted(() => {
  const caregiverId = route.params.userId;
  if (caregiverId) {
    if (caregiverId === 'user_101') {
        caregiverName.value = 'John';
    }
    fetchData(caregiverId);
  } else {
    console.error("No caregiver ID found in URL.");
    loading.value = false;
  }
});
</script>

<style scoped>
/* Styles are identical to the previous response, no changes needed */
.dashboard-wrapper {
  background-color: #eaf5e9;
  font-family: "Times New Roman", serif;
  padding: 2rem 3rem;
  border-radius: 25px;
  border: 1px solid #cce2c9;
  max-width: 1400px;
  margin: auto;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}
.header {
  display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem;
}
.date-section .date { font-size: 1.1rem; color: #555; margin: 0; }
.greeting { font-size: 2.5rem; color: #333; margin-top: 0.5rem; font-weight: normal; }
.header-icons { display: flex; gap: 1.5rem; font-size: 1.8rem; color: #444; cursor: pointer; }
.main-content { display: flex; gap: 3rem; }
.medications-column { flex: 3; }
.calendar-column { flex: 2; min-width: 350px; }
.subheading { font-size: 1.4rem; font-weight: bold; color: #333; margin-bottom: 1.5rem; }
.dependent-card { margin-bottom: 2rem; }
.dependent-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem; }
.dependent-header h3 { font-size: 1.2rem; margin: 0; color: #333; }
.view-all-link { font-size: 1rem; color: #007bff; text-decoration: none; font-weight: bold; }
.view-all-link:hover { text-decoration: underline; }
.med-info-card { display: flex; align-items: center; gap: 1.5rem; padding: 1rem 1.5rem; border-radius: 50px; font-size: 1.1rem; border: 2px solid; }
.med-info-card.empty { font-style: italic; justify-content: center; }
.pill-icon, .icon { font-size: 1.4rem; }
.med-name { flex-grow: 1; font-weight: bold; }
.med-dosage, .med-time { display: flex; align-items: center; gap: 0.5rem; }
.color-yellow { background-color: #fffde7; border-color: #fbc02d; }
.color-purple { background-color: #f3e5f5; border-color: #ab47bc; }
.color-blue { background-color: #e3f2fd; border-color: #42a5f5; }
.poke-button { background-color: #d9534f; color: white; border: none; border-radius: 20px; padding: 0.6rem 1.5rem; font-weight: bold; font-family: "Times New Roman", serif; font-size: 1rem; cursor: pointer; transition: background-color 0.2s; }
.poke-button:hover { background-color: #c9302c; }
.calendar-placeholder { border: 1px solid #ccc; background: #fff; padding: 1rem; border-radius: 10px; font-style: italic; color: #666; text-align: center; }
.poke-alert { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: #2c3e50; color: white; padding: 1rem 2rem; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); z-index: 1000; }
.loading-state { text-align: center; padding: 3rem; font-style: italic; color: #666; }
/* --- NEW MODAL STYLES --- */
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
  background-color: #d9eafc; /* Light blue from mockup */
  padding: 2rem 2.5rem;
  border-radius: 20px;
  border: 1px solid #a0b8d0;
  box-shadow: 0 5px 20px rgba(0,0,0,0.3);
  width: 90%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
}
.modal-title {
  text-align: center;
  font-size: 1.8rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}
.modal-loading {
  text-align: center;
  font-style: italic;
  padding: 3rem;
  font-size: 1.2rem;
}
.modal-meds-list { display: flex; flex-direction: column; gap: 1.5rem; }
.modal-meds-category .category-header { font-size: 1.2rem; font-weight: bold; color: #333; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }
.no-meds-text { font-style: italic; color: #555; padding-left: 1rem; }

.modal-med-card {
    display: flex; align-items: center; gap: 1.5rem; padding: 0.8rem 1.5rem; border-radius: 50px; font-size: 1rem; font-weight: 500; margin-bottom: 0.75rem; border: 2px solid;
}
.modal-med-card.day { background-color: #fffde7; border-color: #fbc02d; }
.modal-med-card.night { background-color: #f3e5f5; border-color: #ab47bc; }

.modal-close-button {
  background-color: #0d6efd;
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 10px;
  font-size: 1.1rem;
  cursor: pointer;
  margin-top: 2rem;
  align-self: center;
  transition: background-color 0.2s;
}
.modal-close-button:hover { background-color: #0b5ed7; }
.poke-button:disabled {
  background-color: #ed6e7b;  /* soft alert tone */
  color: white;
  cursor: not-allowed;
  opacity: 0.9;
}

</style>