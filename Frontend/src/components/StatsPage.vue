<template>
  <div class="stats-dashboard-container">
    <header class="dashboard-header">
      <h1>Health at a Glance</h1>
      <Navbar @logout="logout"/>
    </header>

    <div class="member-toggle-group" v-if="role==='care_giver'">
      <button v-for="m in members" :key="m.username"
        class="toggle-button" :class="{ active: current === m.username }"
        @click="selectMember(m)">
        {{ m.username }}
      </button>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>Medicine Compliance (Last 30 Days)</h3>
        <Bar :data="medicineChart" :options="barOptions"/>
      </div>
      <div class="chart-card">
        <h3>Vitals (Last 7 Days)</h3>
        <Line :data="vitalsChart" :options="lineOptions"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from './Navbar.vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend,
  CategoryScale, LinearScale, BarElement, PointElement, LineElement
} from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement)

const router = useRouter()
const role = sessionStorage.getItem('role')
const uid = sessionStorage.getItem('user_id')
const token = sessionStorage.getItem('accesstoken')
const members = ref([])
const statsMap = ref({})
const current = ref(null)

const medicineChart = computed(() => {
  const d = statsMap.value[current.value]?.medicineCompliance || {}
  return {
    labels: d.labels || [],
    datasets: [
      { label: 'Taken', backgroundColor: '#4caf50', data: d.taken || [] },
      { label: 'Missed', backgroundColor: '#f44336', data: d.missed || [] }
    ]
  }
})
const vitalsChart = computed(() => {
  const v = statsMap.value[current.value]?.vitalsLast7 || {}
  return {
    labels: v?.labels || [],
    datasets: [
      { label: 'Systolic', borderColor: '#2196f3', data: v.systolic || [], fill: false },
      { label: 'Diastolic', borderColor: '#e91e63', data: v.diastolic || [], fill: false },
      { label: 'Sugar', borderColor: '#ff9800', data: v.sugar || [], fill: false }
    ]
  }
})
const barOptions = {
  responsive: true,
  plugins: {
    legend: {
      labels: {
        font: {
          weight: 'bold',
          size: 14
        }
      }
    }
  },
  scales: {
    x: {
      stacked: true,
      title: {
        display: true,
        text: 'Medicines',
        font: {
          weight: 'bold',
          size: 16
        }
      },
      ticks: {
        font: {
          weight: 'bold',
          size: 13
        }
      }
    },
    y: {
      stacked: true,
      beginAtZero: true,
      title: {
        display: true,
        text: 'Count',
        font: {
          weight: 'bold',
          size: 16
        }
      },
      ticks: {
        font: {
          weight: 'bold',
          size: 13
        }
      }
    }
  }
}
//const barOptions = { responsive: true, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } }
const lineOptions = {
  responsive: true,
  plugins: {
    legend: {
      labels: {
        font: {
          weight: 'bold',
          size: 14
        }
      }
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Date',
        font: {
          weight: 'bold',
          size: 16
        }
      },
      ticks: {
        font: {
          weight: 'bold',
          size: 13
        }
      }
    },
    y: {
      beginAtZero: false,
      title: {
        display: true,
        text: 'Reading Value',
        font: {
          weight: 'bold',
          size: 16
        }
      },
      ticks: {
        font: {
          weight: 'bold',
          size: 13
        }
      }
    }
  }
}
function logout(){ sessionStorage.clear(); router.push('/login') }
function selectMember(m){ current.value = m.username }

onMounted(async () => {
  if (!uid || !token) return router.push('/login')
  if (role==='care_giver') {
    const dres = await fetch('http://localhost:5000/sc/my-dependents', {
      headers:{ 'Authorization':`Bearer ${token}` }
    })
    const { dependents } = await dres.json()
    members.value = dependents
    for (const m of dependents) {
      const r = await fetch(`http://localhost:5000/sc/user-stats/${m.id}`, {
        headers:{ 'Authorization':`Bearer ${token}` }
      })
      statsMap.value[m.username] = await r.json()
    }
    current.value = members.value[0].username
  }
  else if (role==='senior_citizen') {
    members.value = [{ id: uid, username: 'Me' }]
    const r = await fetch(`http://localhost:5000/sc/user-stats/${uid}`, {
      headers:{ 'Authorization':`Bearer ${token}` }
    })
    statsMap.value['Me'] = await r.json()
    current.value = 'Me'
  }
})
</script>

<style scoped>
/* FIX 4: Changed CSS selector to match the class in the template */
.stats-dashboard-container {
  background-color: #eaf5e9;
  font-family: "Times New Roman", serif;
  min-height: 100vh;
  padding: 2.5rem 3rem;
  display: flex;
  flex-direction: column;
}


/* New Header Style */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  border-bottom: 1px solid #d0e0cf;
  padding-bottom: 1.5rem;
}
.greeting h1 {
  font-family: 'Georgia', serif;
  font-weight: 500;
  font-size: 2.5rem;
  margin: 0;
  color: #333;
}
.greeting p {
  font-style: italic;
  color: #666;
  margin-top: 0.5rem;
}

/* New Toggle Button Styles */
.member-toggle-group {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  background-color: #dbe8d9;
  padding: 0.5rem;
  border-radius: 50px;
  align-self: center;
}
.toggle-button {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 50px;
  background-color: transparent;
  font-family: "Times New Roman", serif;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  color: #555;
  transition: all 0.3s ease;
}
.toggle-button.active {
  background-color: #fff;
  color: #2c5e2e;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Chart Layout and Card Styling */
.charts-row {
  flex-grow: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.chart-card {
  background-color: #f7fbf6;
  padding: 1.5rem 2rem;
  border-radius: 20px;
  border: 1px solid #dbe8d9;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
}

.chart-title {
  text-align: center;
  font-size: 1.3rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1.5rem;
}

.chart-area {
  flex-grow: 1;
  position: relative;
  min-height: 350px;
}
</style>