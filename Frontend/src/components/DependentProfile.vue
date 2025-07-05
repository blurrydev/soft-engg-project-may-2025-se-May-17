<template>
  <div class="page-container">
    <div v-if="isLoading" class="loading">Loading Profile...</div>
    <div v-else-if="!dependent" class="loading">Profile not found.</div>
    
    <div v-else class="profile-container">
    <header class="dashboard-header">
      <div class="greeting"></div>
      <Navbar/>
    </header>
      <h1>{{ dependent.firstName }}'s Profile</h1>

      <!-- User Details Section -->
      <div class="user-details-grid">
        <div class="detail-item">
          <label>1. Name of the person</label>
          <input type="text" :value="`${dependent.firstName} ${dependent.lastName}`" readonly />
        </div>
        <div class="detail-item">
          <label>2. Age</label>
          <input type="text" :value="dependent.age" readonly />
        </div>
        <div class="detail-item">
          <label>3. How are you related to him/her?</label>
          <input type="text" :value="dependent.relation" readonly />
        </div>
      </div>

      <!-- Daytime Meds Section -->
      <div class="meds-section">
        <div class="meds-header">
          <span><i class="icon-sun"></i> Daytime Meds</span>
          <button class="add-medicine-btn" @click="openAddMedModal">Add a medicine</button>
        </div>
        <div v-if="daytimeMeds.length === 0" class="no-meds">No daytime medicines scheduled.</div>
        <div v-for="med in daytimeMeds" :key="med.id" class="med-row daytime">
          <i class="icon-pill"></i>
          <span class="med-name">{{ med.medicineTitle }}</span>
          <span class="med-dosage">{{ med.dosage }}</span>
          <span class="med-time"><i class="icon-clock"></i> {{ formatTime(med) }}</span>
          <span class="icon-trash" @click="handleDeleteMed(med.id)"></span>
        </div>
      </div>

      <!-- Nighttime Meds Section -->
      <div class="meds-section">
        <div class="meds-header">
          <span><i class="icon-moon"></i> Nighttime Meds</span>
        </div>
        <div v-if="nighttimeMeds.length === 0" class="no-meds">No nighttime medicines scheduled.</div>
        <div v-for="med in nighttimeMeds" :key="med.id" class="med-row nighttime">
          <i class="icon-pill"></i>
          <span class="med-name">{{ med.medicineTitle }}</span>
          <span class="med-dosage">{{ med.dosage }}</span>
          <span class="med-time"><i class="icon-clock"></i> {{ formatTime(med) }}</span>
          <span class="icon-trash" @click="handleDeleteMed(med.id)"></span>
        </div>
      </div>
    </div>
    
    <!-- Add Medicine Modal -->
    <AddMedicineModal
      v-if="showAddMedModal"
      @close="closeAddMedModal"
      @add-medication="handleAddMedication"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from './Navbar.vue';
// Import mock API functions
import { 
  getDependentDetails, 
  getDependentMedications,
  deleteMedicationMapping,
  addMedicationToDependent,
} from '../services/mockApi';

// A separate component for the modal to keep this file cleaner
import AddMedicineModal from './AddMedicineModal.vue';

// --- State ---
const route = useRoute();
const isLoading = ref(true);
const dependent = ref(null);
const medications = ref([]);
const showAddMedModal = ref(false);

const userId = route.params.userId;

// --- Lifecycle ---
onMounted(async () => {
  // Fetch data from our mock API
  const [details, meds] = await Promise.all([
    getDependentDetails(userId),
    getDependentMedications(userId)
  ]);
  dependent.value = details;
  medications.value = meds;
  isLoading.value = false;
});

// --- Computed Properties ---
const daytimeMeds = computed(() => 
  medications.value.filter(med => med.breakfast_before || med.breakfast_after || med.lunch_before || med.lunch_after)
);

const nighttimeMeds = computed(() => 
  medications.value.filter(med => med.dinner_before || med.dinner_after)
);

// --- Methods ---
function formatTime(med) {
  const times = [];
  if (med.breakfast_before) times.push('Before Breakfast');
  if (med.breakfast_after) times.push('After Breakfast');
  if (med.lunch_before) times.push('Before Lunch');
  if (med.lunch_after) times.push('After Lunch');
  if (med.dinner_before) times.push('Before Dinner');
  if (med.dinner_after) times.push('After Dinner');
  return times.join(', ');
}

async function handleDeleteMed(mapId) {
  if (confirm('Are you sure you want to delete this medicine schedule?')) {
    const response = await deleteMedicationMapping(mapId);
    if (response.success) {
      // For instant UI update, filter it out from the local array
      medications.value = medications.value.filter(m => m.id !== mapId);
    } else {
      alert('Failed to delete medicine.');
    }
  }
}

async function handleAddMedication(medMapData) {
  // Call mock API to add the new mapping
  const newMedMap = await addMedicationToDependent(userId, medMapData);
  // Add the result to our local array for UI update
  medications.value.push(newMedMap);
  closeAddMedModal();
}

const openAddMedModal = () => showAddMedModal.value = true;
const closeAddMedModal = () => showAddMedModal.value = false;
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

/* Icon styles */
.icon-sun::before { content: '\f185'; font-family: 'Font Awesome 6 Free'; font-weight: 900; margin-right: 8px; }
.icon-moon::before { content: '\f186'; font-family: 'Font Awesome 6 Free'; font-weight: 900; margin-right: 8px; }
.icon-pill::before { content: '\f484'; font-family: 'Font Awesome 6 Free'; font-weight: 900; color: #dc3545; }
.icon-clock::before { content: '\f017'; font-family: 'Font Awesome 6 Free'; font-weight: 400; margin-right: 5px; }
.icon-trash::before { content: '\f2ed'; font-family: 'Font Awesome 6 Free'; font-weight: 900; color: #dc3545; cursor: pointer; }

/* General page */
.page-container {
  background-color: #eaf5e9;
  font-family: "Times New Roman", serif;
  min-height: calc(100vh - 58px);
  padding: 2.5rem 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading {
  font-size: 1.5rem;
  color: #555;
  margin-top: 5rem;
}

.profile-container {
  background-color: #fdfdfd;
  border-radius: 16px;
  padding: 2rem 3rem;
  width: 100%;
  max-width: 950px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Title */
h1 {
  text-align: center;
  margin-bottom: 2rem;
  font-weight: 600;
}

/* User detail grid */
.user-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.detail-item {
  font-family: 'Times New Roman';

  display: flex;
  flex-direction: column;
}

.detail-item label {
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.detail-item input {
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #b0d0b0;
  background-color: #f9fff9;
  font-family: inherit;
  font-size: 1rem;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}

/* Medication sections */
.meds-section {
  margin-bottom: 2rem;
}

.meds-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.3rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 1rem;
}

/* Add Med Button */
.add-medicine-btn {
  background-color: #4a74ce;
  color: white;
  border: none;
  padding: 8px 18px;
  font-size: 0.95rem;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  transition: background-color 0.2s ease;
}
.add-medicine-btn:hover {
  background-color: #00796b;
}

/* Med row styling - pill card look */
.med-row {
  display: grid;
  grid-template-columns: 30px 1fr 1fr 1.2fr 30px;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.2rem;
  border-radius: 25px;
  margin-bottom: 1rem;
  font-family: 'Times New Roman';
  box-shadow: 0 4px 8px rgba(0,0,0,0.06);
  border: 2px solid transparent;
}

/* Backgrounds based on time */
.med-row.daytime {
  background-color: #fffce8;
  border-color: #ffe082;
}

.med-row.nighttime {
  background-color: #f3e8ff;
  border-color: #ce93d8;
}

/* Med row text formatting */
.med-name {
  font-weight: bold;
  font-size: 1rem;
  color: #2e2e2e;
}

.med-dosage {
  color: #555;
  font-size: 0.95rem;
}

.med-time {
  font-size: 0.92rem;
  color: #666;
  display: flex;
  align-items: center;
}

/* No meds message */
.no-meds {
  padding: 1rem;
  text-align: center;
  color: #777;
  font-style: italic;
  background-color: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
}
</style>
