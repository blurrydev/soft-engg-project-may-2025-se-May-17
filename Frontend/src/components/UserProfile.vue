<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <Navbar />
    </header>

    <main class="main-content">
      <div class="profile-container">
        <h1 class="profile-title">Caregiver Profile</h1>
        <div class="profile-details">
          <div class="info-row">
            <span class="label">Full Name :</span>
            <span class="value">John Doe</span>
          </div>
          <div class="info-row">
            <span class="label">Username :</span>
            <span class="value">John1010</span>
          </div>
          <div class="info-row">
            <span class="label">User ID :</span>
            <span class="value">user_101</span>
          </div>

          <h3 class="section-title"><b>My Dependents</b></h3>

          <div class="dependent-section">
            <h4 class="dependent-title">Dependent 1</h4>
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
              <span class="label">Relation :</span>
              <span class="value">Mom</span>
            </div>
            <div class="info-row">
              <span class="label">Birth Date :</span>
              <span class="value">1958-05-15</span>
            </div>
          </div>

          <div class="dependent-section">
            <h4 class="dependent-title">Dependent 2</h4>
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
              <span class="label">Relation :</span>
              <span class="value">Dad</span>
            </div>
            <div class="info-row">
              <span class="label">Birth Date :</span>
              <span class="value">1955-11-20</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import Navbar from './Navbar.vue'
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
</style>
