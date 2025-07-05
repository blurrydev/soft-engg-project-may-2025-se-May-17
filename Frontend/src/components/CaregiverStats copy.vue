<template>
  <div class="stats-dashboard-container">
    <!-- NEW: Consistent Header with Navbar -->
    <header class="dashboard-header">
      <div class="greeting">
        <h1>Family Health Overview</h1>
        <p>A visual summary of health trends</p>
      </div>
      <Navbar @logout="logout" />
    </header>

    <!-- RE-STYLED: Member selection buttons -->
    <div class="member-toggle-group">
      <button
        v-for="member in Object.keys(memberData)"
        :key="member"
        class="toggle-button"
        :class="{ active: currentMember === member }"
        @click="currentMember = member"
      >
        {{ member }}
      </button>
    </div>

    <!-- RE-STYLED: Charts are now in "cards" -->
    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">Medicines Taken (Last 30 Days)</h3>
        <div class="chart-area">
          <Bar :data="currentData.medicineChartData" :options="barChartOptions" />
        </div>
      </div>

      <div class="chart-card">
        <h3 class="chart-title">Vitals (Last Quarter)</h3>
        <div class="chart-area">
          <Line :data="currentData.bpSugarChartData" :options="lineChartOptions" :plugins="[monthLabelPlugin]"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import Navbar from './Navbar.vue'; // Import the reusable Navbar
import { Bar, Line } from 'vue-chartjs';
import {
  Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale,
  LinearScale, PointElement, LineElement
} from 'chart.js';

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
// --- ADDED FOR NAVBAR ---
const router = useRouter();
function logout() {
  sessionStorage.clear();
  router.push('/login');
}

const memberData = {
  Mom: {
    medicineChartData: {
      labels: ['Lisinopril', 'Metformin','Atorvastatin', 'Amlodipine'],
      datasets: [{
        label: 'Count',
        backgroundColor: ['#8884d8', '#82ca9d', '#ffc658', '#e78ac3'],
        data: [8,15, 20,10]
      }]
    }
  }
}
const monthLabelPlugin = {
  id: 'monthLabelPlugin',
  afterDraw(chart) {
    const { ctx, chartArea, scales } = chart;
    const xAxis = scales.x;
    const months = ['Apr', 'May', 'Jun'];
    const labelPositions = [0, 4, 8]; // indices where each month starts

    ctx.save();
    ctx.font = 'bold 14px Segoe UI';
    ctx.fillStyle = '#333';
    ctx.textAlign = 'center';

    labelPositions.forEach((startIndex, i) => {
      const endIndex = startIndex + 3;
      const startPixel = xAxis.getPixelForTick(startIndex);
      const endPixel = xAxis.getPixelForTick(endIndex);
      const center = (startPixel + endPixel) / 2;

      ctx.fillText(
        months[i],
        center,
        chartArea.bottom + 40 // adjust vertical position as needed
      );
    });

    ctx.restore();
  }
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
  ]}
  },
  Dad: {
    medicineChartData: {
      labels: ['Atorvastatin', 'Amlodipine','Metformin'],
      datasets: [{
        label: 'Count',
        backgroundColor: ['#8884d8', '#e78ac3', '#82ca9d'],
        data: [20, 18,15]
      }]
    },
    bpSugarChartData: {
      labels: [
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4'
  ],
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

const currentMember = ref('Mom');
const currentData = computed(() => memberData[currentMember.value]);

// --- AESTHETICALLY IMPROVED CHART OPTIONS ---
const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } }, // Hide legend as it's redundant for one dataset
  scales: {
    x: { ticks: { color: '#333', font: { weight: '600' } }, grid: { display: false } },
    y: {
      ticks: { color: '#333', font: { weight: '600' } },
      title: { display: true, text: 'Count', font: { weight: 'bold', size: 14 } },
      beginAtZero: true
    }
  }
};

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  elements: { line: { tension: 0.4 } }, // This makes the lines beautifully curved
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
};
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
  flex-grow: 1; /* Allows this row to fill available space */
  display: grid;
  grid-template-columns: 1fr 1fr; /* Two equal columns */
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
  position: relative; /* Required for chart.js responsiveness */
  min-height: 350px; /* Ensures chart has space */
}
</style>