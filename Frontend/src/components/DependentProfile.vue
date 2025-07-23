<template>
  <div class="page-container">
    <div v-if="isLoading" class="loading">Loading Profile...</div>
    <div v-else-if="!dependent" class="loading">Profile not found.</div>

    <div v-else class="profile-container">
      <header class="dashboard-header">
        <Navbar />
      </header>

      <h1>{{ dependent.firstName }}'s Profile</h1>

      <!-- User Details -->
      <div class="user-details-grid">
        <div class="detail-item">
          <label>Name</label>
          <input type="text" :value="`${dependent.firstName} ${dependent.lastName}`" readonly />
        </div>
      </div>

      <!-- Daytime Meds -->
      <div class="meds-section">
        <div class="meds-header">
          <span><i class="icon-sun"></i> Daytime Meds</span>
          <button class="add-medicine-btn" @click="openAddMedModal">Add a medicine</button>
        </div>
        <div v-if="daytimeMeds.length === 0" class="no-meds">No daytime medicines scheduled.</div>
        <div v-else>
          <div v-for="med in daytimeMeds" :key="med.id" class="med-row daytime">
            <i class="icon-pill" />
            <span class="med-name">{{ med.medicineTitle }}</span>
            <span class="med-dosage">{{ med.dosage }}</span>
            <span class="med-time"><i class="icon-clock" /> {{ formatTime(med) }}</span>
            <span class="icon-trash" @click="openDeleteModal(med.id)" />
          </div>
        </div>
      </div>

      <!-- Nighttime Meds -->
      <div class="meds-section">
        <div class="meds-header">
          <span><i class="icon-moon"></i> Nighttime Meds</span>
        </div>
        <div v-if="nighttimeMeds.length === 0" class="no-meds">No nighttime medicines scheduled.</div>
        <div v-else>
          <div v-for="med in nighttimeMeds" :key="med.id" class="med-row nighttime">
            <i class="icon-pill" />
            <span class="med-name">{{ med.medicineTitle }}</span>
            <span class="med-dosage">{{ med.dosage }}</span>
            <span class="med-time"><i class="icon-clock" /> {{ formatTime(med) }}</span>
            <span class="icon-trash" @click="openDeleteModal(med.id)" />
          </div>
        </div>
      </div>
    </div>

    <!-- Add Medicine Modal -->
    <AddMedicineModal
      v-if="showAddMedModal"
      @close="closeAddMedModal"
      @add-medication="handleAddMedication"
    />

    <!-- ✅ Confirm Delete Modal -->
    <ConfirmModal
      v-if="showDeleteModal"
      message="Are you sure you want to delete this medication from the schedule?"
      @confirm="handleDeleteConfirmed"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AddMedicineModal from './AddMedicineModal.vue'
import ConfirmModal from './ConfirmModal.vue'
import Navbar from './Navbar.vue'
import apiService from '@/services/apiService'

const route = useRoute()
const userId = route.params.userId

const isLoading = ref(true)
const dependent = ref(null)
const medications = ref([])
const showAddMedModal = ref(false)

const showDeleteModal = ref(false)
const medToDelete = ref(null)

const daytimeMeds = computed(() =>
  medications.value.filter(
    med =>
      med.breakfast_before ||
      med.breakfast_after ||
      med.lunch_before ||
      med.lunch_after
  )
)

const nighttimeMeds = computed(() =>
  medications.value.filter(
    med => med.dinner_before || med.dinner_after
  )
)

const formatTime = (med) => {
  const slots = []
  if (med.breakfast_before) slots.push('Before Breakfast')
  if (med.breakfast_after) slots.push('After Breakfast')
  if (med.lunch_before) slots.push('Before Lunch')
  if (med.lunch_after) slots.push('After Lunch')
  if (med.dinner_before) slots.push('Before Dinner')
  if (med.dinner_after) slots.push('After Dinner')
  return slots.join(', ')
}

async function getDependentDetails(id) {
  try {
    const res = await apiService.get(`/sc/dependent/${id}/details`)
    return res.data
  } catch (err) {
    console.error('Error fetching dependent details:', err)
    return null
  }
}

async function getDependentMedications(id) {
  try {
    const res = await apiService.get(`/sc/dependent/${id}/medications`)
    return res.data.medications || []
  } catch (err) {
    console.error('Error fetching medications:', err)
    return []
  }
}

async function deleteMedicationMapping(medId) {
  try {
    const res = await apiService.delete(`/sc/medication/${medId}`)
    return res.data
  } catch (err) {
    console.error('Error deleting medication:', err)
    return { success: false }
  }
}

async function addMedicationToDependent(dependentId, payload) {
  try {
    const res = await apiService.post(
      `/sc/dependent/${dependentId}/add-medication`,
      payload
    )
    return res.data.medication
  } catch (err) {
    console.error('Error adding medication:', err)
    return null
  }
}

function openAddMedModal() {
  showAddMedModal.value = true
}

function closeAddMedModal() {
  showAddMedModal.value = false
}

function openDeleteModal(medId) {
  medToDelete.value = medId
  showDeleteModal.value = true
}

async function handleDeleteConfirmed() {
  if (!medToDelete.value) return

  const result = await deleteMedicationMapping(medToDelete.value)
  if (result.success || result.message) {
    medications.value = medications.value.filter(m => m.id !== medToDelete.value)
  } else {
    alert('Failed to delete medication.')
  }

  showDeleteModal.value = false
  medToDelete.value = null
}

async function handleAddMedication(payload) {
  const newMed = await addMedicationToDependent(userId, payload)
  if (newMed) {
    medications.value.push(newMed)
    closeAddMedModal()
  } else {
    alert('Failed to add medication.')
  }
}

onMounted(async () => {
  const [details, meds] = await Promise.all([
    getDependentDetails(userId),
    getDependentMedications(userId),
  ])
  dependent.value = details
  medications.value = meds
  isLoading.value = false
})
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
