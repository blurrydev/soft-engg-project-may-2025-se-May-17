<template>
  <div class="admin-dashboard container mt-4 p-4 rounded">
    <div v-if="alertMessage" class="alert alert-success alert-dismissible fade show mt-3" role="alert">
      {{ alertMessage }}
      <button type="button" class="btn-close" @click="alertMessage = ''" aria-label="Close"></button>
    </div>

    <!-- Header Section -->
    <div class="dashboard-header d-flex justify-content-between align-items-start mb-4">
       <div class="greeting">
        <p class="mb-0">Today</p>
        <p class="fw-bold">{{ currentDate }}</p>
        <h3>Greetings Admin,</h3>
        <br />
        <h3 class="mt-3 fw-semibold">Medicine Requests</h3>
      </div>

       <div class="search-section">
        <!-- Search Input -->
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
      class="list-group-item py-2 px-3"
    >
      <strong>{{ med.title }}</strong>: {{ med.description }}
    </li>
  </ul>
</div>

<!-- Show this if search is done and nothing was found -->
<div v-else-if="searchQuery && !isSearching" class="search-results mt-3">
  <p class="text-muted fst-italic"><b>No medicines found in the database.</b></p>
</div>

<!-- Optional: show loading indicator -->
<div v-else-if="isSearching" class="search-results mt-3">
  <p class="text-info">Searching...</p>
</div>


        <!-- Add Button -->
        <button class="btn btn-lg btn-outline-primary w-100 add-button mt-3" @click="showModal = true">
          <i class="fa-solid fa-plus"></i> Add medicine
        </button>
      </div>
    </div>

    <!-- Requests Table Header -->
    <div class="grid-header">
      <div>Image</div>
      <div>Name of Medicine</div>
      <div>Dosage</div>
      <div>User</div>
      <div>Actions</div>
    </div>

    <!-- Requests List -->
    <div
      v-for="(request, index) in requests"
      :key="index"
      :class="['request-row mb-3 p-3 rounded shadow-sm', request.colorClass]"
    >
      <div class="grid-row">
        <div><i class="fa-solid fa-pills text-danger"></i></div>
        <div class="fw-bold">{{ request.medicine }}</div>
        <div>{{ request.dosage }}</div>
        <div>{{ request.user }}</div>
        <div>
          <button class="btn-approve me-2" @click="approveRequest(index)">APPROVE</button>
          <button class="btn-reject" @click="rejectRequest(index)">REJECT</button>
        </div>
      </div>
    </div>

    <!-- Modal for Adding Medicine -->
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
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { searchMedicines } from '@/services/mockApi'

const currentDate = new Date().toDateString()
const alertMessage = ref('')
const showModal = ref(false)
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)

const newMedicine = ref({
  title: '',
  description: '',
  dosage: '',
  time: ''
})

const requests = ref([
  { user: 'Alice', medicine: 'Paracetamol', dosage: '10mg', colorClass: 'bg-light-yellow' },
  { user: 'Bob', medicine: 'Ibuprofen', dosage: '20mg', colorClass: 'bg-light-yellow' },
  { user: 'Charlie', medicine: 'Amoxicillin', dosage: '10mg', colorClass: 'bg-light-yellow' }
])

const isFormValid = computed(() => {
  return newMedicine.value.title.trim() !== '' &&
    newMedicine.value.description.trim() !== '' &&
    newMedicine.value.dosage > 0;
})

function approveRequest(index) {
  const approvedMed = requests.value[index].medicine
  requests.value.splice(index, 1)
  alertMessage.value = `${approvedMed} approved successfully!`
}

function rejectRequest(index) {
  const rejectedMed = requests.value[index].medicine
  requests.value.splice(index, 1)
  alertMessage.value = `${rejectedMed} rejected and removed from requests.`
}

function submitMedicine() {
  if (!newMedicine.value.title) return
  alertMessage.value = `Medicine "${newMedicine.value.title}" added successfully!`
  newMedicine.value = { title: '', description: '', dosage: '', time: '' }
  showModal.value = false
}

async function handleSearch() {
  isSearching.value = true
  try {
    const results = await searchMedicines(searchQuery.value)
    searchResults.value = results
  } catch (error) {
    console.error('Error searching medicines:', error)
  } finally {
    isSearching.value = false
  }
}

watch(searchQuery, () => {
  handleSearch()
})
</script>

<style scoped>
.admin-dashboard {
  background-color: #d6eed6;
  border-radius: 20px;
  font-family: 'Times New Roman', serif;
}

.greeting {
  font-size: 20px;
}

.dashboard-header {
  gap: 2rem;
}

.search-section {
  width: 320px;
}

.search-input {
  font-size: 18px;
  border-radius: 8px;
}

.search-results {
  background-color: #f9f9f9;
  border-radius: 10px;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.08);
}

.result-card {
  padding: 10px 15px;
  background-color: #ffffff;
  border: 1px solid #dedede;
  border-radius: 8px;
  margin-bottom: 10px;
  transition: box-shadow 0.2s ease;
}

.result-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.grid-header {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 2fr 2fr;
  font-weight: bold;
  padding: 0.5rem 1rem;
  background-color: #d9a8f9;
  border-radius: 8px 8px 0 0;
  border-bottom: 2px solid #ddd;
  font-size: 20px;
}

.grid-row {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 2fr 2fr;
  align-items: center;
  gap: 1rem;
  font-size: 20px;
  background-color: #fffacd;
}

.bg-light-yellow {
  background-color: #fffacd;
}

.btn-approve {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-reject {
  background-color: red;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-box {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
}
</style>
