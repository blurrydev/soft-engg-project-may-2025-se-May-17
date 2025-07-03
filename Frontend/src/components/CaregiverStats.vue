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
          <Line :data="currentData.bpSugarChartData" :options="lineChartOptions" :plugins="[monthLabelPlugin]"/>
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
  bpSugarChartData :{
  labels: [
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4'
  ],
  datasets: [
    {
      label: 'Systolic BP',
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
    }
  ]}
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
      labels: [
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4'
  ],
      datasets: [
        {
          label: 'Systolic BP',
          borderColor: '#36A2EB',
          data: [118, 120, 117, 119, 121, 123, 124, 122, 120, 121, 119, 118],
          fill: false
        },
        {
          label: 'Diastolic BP',
          borderColor: '#FF6384',
          data: [78, 76, 77, 79, 80, 78, 77, 76, 75, 74, 76, 75],
          fill: false
        },
        {
          label: 'Sugar (mg/dL)',
          borderColor: '#8e5ea2',
          data: [128, 125, 126, 124, 122, 120, 121, 123, 124, 122, 123, 125],
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
      labels: [
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4',
    'W1', 'W2', 'W3', 'W4'
  ],
      datasets: [
        {
          label: 'Systolic BP',
          borderColor: '#36A2EB',
          data: [135, 134, 136, 137, 138, 137, 136, 134, 135, 133, 134, 136],
          fill: false
        },
        {
          label: 'Diastolic BP',
          borderColor: '#FF6384',
          data: [88, 87, 89, 90, 91, 90, 89, 87, 88, 86, 87, 88],
          fill: false
        },
        {
          label: 'Sugar (mg/dL)',
          borderColor: '#8e5ea2',
          data: [150, 148, 149, 147, 146, 144, 143, 145, 146, 145, 144, 142],
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
  },monthLabelPlugin: {},
  scales: {
    x: { ticks: { font: { weight: 'bold' } } ,
      title: {
        display: true,
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
  background-color: #eaf5e9;
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
