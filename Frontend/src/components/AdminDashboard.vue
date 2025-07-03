<template>
  <div class="admin-dashboard container mt-4 p-4 rounded">

    <div class="dashboard-header d-flex justify-content-between align-items-start mb-4">
      <div class="greeting">
        <p class="mb-0">Today</p>
        <p class="fw-bold">{{ currentDate }}</p>
        <h3>Greetings Admin,</h3>
        <br />
        <h3 class="mt-3 fw-semibold">Medicine Requests</h3>
      </div>


      <div class="search-section">
              <button class="logout-button" @click="logout">Logout</button>
              <br><br>

        <input
          type="text"
          class="form-control form-control-sm search-input"
          placeholder="Search medicines"
          v-model="searchQuery"
        />


        <div v-if="searchResults.length > 0" class="search-results mt-3">
          <p class="fw-semibold mb-2">Existing Medicines:</p>
          <ul class="list-group mb-2">
            <li v-for="(med, index) in searchResults" :key="index" class="list-group-item py-2 px-3 search-result-item">
                        <div style="background-color: #fffde7; width: 100%">
            {{ med.title }}</div>
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
      :class="['request-row mb-3 p-3 rounded shadow-sm', request.colorClass]">
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
  </div>
  <!-- Toast Notification -->
<div v-if="showToast" class="toast-notification">
  {{ alertMessage }}
</div>

</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router';

import { 
  searchMasterMedicineList, 
  addMedicineToMemory
} from '@/services/mockApi'
const showToast = ref(false)

function triggerToast(message) {
  alertMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const router = useRouter();

function logout() {
  sessionStorage.clear();
  router.push('/login');
}

const currentDate = new Date().toDateString()
const showModal = ref(false)
const alertMessage = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)

const newMedicine = ref({
  title: '',
  description: '',
  dosage: '',
})

const requests = ref([
  { user: 'Alice', medicine: 'Paracetamol', description: 'Pain relief', dosage: '10mg', colorClass: 'bg-light-yellow' },
  { user: 'Bob', medicine: 'Ibuprofen', description: 'Anti-inflammatory', dosage: '20mg', colorClass: 'bg-light-yellow' },
  { user: 'Charlie', medicine: 'Amoxicillin', description: 'Antibiotic', dosage: '10mg', colorClass: 'bg-light-yellow' }
]);

const isFormValid = computed(() =>
  newMedicine.value.title.trim() &&
  newMedicine.value.description.trim() &&
  newMedicine.value.dosage > 0
)

async function approveRequest(index) {
  const approved = requests.value[index];
  requests.value.splice(index, 1);
  triggerToast(`${approved.medicine} has been approved.`);

  await addMedicineToMemory(
    approved.medicine,
    `${approved.description}`
  );
}

function rejectRequest(index) {
  const rejected = requests.value[index];
  requests.value.splice(index, 1);
  triggerToast(`${rejected.medicine} has been rejected.`);
}

async function submitMedicine() {
  if (!newMedicine.value.title) return;

  alertMessage.value = `Medicine "${newMedicine.value.title}" added successfully!`;

  await addMedicineToMemory(newMedicine.value.title, newMedicine.value.description);

  newMedicine.value = { title: '', description: '', dosage: '', time: '' };
  showModal.value = false;
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
.admin-dashboard {
  background-color: #eaf5e9;
  border-radius: 20px;
  font-family: 'Serif', Georgia, Times, 'Times New Roman';
}
.dashboard-header {
  gap: 2rem;
}
.greeting {
  font-size: 20px;
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end; /* Aligns Navbar to the right */
  gap: 1rem; /* Creates space between navbar and search box */
}

/* This targets the Navbar component specifically inside this new container */
.header-actions .navbar-container {
  width: 100%;
  justify-content: flex-end; /* Pushes icons to the right end of the navbar */
}
.search-section {
  width: 320px;
}

.search-input {
  font-size: 18px;
  border-radius: 8px;
}
.search-results {
  background-color: #e1bee7;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 0 10px white;
  border-left: 5px solid #e1bee7; 
  border-right: 5px solid #e1bee7; 
  margin-bottom: 8px;
}
.grid-header,
.grid-row {
  display: grid;
  grid-template-columns: 1fr 2fr 2fr 1fr 1fr 2fr;
  align-items: center;
  gap: 1rem;
  font-size: 20px;
}
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.grid-header{
    padding: 0.5rem 1rem;
    background-color: #e1bee7;
    border-radius: 8px 8px 0 0;
  border-bottom: 2px solid #ddd;
  font-weight:bold
}

.bg-light-yellow {
  background-color: #fffde7;
  border: 2px solid #fbc02d;
  border-radius: 25px;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
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
.search-result-item{
  background-color: #fffde7 !important;
  padding: 10px;
  border: none;
  border-radius: 0;
  margin-bottom: 8px;
  width: 100%;
}
.toast-notification {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  border-radius: 10px;
  font-size: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  transition: opacity 0.3s ease-in-out;
  white-space: nowrap;
}

</style>
