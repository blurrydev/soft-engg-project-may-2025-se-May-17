<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <Navbar />
    </header>
    <main class="main-content">
      <div class="profile-container">
        <h1 class="profile-title">Senior Citizen Profile</h1>

        <!-- Profile for dep_001 -->
        <div class="profile-details" v-if="idFromUrl === 'dep_001'">
          <div class="info-row">
            <span class="label">Full Name :</span>
            <span class="value">Eleanor Vance</span>
          </div>
          <div class="info-row">
            <span class="label">Username :</span>
            <span class="value">Eleanor1505</span>
          </div>
          <div class="info-row">
            <span class="label">User ID :</span>
            <span class="value">dep_001</span>
          </div>
          <div class="info-row">
            <span class="label">Birth Date :</span>
            <span class="value">1958-05-15</span>
          </div>

          <div>
            <h3 class="section-title">My Medicines</h3>
            <div class="medicine-section medicine-row">
              <span class="label">Medicine Name</span>
              <span class="label">Dosage</span>
              <span class="label">⏰ Time</span>
            </div>
            <div class="medicine-row">
              <span class="value">💊Lisinopril</span>
              <span class="value">10 mg</span>
              <span class="value">breakfast_after</span>
            </div>
            <div class="medicine-row">
              <span class="value">💊Albuterol</span>
              <span class="value">5 mg</span>
              <span class="value">lunch_before</span>
            </div>
            <div class="medicine-row">
              <span class="value">💊Atorvastatin</span>
              <span class="value">20 mg</span>
              <span class="value">dinner_after</span>
            </div>
          </div>

          <div>
            <h3 class="section-title">My Caregiver</h3>
            <div class="info-row">
              <span class="label">Full Name :</span>
              <span class="value">John Doe</span>
            </div>
            <div class="info-row">
              <span class="label">Username :</span>
              <span class="value">John1010</span>
            </div>
            <div class="info-row">
              <span class="label">Caregiver ID :</span>
              <span class="value">user_101</span>
            </div>
          </div>
        </div>

        <!-- Profile for dep_002 -->
        <div class="profile-details" v-else-if="idFromUrl === 'dep_002'">
          <div class="info-row">
            <span class="label">Full Name :</span>
            <span class="value">Hugh Crain</span>
          </div>
          <div class="info-row">
            <span class="label">Username :</span>
            <span class="value">Hugh2011</span>
          </div>
          <div class="info-row">
            <span class="label">User ID :</span>
            <span class="value">dep_002</span>
          </div>
          <div class="info-row">
            <span class="label">Birth Date :</span>
            <span class="value">1955-11-20</span>
          </div>

          <div>
            <h3 class="section-title">My Medicines</h3>
            <div class="medicine-section medicine-row">
              <span class="label">Medicine Name</span>
              <span class="label">Dosage</span>
              <span class="label">⏰ Time</span>
            </div>
            <div class="medicine-row">
              <span class="value">💊Metformin</span>
              <span class="value">500 mg</span>
              <span class="value">breakfast_after</span>
            </div>
            <div class="medicine-row">
              <span class="value">💊Amlodipine</span>
              <span class="value">5 mg</span>
              <span class="value">lunch_before</span>
            </div>
          </div>

          <div>
            <h3 class="section-title">My Caregiver</h3>
            <div class="info-row">
              <span class="label">Full Name :</span>
              <span class="value">John Doe</span>
            </div>
            <div class="info-row">
              <span class="label">Username :</span>
              <span class="value">John1010</span>
            </div>
            <div class="info-row">
              <span class="label">Caregiver ID :</span>
              <span class="value">user_101</span>
            </div>
          </div>
        </div>

        <!-- Optional fallback -->
        <div v-else class="profile-details">
          <p style="text-align: center; color: red; font-weight: bold;">Profile not found for ID: {{ idFromUrl }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './Navbar.vue'

// Extract ID from the URL path
const route = useRoute()
const idFromUrl = computed(() => route.path.split('/')[2])
</script>

<style scoped>
/* same CSS as before, unchanged */
:global(html, body) {
  margin: 0;
  padding: 0;
}

.dashboard-wrapper {
  background-color: #f0f8f1;
  min-height: 100vh;
  font-family: "Times New Roman", serif;
  padding: 0;
  margin: 0;
}

.main-content {
  padding: 2rem 3rem;
  display: flex;
  justify-content: center;
}

.profile-container {
  background-color: white;
  border-radius: 18px;
  padding: 2rem;
  max-width: 700px;
  width: 100%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.profile-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
}

.profile-details {
  padding: 1.5rem;
  border-radius: 8px;
}

.info-row {
  display: grid;
  grid-template-columns: 2fr 2fr;
  gap: 1rem;
  align-items: center;
  background-color: #f0f8ff;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border-radius: 6px;
  margin-left: 20%;
  margin-right: 20%;
}

.label {
  font-weight: bold;
}

.value {
  color: #555;
  text-align: center;
}

.section-title {
  font-size: 1.5rem;
  margin: 2rem 0 1rem;
  border-bottom: 2px solid #66bb6a;
  padding-bottom: 0.5rem;
}

.medicine-section {
  margin-top: 2rem;
  background-color: #f0f8ff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.medicine-row {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr;
  background-color: #f0f8ff;
  padding: 0.8rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}
</style>
