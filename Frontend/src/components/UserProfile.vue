<template>
  <div class="profile-container">
    <h1 class="profile-title">My Profile</h1>
    <div v-if="user" class="profile-details">
      <!-- Profile Information -->
      <div class="info-row">
        <span class="label">Full Name :</span>
        <span class="value">{{ user.firstName }} {{ user.lastName }}</span>
      </div>
      <div class="info-row">
        <span class="label">Username :</span>
        <span class="value">{{ user.username }}</span>
      </div>
      <div class="info-row">
        <span class="label">User ID :</span>
        <span class="value">{{ user.id }}</span>
      </div>
      <div v-if="user.role=='senior_citizen'" class="info-row">
        <span class="label">Birth Date :</span>
        <span class="value">{{ user.birthDate }}</span>
      </div>
      <br>
      <!-- Medicine Info -->
        <div v-if="user.role === 'senior_citizen' && medicines.length">
        <h3 class="section-title">My Medicines</h3>

        <!-- Table header row -->
        <div class="medicine-section medicine-row">
            <span class="label">Medicine Name</span>
            <span class="label">Dosage</span>
            <span class="label">⏰ Time</span>
        </div>

        <!-- One row per medicine -->
        <div v-for="(m, index) in medicines" :key="index" class="medicine-row">
            <span class="value">💊{{ m.name }}</span>
            <span class="value">{{ m.dosage }}</span>
            <span class="value">{{ m.timing }}</span>
        </div>
        </div>

      <!-- Caregiver Information -->
      <div v-if="user.role === 'senior_citizen' && caregiver">
        <h3 class="section-title">My Caregiver</h3>
        <div class="info-row">
          <span class="label">Full Name :</span>
          <span class="value">{{ caregiver.firstName }} {{ caregiver.lastName }}</span>
        </div>
        <div class="info-row">
          <span class="label">Username :</span>
          <span class="value">{{ caregiver.username }}</span>
        </div>
        <div class="info-row">
          <span class="label">Caregiver ID :</span>
          <span class="value">{{ caregiver.id }}</span>
        </div>
      </div>
      <br>
      <!-- Dependents Information -->
      <div v-if="user.role === 'care_giver' && dependents.length > 0">
        <h3 class="section-title">My Dependents</h3>
        <div v-for="(d, index) in dependents" :key="d.id" class="dependent-section">
          <h4 class="dependent-title">Dependent {{ index + 1 }}</h4>
          <div class="info-row">
            <span class="label">Full Name :</span>
            <span class="value">{{ d.firstName }} {{ d.lastName }}</span>
          </div>
          <div class="info-row">
            <span class="label">Username :</span>
            <span class="value">{{ d.username }}</span>
          </div>
          <div class="info-row">
            <span class="label">User ID :</span>
            <span class="value">{{ d.id }}</span>
          </div>
          <div class="info-row">
            <span class="label">Relation :</span>
            <span class="value">{{ d.relation }}</span>
        </div>
          <div class="info-row">
            <span class="label">Birth Date :</span>
            <span class="value">{{ d.birthDate }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  getUserById,
  getCaregiverForSenior,
  getDependentsForCaregiver,
  getMedicinesForUser,
} from '@/services/mockApi'

const user = ref(null)
const caregiver = ref(null)
const dependents = ref([])
const medicines = ref([])

onMounted(async () => {
  const userId = sessionStorage.getItem('user_id')
  if (!userId) return

  const fetchedUser = await getUserById(userId)
  user.value = fetchedUser

  if (fetchedUser?.role === 'senior_citizen') {
    caregiver.value = await getCaregiverForSenior(fetchedUser.id)
    medicines.value = await getMedicinesForUser(fetchedUser.id)
  } else if (fetchedUser?.role === 'care_giver') {
    dependents.value = await getDependentsForCaregiver(fetchedUser.id)
  }
})
</script>

<style scoped>
.profile-container {
  font-family: 'Segoe UI', sans-serif;
  background-color: #eaf5e9;
  padding: 2rem;
  border-radius: 8px;
  max-width: 600px;
  margin: 0 auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid #51e544;
}

.profile-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 1.5rem;
}
.profile-details {
  padding: 1.5rem;
  border-radius: 8px;
}
.info-row {
  display: grid;
  grid-template-columns: 2fr 2fr;  /* Equal columns */
  gap: 1rem;
  align-items: center;
  background-color: #f0f8ff;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border-radius: 6px;
  margin-left:20%;
  margin-right:20%
}
.label {
  font-weight: bold;
 }

.value {
  color: #555;
  text-align:center;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
}

.dependent-section {
  padding: 1.2rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: #f0f8ff;
}

.dependent-title {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #66bb6a;
}
.medicine-section {
  margin-top: 2rem;
  background-color: #f0f8ff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.medicine-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.medicine-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  padding: 0.8rem 1rem;
  border-radius: 6px;
  border-left: 5px solid #66bb6a;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.pill-icon {
  font-size: 1.4rem;
  margin-right: 1rem;
  color: #ff4081;
}

.medicine-info {
  display:flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}

.medicine-name {
  font-weight: bold;
  font-size: 1rem;
  color: #333;
}

.medicine-dose,
.medicine-timing {
  font-size: 0.95rem;
  color: #555;
}
.info-header {
  background-color: #c8e6c9;
  font-weight: bold;
  justify-content: space-between;
}
.medicine-section {
  margin-top: 2rem;
}
.medicine-row {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr; /* Flexibly aligned columns */
  background-color: #f0f8ff;
  padding: 0.8rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}
</style>