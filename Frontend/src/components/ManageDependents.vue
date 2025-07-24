import apiService from '@/services/apiService';
<template>
  <header class="dashboard-header">
    <div class="greeting"></div>
    <Navbar />
  </header>

  <div class="page-container">
    <h1>Member Details</h1>

    <div class="members-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading">Loading members...</div>

      <!-- Member Cards Grid -->
      <div v-else-if="filteredDependents.length > 0" class="members-grid">
        <div
          v-for="dep in filteredDependents"
          :key="dep.id"
          class="member-card"
          :style="{ backgroundColor: getCardColor(dep.gender) }"
          @click="viewProfile(dep)"
        >
          <div class="card-header">
            <span class="member-name">{{ dep.firstName }}</span>
            <span class="edit-icon">✎</span>
          </div>
          <div class="member-icon">
            <svg
              v-if="dep.gender === 'female'"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 288 512"
              fill="currentColor"
            >
              <path
                d="M144 0a80 80 0 1 1 0 160A80 80 0 1 1 144 0zM96 192c-35.3 0-64 28.7-64 64V448c0 17.7 14.3 32 32 32s32-14.3 32-32V384h64v64c0 17.7 14.3 32 32 32s32-14.3 32-32V256c0-35.3-28.7-64-64-64H96z"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 320 512"
              fill="currentColor"
            >
              <path
                d="M160 0a80 80 0 1 1 0 160A80 80 0 1 1 160 0zM56 192c-33.1 0-60.3 25.5-63.8 57.9l-2.4 23.3C-14.5 306.9 1.7 344.4 29.3 365.2l2.3 1.7c29.1 21.6 68.3 21.6 97.4 0l2.3-1.7c27.6-20.8 43.8-58.3 29.1-89.1l-2.4-23.3C176.3 217.5 149.1 192 116 192H56zM232 256c-13.3 0-24 10.7-24 24V448c0 17.7 14.3 32 32 32s32-14.3 32-32V280c0-13.3-10.7-24-24-24z"
              />
            </svg>
          </div>
          <button class="delete-btn" @click.stop="handleDelete(dep.id)">
            Delete Profile
          </button>
        </div>
      </div>

      <!-- No Dependents Message -->
      <div v-if="!isLoading && filteredDependents.length === 0" class="empty-state">
        <p>No members found. Please add one.</p>
      </div>

      <!-- Add Member Button -->
      <div class="add-button-container">
        <button class="add-member-btn" @click="openAddModal">Add a member</button>
      </div>
    </div>

    <!-- Add Modal (unchanged) -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content">
        <h2>Add a New Dependent</h2>
        <p>Search for a user by name or username and select them to add.</p>
        <div class="search-container">
          <input type="text" v-model="searchQuery" placeholder="Enter username or name..." @input="handleSearch" />
          <div v-if="isSearching" class="search-loading">Searching...</div>
        </div>
        <ul v-if="searchResults.length > 0" class="search-results">
          <li
            v-for="user in searchResults"
            :key="user.id"
            @click="selectUser(user)"
            :class="{ selected: selectedNewDependent && selectedNewDependent.id === user.id }"
          >
            {{ user.firstName }} {{ user.lastName }} ({{ user.username }})
          </li>
        </ul>
        <div v-if="searchAttempted && searchResults.length === 0 && !isSearching" class="no-results">
          No users found.
        </div>
        <div class="modal-actions">
          <button class="modal-btn-cancel" @click="closeAddModal">Cancel</button>
          <button class="modal-btn-confirm" @click="handleAddDependent" :disabled="!selectedNewDependent">Request Dependent</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Navbar from './Navbar.vue';
import apiService from '@/services/apiService';
// import {
//   getDependentsList,
//   deleteDependent as apiDeleteDependent,
//   searchAllUsers,
//   addDependent as apiAddDependent
// } from '../services/mockApi.js';

const router = useRouter();
const dependents = ref([]);
const isLoading = ref(true);
const showAddModal = ref(false);

const searchQuery = ref('');
const searchResults = ref([]);
const selectedNewDependent = ref(null);
const isSearching = ref(false);
const searchAttempted = ref(false);

// ✅ Filter only senior citizens
const filteredDependents = computed(() =>
  dependents.value.filter(dep => dep.role === 'senior_citizen')
);

async function fetchDependents() {
  isLoading.value = true;
  try {
    const res = await apiService.get('/sc/my-dependents');
    const data = res.data;
    console.log("DEPENDENTS FROM API:", data);
    dependents.value = Array.isArray(data.dependents) ? data.dependents : [];
    console.log("Fetched dependents:", dependents.value);
  } catch (err) {
    console.error('Error fetching dependents:', err);
    dependents.value = []; // Safeguard: ensure it's always an array
  } finally {
    isLoading.value = false;
  }
}

// async function getDependentsList() {
//   try {
//     const res = await apiService.get('/sc/my-dependents');
//     return Array.isArray(res.data.dependents) ? res.data.dependents : [];
//   } catch (err) {
//     console.error('API error getting dependents:', err);
//     return [];
//   }
// }


async function apiAddDependent(userToAdd) {
  try {
    const res = await apiService.post('/sc/request-senior', {
      senior_id: userToAdd.id,
    });
    
    const data = res.data;
    if (!data.success) {
      return {
        success: false,
        message: data.message || 'Failed to add dependent.'
      };
    }
    console.log('✅ Dependent added successfully:', data.dependent);
    return {
      success: true,
      dependent: data.dependent
    };

  } catch (err) {
    console.error('❌ Error adding dependent:', err.message);
    return {
      success: false,
      message: err.message
    };
  }
}


async function apiDeleteDependent(seniorId) {
  try {
    const res = await apiService.delete('/sc/delete-dependent', {
      data: { senior_id: seniorId } // required syntax for axios.delete body
    });

    const data = res.data;
    console.log("✅ Dependent removed:", data);
  } catch (err) {
    console.error('❌ Error deleting dependent:', err.message);
  }
}


async function searchAllUsers(query) {
  if (!query) return [];

  try {
    const res = await apiService.get(`/sc/search-users?query=${encodeURIComponent(query)}`);
    const data = res.data; // ✅ Axios response data

    console.log('[API] /search-users →', data);
    return data.users;
  } catch (err) {
    // ✅ Log backend error message
    console.error('Error searching users:', err.response?.data || err.message);
    return [];
  }
}



onMounted(() => {
  fetchDependents();
});

function getCardColor(gender) {
  return gender === 'female' ? '#E8D2E8' : '#D2D9E8';
}

function viewProfile(dependent) {
  router.push({ name: 'DependentProfile', params: { userId: dependent.id } });
}

async function handleDelete(userId) {
  if (confirm('Are you sure you want to delete this profile?')) {
    await apiDeleteDependent(userId);
    await fetchDependents();
  }
}

function openAddModal() {
  showAddModal.value = true;
}

function closeAddModal() {
  showAddModal.value = false;
  searchQuery.value = '';
  searchResults.value = [];
  selectedNewDependent.value = null;
  isSearching.value = false;
  searchAttempted.value = false;
}

let searchTimeout;
function handleSearch() {
  clearTimeout(searchTimeout);
  isSearching.value = true;
  searchAttempted.value = true;
  searchTimeout = setTimeout(async () => {
    searchResults.value = await searchAllUsers(searchQuery.value);
    isSearching.value = false;
  }, 300);
}

function selectUser(user) {
  selectedNewDependent.value = user;
}
async function handleAddDependent() {
  if (!selectedNewDependent.value) return;
  const response = await apiAddDependent(selectedNewDependent.value);
  if (response.success) {
    closeAddModal();
    await fetchDependents();
  } else {
    alert(response.message || 'Failed to add dependent.');
    closeAddModal();
  }
}
</script>

<style scoped>
.page-container {
  background-color: #eaf5e9;
  font-family: "Times New Roman", serif;
  min-height: calc(100vh - 58px);
  padding: 2.5rem 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h1 {
  font-family: 'Georgia', serif;
  font-weight: 500;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #333;
}

.members-container {
  background-color: #f7fbf6;
  border-radius: 20px;
  padding: 2rem 2.5rem;
  width: 100%;
  max-width: 1100px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  border: 1px solid #5a8a52;
}

.loading, .empty-state {
  text-align: center;
  padding: 4rem;
  color: #666;
  font-size: 1.2rem;
  font-style: italic;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 2rem;
}

.member-card {
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 20px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: none;
  background: linear-gradient(135deg, #247890, #6aa7cd);
}

.member-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.12);
}

.card-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.member-name {
  font-size: 1.5rem;
  font-weight: bold;
  font-family: 'Georgia', serif;
  color: #333;
}

.edit-icon {
  font-size: 1.2rem;
  color: #825858;
  transition: color 0.2s;
}

.member-card:hover .edit-icon {
  color: #333;
}

.member-icon {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 1rem auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.member-icon svg {
  width: 50%;
  height: 50%;
  color: white;
}

.member-card[style*="rgb(232, 210, 232)"] {
  background: linear-gradient(135deg, #fef6ff, #f7e9f7);
}
.member-card[style*="rgb(210, 217, 232)"] {
  background: linear-gradient(135deg, #f0f7ff, #e4f1fb);
}

.delete-btn {
  background-color: transparent;
  color: #e74c3c;
  border: 1px solid #f5b7b1;
  padding: 8px 16px;
  border-radius: 50px;
  cursor: pointer;
  margin-top: 1.5rem;
  font-weight: bold;
  transition: all 0.2s;
}
.delete-btn:hover {
  background-color: #e74c3c;
  color: white;
  border-color: #e74c3c;
}

.add-button-container {
  display: flex;
  justify-content: center;
  margin-top: 2.5rem;
  border-top: 1px solid #e0e0e0;
  padding-top: 2.5rem;
}

.add-member-btn {
  background: linear-gradient(45deg, #28a745, #2ecc71);
  color: white;
  border: none;
  padding: 12px 28px;
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(46, 204, 113, 0.4);
  transition: all 0.2s;
}
.add-member-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(46, 204, 113, 0.5);
}

/* Modal styles remain unchanged */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 10px; width: 90%; max-width: 500px; }
.search-container input { width: 100%; padding: 10px; font-size: 1rem; border: 1px solid #ccc; border-radius: 5px; }
.search-loading { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #888; }
.search-results { list-style: none; padding: 0; margin: 0; max-height: 200px; overflow-y: auto; border: 1px solid #ddd; border-radius: 5px; }
.search-results li { padding: 10px; cursor: pointer; border-bottom: 1px solid #eee; }
.search-results li:last-child { border-bottom: none; }
.search-results li:hover { background-color: #f0f0f0; }
.search-results li.selected { background-color: #007bff; color: white; }
.no-results { padding: 10px; color: #777; text-align: center; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
.modal-btn-cancel, .modal-btn-confirm { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; }
.modal-btn-cancel { background-color: #6c757d; color: white; }
.modal-btn-confirm { background-color: #28a745; color: white; }
.modal-btn-confirm:disabled { background-color: #aaa; cursor: not-allowed; }
</style>