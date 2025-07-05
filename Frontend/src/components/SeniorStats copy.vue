<template>
  <div class="stats-dashboard-container">
    <!-- NEW: Consistent Header with Navbar -->
    <header class="dashboard-header">
      <div class="greeting">
        <h1>Health at a Glance</h1>
        <p>Your personal health trends</p>
      </div>
      <!-- You may need to change 'TheNavbar' to 'Navbar' depending on your file name -->
      <Navbar @logout="logout" />
    </header>

    <!-- RE-STYLED: Charts are now in "cards" -->
    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">Medicines Taken (Last 30 Days)</h3>
        <div class="chart-area">
          <Bar :data="medicineChartData" :options="barChartOptions" />
        </div>
      </div>

      <div class="chart-card">
        <h3 class="chart-title">Vitals (Last Quarter)</h3>
        <div class="chart-area">
        <Line :data="bpSugarChartData" :options="lineChartOptions" :plugins="[monthLabelPlugin]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
<<<<<<< HEAD
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
};

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
)
// Dummy Data for Medicine Chart
const medicineChartData = {
  labels: ['Lisinopril', 'Metformin', 'Atorvastatin', 'Amlodipine'],
  datasets: [
    {
      label: 'Count of Medicines taken',
      backgroundColor: ['#36A2EB', '#FF6384','#8884d8', '#e78ac3'],
      data: [30, 24, 18, 12]
    }
  ]
=======
import { Bar, Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';
// Imports to support the new header
import { useRouter } from 'vue-router';
import Navbar from './Navbar.vue'; // Using the multi-word name

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

// --- Logic for Navbar ---
const router = useRouter();
function logout() {
  sessionStorage.clear();
  router.push('/login');
>>>>>>> 8e610b2 (Modified aesthetics of all frontend pages)
}

// --- Aesthetically Enhanced Chart Data ---
const vibrantColors = ['#20c997', '#fd7e14', '#e83e8c', '#0dcaf0'];
const lineColors = ['#20c997', '#e83e8c', '#fd7e14'];

const medicineChartData = {
  labels: ['Lisinopril', 'Metformin', 'Atorvastatin', 'Amlodipine'],
  datasets: [{
    label: 'Count',
    backgroundColor: vibrantColors,
    borderColor: '#ffffff',
    borderWidth: 2,         // Creates a white border around each bar for a "propped-up" look
    borderRadius: 5,        // Rounds the corners of the bars
    data: [30, 24, 18, 12]
  }]
};

const bpSugarChartData = {
  labels: [
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4'
  ],
  datasets: [
    {
      label: 'Systolic BP',
<<<<<<< HEAD
      borderColor: '#36A2EB',
      data: [124, 126, 125, 128, 129, 123, 127, 126, 124, 125, 128, 127],
      fill: false,
      tension: 0.3
    },
    {
      label: 'Diastolic BP',
      borderColor: '#FF6384',
      data: [80, 81, 83, 82, 79, 80, 81, 83, 82, 79, 78, 80],
      fill: false,
      tension: 0.3
    },
    {
      label: 'Sugar (mg/dL)',
      borderColor: '#8e5ea2',
      data: [135, 140, 138, 142, 137, 139, 141, 138, 136, 137, 135, 139],
      fill: false,
      tension: 0.3
=======
      borderColor: lineColors[0],
      data: [125, 130, 128],
      borderWidth: 3,
      pointBackgroundColor: lineColors[0],
      pointRadius: 5
    },
    {
      label: 'Diastolic BP',
      borderColor: lineColors[1],
      data: [82, 85, 80],
      borderWidth: 3,
      pointBackgroundColor: lineColors[1],
      pointRadius: 5
    },
    {
      label: 'Sugar (mg/dL)',
      borderColor: lineColors[2],
      data: [140, 135, 145],
      borderWidth: 3,
      pointBackgroundColor: lineColors[2],
      pointRadius: 5
>>>>>>> 8e610b2 (Modified aesthetics of all frontend pages)
    }
  ]
};

// --- Aesthetically Enhanced Chart Options ---
const barChartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
<<<<<<< HEAD
    x: {
       ticks:{
        font: {
          weight: 'bold',
          size: 14
        }
      },
      title: {
        display: true,
        text: 'Medicine Name',
        font: {
          weight: 'bold',
          size: 16
        }
      }
    },
=======
    x: { ticks: { color: '#444', font: { weight: '600' } }, grid: { display: false } },
>>>>>>> 8e610b2 (Modified aesthetics of all frontend pages)
    y: {
      ticks: { color: '#444', font: { weight: '600' } },
      title: { display: true, text: 'Count', font: { weight: 'bold', size: 14 } },
      grid: { color: '#eef2ed', borderDash: [5, 5] },
      beginAtZero: true
    }
  }
};

const lineChartOptions = {
  responsive: true, maintainAspectRatio: false,
  elements: { line: { tension: 0.4 } }, // Makes lines beautifully curved
  plugins: {
<<<<<<< HEAD
    legend: {
      labels: {
        font: {
          weight: 'bold',
          size: 14
        }
      }
    },monthLabelPlugin: {}
  },
  scales: {
    x: {
      ticks: {
        font: {
          weight: 'bold',
          size: 14
        }
      },
      title: {
      display: true,
      font: {
          weight: 'bold',
          size: 16
        }
      }
    },
=======
    legend: { position: 'top', align: 'center', labels: { usePointStyle: true, boxWidth: 10, padding: 20, font: { weight: 'bold' } } }
  },
  scales: {
    x: { ticks: { color: '#444', font: { weight: '600' } }, grid: { display: false } },
>>>>>>> 8e610b2 (Modified aesthetics of all frontend pages)
    y: {
      ticks: { color: '#444', font: { weight: '600' } },
      title: { display: true, text: 'Values', font: { weight: 'bold', size: 14 } },
      grid: { color: '#eef2ed', borderDash: [5, 5] },
      suggestedMin: 70, // Retaining your useful suggestions
      suggestedMax: 160
    }
  }
};
</script>

<style scoped>
<<<<<<< HEAD
.senior-stats-container {
  font-family: 'Serif', Georgia, Times, 'Times New Roman';
  margin-top: 0px;
  height: 100vh;
  padding: 1rem 2rem 2rem 2rem;
  background-color: #eaf5e9;
=======
/* These styles are copied and adapted from CaregiverStats.vue for consistency */
.stats-dashboard-container {
  background-color: #eaf5e9;
  font-family: "Times New Roman", serif;
  min-height: 100vh;
  padding: 2.5rem 3rem;
>>>>>>> 8e610b2 (Modified aesthetics of all frontend pages)
  display: flex;
  flex-direction: column;
}

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

.charts-row {
  flex-grow: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem; /* Added space since there are no toggle buttons */
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