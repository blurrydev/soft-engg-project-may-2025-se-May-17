<template>
  <div class="dashboard-wrapper">
    <div class="header-wrapper">
      <header class="dashboard-header">
        <Navbar />
      </header>

      <div class="left-section">
        <div class="greeting">
          <h2 class="text-muted small mb-1">{{ formattedDate }}</h2>
          <h2 class="fw-semibold mb-1">Greetings, Admin</h2>
          <h5 class="text-muted mt-1">Medicine Requests</h5>
        </div>
      </div>

      <div class="search-section">
        <input
          type="text"
          class="form-control form-control-sm search-input"
          placeholder="Search medicines"
          v-model="searchQuery"
        />

        <!-- Search Results -->
        <div v-if="searchResults.length > 0" class="search-results mt-3">
          <p class="fw-semibold mb-2">Existing Medicines:</p>
          <ul class="list-group mb-2">
            <li
              v-for="(med, index) in searchResults"
              :key="index"
              class="list-group-item py-2 px-3 search-result-item"
            >
              <div style="background-color: #fffde7; width: 100%">
                {{ med.title }}
              </div>
            </li>
          </ul>
        </div>

        <div v-else-if="searchQuery && !isSearching" class="search-results mt-3">
          <p class="text-muted fst-italic"><b>No medicines found in the database.</b></p>
        </div>

        <div v-else-if="isSearching" class="search-results mt-3">
          <p class="text lg fst-italic">Searching...</p>
        </div>

        <button class="btn btn-lg btn-outline-primary w-100 add-button mt-3" @click="showModal = true">
          <i class="fa-solid fa-plus"></i> Add medicine
        </button>
      </div>
    </div>

    <div class="grid-header">
      <div>Image</div>
      <div>Name of Medicine</div>
      <div>Description</div>
      <div>Dosage</div>
      <div>User</div>
      <div>Actions</div>
    </div>

    <div
      v-for="(request, index) in requests"
      :key="index"
      :class="['request-row mb-3 p-3 rounded shadow-sm', request.colorClass]"
    >
      <div class="grid-row">
        <div><i class="fa-solid fa-pills text-danger"></i></div>
        <div class="fw-bold">{{ request.medicine }}</div>
        <div>{{ request.description }}</div>
        <div>{{ request.dosage }}</div>
        <div>{{ request.user }}</div>
        <div class="action-buttons">
          <button class="btn-approve me-2" @click="approveRequest(index)">APPROVE</button>
          <button class="btn-reject" @click="rejectRequest(index)">REJECT</button>
        </div>
      </div>
    </div>

    <div class="modal-backdrop" v-if="showModal">
      <div class="modal-box">
        <h5 class="mb-3">Add New Medicine</h5>

        <div class="mb-2">
          <input
            type="text"
            v-model.trim="newMedicine.title"
            class="form-control"
            placeholder="Medicine Title"
            required
          />
        </div>
        <div class="mb-2">
          <textarea
            v-model.trim="newMedicine.description"
            class="form-control"
            placeholder="Description"
            rows="3"
            required
          ></textarea>
        </div>
        <div class="mb-2">
          <input
            type="number"
            v-model.number="newMedicine.dosage"
            class="form-control"
            placeholder="Dosage (e.g. 10)"
            min="1"
            required
          />
        </div>
        <div class="text-end">
          <button class="btn btn-secondary me-2" @click="showModal = false">Cancel</button>
          <button class="btn btn-success" :disabled="!isFormValid" @click="submitMedicine">Add</button>
        </div>
      </div>
    </div>

    <div v-if="showToast" class="toast-notification">
      {{ alertMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Navbar from './Navbar.vue'
import {
  searchMasterMedicineList,
  addMedicineToMemory
} from '@/services/mockApi'

const showToast = ref(false)
const alertMessage = ref('')
const currentDate = new Date()
const formattedDate = currentDate.toLocaleDateString('en-US', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric'
})

const showModal = ref(false)
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)

const newMedicine = ref({
  title: '',
  description: '',
  dosage: ''
})

const requests = ref([
  { user: 'Alice', medicine: 'Paracetamol', description: 'Pain relief', dosage: '10mg', colorClass: 'bg-light-yellow' },
  { user: 'Bob', medicine: 'Ibuprofen', description: 'Anti-inflammatory', dosage: '20mg', colorClass: 'bg-light-yellow' },
  { user: 'Charlie', medicine: 'Amoxicillin', description: 'Antibiotic', dosage: '10mg', colorClass: 'bg-light-yellow' }
])

const isFormValid = computed(() =>
  newMedicine.value.title.trim() &&
  newMedicine.value.description.trim() &&
  newMedicine.value.dosage > 0
)

function triggerToast(message) {
  alertMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

async function approveRequest(index) {
  const approved = requests.value[index]
  requests.value.splice(index, 1)
  triggerToast(`${approved.medicine} has been approved.`)

  await addMedicineToMemory(
    approved.medicine,
    `${approved.description}`
  )
}

function rejectRequest(index) {
  const rejected = requests.value[index]
  requests.value.splice(index, 1)
  triggerToast(`${rejected.medicine} has been rejected.`)
}

async function submitMedicine() {
  if (!newMedicine.value.title) return

  alertMessage.value = `Medicine "${newMedicine.value.title}" added successfully!`

  await addMedicineToMemory(newMedicine.value.title, newMedicine.value.description)

  newMedicine.value = { title: '', description: '', dosage: '' }
  showModal.value = false
}

async function handleSearch() {
  isSearching.value = true
  try {
    const results = await searchMasterMedicineList(searchQuery.value)
    searchResults.value = Array.isArray(results) ? results : []
  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

watch(searchQuery, () => {
  handleSearch()
})
</script>

<style scoped>
.dashboard-wrapper {
  background-color: #f0f8f1;
  min-height: 100vh;
  font-family: "Times New Roman", serif;
  padding: 0;
}

.header-wrapper {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 2rem 3rem;
  flex-wrap: wrap;
  background-color: #f0f8f1;
}

.left-section {
  flex: 1 1 60%;
  max-width: 60%;
}

.greeting p,
.greeting h2,
.greeting h5 {
  margin: 0;
}

.search-section {
  flex: 1 1 300px;
  max-width: 300px;
  background-color: white;
  padding: 1.5rem;
  border-radius: 18px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  margin-top: 1rem;
}

.search-input {
  border-radius: 12px;
  border: 1px solid #ccc;
}

.logout-button {
  background-color: #00838f;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: bold;
  width: 100%;
  margin-bottom: 1rem;
}

.add-button {
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  padding: 10px;
}

.search-result-item {
  background-color: #fffde7;
  border-left: 5px solid #ffcc00;
  border-radius: 8px;
  font-size: 0.95rem;
}

.grid-header {
  display: grid;
  grid-template-columns: 1fr 2fr 3fr 1fr 1fr 2fr;
  font-weight: bold;
  background-color: #d0f0e0;
  padding: 0.8rem 2rem;
  border-radius: 12px;
  margin: 1rem 3rem;
  font-size: 0.95rem;
  color: #333;
}

.grid-row {
  display: grid;
  grid-template-columns: 1fr 2fr 3fr 1fr 1fr 2fr;
  align-items: center;
  gap: 0.5rem;
}

.request-row {
  background-color: #fef9e7;
  border-left: 6px solid #f9a825;
  border-radius: 16px;
  padding: 1rem;
  font-size: 0.95rem;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
  margin: 0 3rem;
}

.bg-light-yellow {
  background-color: #fffde7 !important;
}

.btn-approve {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
}

.btn-reject {
  background-color: #e53935;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-box {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 16px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.toast-notification {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  background-color: #00c853;
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 12px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 999;
}
</style>
