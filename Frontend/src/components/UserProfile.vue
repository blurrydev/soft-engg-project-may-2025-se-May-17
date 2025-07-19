<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <Navbar />
    </header>

    <main class="main-content">
      <div class="profile-container">
        <h1 class="profile-title">My Profile</h1>
        <div class="profile-details">
          <div class="info-row">
            <span class="label">Full Name :</span>
            <span class="value">{{ user.firstName }} {{ user.lastName }}</span>
          </div>
          <div class="info-row">
            <span class="label">Username :</span>
            <span class="value">{{ user.username }}</span>
          </div>
          <!-- Medicine Info -->
          <div v-if="user.role === 'senior_citizen' && medicines.length>0">
          <h3 class="section-title">My Medicines</h3>

          <!-- Table header row -->
          <div class="medicine-section medicine-row">
              <span class="label">Medicine Name</span>
              <span class="label">Dosage</span>
              <span class="label">⏰ Time</span>
          </div>

          <!-- One row per medicine -->
          <div v-for="(m, index) in medicines" :key="index" class="medicine-row">
              <span class="value">💊{{ m.title }}</span>
              <span class="value">{{ m.dosage }}</span>
              <span class="value">{{ m.assigned_slots.join(", ") }}</span>
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
          </div>
          <!-- Dependents Information -->
          <div v-if="user.role === 'care_giver' && dependents.length>0">
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
        </div>
      </div>
    </div>
  </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from './Navbar.vue'
import { useRouter } from 'vue-router'
import {jwtDecode} from 'jwt-decode'

const user = ref({})
const caregiver = ref(null)
const dependents = ref([])
const medicines = ref([])

const userId = sessionStorage.getItem('user_id')
const role = sessionStorage.getItem('role')
const router = useRouter()

onMounted(async () => {
  if (!userId || !role) {
    router.push('/login') // redirect if not logged in
    return
  }
  const token = sessionStorage.getItem('accesstoken')  // adjust key name if needed
  if (token) {
    const decoded = jwtDecode(token)
    user.value = {
      id: decoded.id,
      firstName: decoded.first_name,
      lastName: decoded.last_name,
      username: decoded.username,
      role:role
    }}
   if (role === 'senior_citizen') {
      try {
        const res = await fetch('http://localhost:5000/sc/my-medicines', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        if (!res.ok) throw new Error('Failed to fetch medicines')
        const data = await res.json()
        medicines.value = data.medicines
      } catch (err) {
        console.error('Error fetching medicines:', err)
      }
    }
    if (role === 'senior_citizen') {
    try {
      const caregiverRes = await fetch('http://localhost:5000/sc/my-caregiver', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      if (!caregiverRes.ok) throw new Error('Failed to fetch caregiver')
      const caregiverData = await caregiverRes.json()
      caregiver.value = caregiverData.caregiver  // will be null if not assigned
    } catch (err) {
      console.error('Error fetching caregiver:', err)
    }
}
    if (role === 'care_giver') {
  try {
    const res = await fetch('http://localhost:5000/sc/my-dependents', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    if (!res.ok) throw new Error('Failed to fetch dependents');
    const data = await res.json();
    console.log("DEPENDENTS FROM API:", data);
    dependents.value = data.dependents;
  } catch (err) {
    console.error('Error fetching dependents:', err);
  }
}


})
</script>

<style scoped>
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
