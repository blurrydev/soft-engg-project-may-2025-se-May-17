<template>
  <div class="caregiver-stats-container">
    <h1 class="text-center mb-4">Family Health Overview</h1>
    <div class="text-center mb-4">
      <button
        v-for="member in Object.keys(memberData)"
        :key="member"
        class="btn btn-outline-dark mx-2"
        :class="{ active: currentMember === member }"
        @click="currentMember = member"
      >
        {{ member }}
      </button>
    </div>

    <div class="charts-row">
      <div class="chart-section">
        <h3 class="text-center mb-3">Medicines Taken in the Last Month</h3>
        <div class="chart-area">
          <Bar :data="currentData.medicineChartData" :options="barChartOptions" />
        </div>
      </div>

      <div class="chart-section">
        <h3 class="text-center mb-3">Blood Pressure & Sugar (Last Quarter)</h3>
        <div class="chart-area">
          <Line :data="currentData.bpSugarChartData" :options="lineChartOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
)

const memberData = {
  Mom: {
    medicineChartData: {
      labels: ['Lisinopril', 'Metformin','Atorvastatin', 'Amlodipine'],
      datasets: [{
        label: 'Count',
        backgroundColor: ['#36A2EB', '#FF6384','#8884d8', '#e78ac3'],
        data: [8,15, 20,10]
      }]
    },
    bpSugarChartData: {
      labels: ['Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Systolic BP',
          borderColor: '#36A2EB',
          data: [122, 125, 124],
          fill: false
        },
        {
          label: 'Diastolic BP',
          borderColor: '#FF6384',
          data: [78, 80, 77],
          fill: false
        },
        {
          label: 'Sugar (mg/dL)',
          borderColor: '#8e5ea2',
          data: [135, 140, 138],
          fill: false
        }
      ]
    }
  },
  Dad: {
    medicineChartData: {
      labels: ['Atorvastatin', 'Amlodipine','Metformin'],
      datasets: [{
        label: 'Count',
        backgroundColor: ['#36A2EB', '#FF6384','#8884d8',],
        data: [20, 18,15]
      }]
    },
    bpSugarChartData: {
      labels: ['Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Systolic BP',
          borderColor: '#36A2EB',
          data: [130, 128, 127],
          fill: false
        },
        {
          label: 'Diastolic BP',
          borderColor: '#FF6384',
          data: [84, 83, 82],
          fill: false
        },
        {
          label: 'Sugar (mg/dL)',
          borderColor: '#8e5ea2',
          data: [145, 140, 142],
          fill: false
        }
      ]
    }
  },
  Uncle: {
    medicineChartData: {
      labels: ['Albuterol','Metformin','Lisinopril'],
      datasets: [{
        label: 'Count',
        backgroundColor: ['#36A2EB','#8884d8', '#e78ac3'],
        data: [12,25,7]
      }]
    },
    bpSugarChartData: {
      labels: ['Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Systolic BP',
          borderColor: '#36A2EB',
          data: [118, 120, 119],
          fill: false
        },
        {
          label: 'Diastolic BP',
          borderColor: '#FF6384',
          data: [76, 75, 74],
          fill: false
        },
        {
          label: 'Sugar (mg/dL)',
          borderColor: '#8e5ea2',
          data: [130, 128, 132],
          fill: false
        }
      ]
    }
  }
}

const currentMember = ref('Mom')
const currentData = computed(() => memberData[currentMember.value])

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { font: { weight: 'bold' } } }
  },
  scales: {
    x: { ticks: { font: { weight: 'bold' } },
      title: {
        display: true,
        text: 'Medicine Name',
        font: {
          weight: 'bold',
          size: 16
        }
      } },
    y: { ticks: { font: { weight: 'bold' } },
      title: {
        display: true,
        text: 'Count',
        font: {
          weight: 'bold',
          size: 16
        }
      },beginAtZero: true }
  }
}

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { font: { weight: 'bold' } } }
  },
  scales: {
    x: { ticks: { font: { weight: 'bold' } } ,
      title: {
        display: true,
        text: 'Month',
        font: {
          weight: 'bold',
          size: 16
        }
      }},
    y: { ticks: { font: { weight: 'bold' } },
      title: {
        display: true,
        text: 'Values',
        font: {
          weight: 'bold',
          size: 16
        }
      }, beginAtZero: false }
  }
}
</script>

<style scoped>
.caregiver-stats-container {
  font-family: 'Georgia', serif;
  height: 100vh;
  padding: 1rem 2rem;
  background-color: #d6eed6;
  display: flex;
  flex-direction: column;
}

.button-group {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.charts-row {
  flex: 1;
  display: flex;
  justify-content: space-between;
  gap: 5rem;
  height: 100%;
  margin-left: 50px;
  margin-right: 50px;
}

.chart-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chart-area {
  flex: 1;
  position: relative;
  max-height: 80%;
  min-height: 400px;
}
button.active {
  background-color: #198754;
  color: white;
}
</style>
