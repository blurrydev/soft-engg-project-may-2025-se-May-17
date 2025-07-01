<template>
  <div class="senior-stats-container">
    <h1 class="mb-4 text-center">Health at a Glance</h1>

    <div class="charts-row">
      <div class="chart-section">
        <h3 class="text-center mb-3">Medicines Taken in the Last Month</h3>
        <div class="chart-area">
          <Bar :data="medicineChartData" :options="barChartOptions" />
        </div>
      </div>

      <div class="chart-section">
        <h3 class="text-center mb-3">Blood Pressure & Sugar Levels (Last Quarter)</h3>
        <div class="chart-area">
          <Line :data="bpSugarChartData" :options="lineChartOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
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
}

// Dummy Data for BP and Sugar Chart
const bpSugarChartData = {
  labels: ['Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Systolic BP',
      borderColor: '#36A2EB',
      data: [125, 130, 128],
      fill: false
    },
    {
      label: 'Diastolic BP',
      borderColor: '#FF6384',
      data: [82, 85, 80],
      fill: false
    },
    {
      label: 'Sugar (mg/dL)',
      borderColor: '#8e5ea2',
      data: [140, 135, 145],
      fill: false
    }
  ]
}

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
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
      ticks: {
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
    y: {
      beginAtZero: true,
      ticks: {
        font: {
          weight: 'bold',
          size: 14
        }
      },
      title: {
        display: true,
        text: 'Count',
        font: {
          weight: 'bold',
          size: 16
        }
      }
    }
  }
}

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
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
      ticks: {
        font: {
          weight: 'bold',
          size: 14
        }
      },
      title: {
        display: true,
        text: 'Month',
        font: {
          weight: 'bold',
          size: 16
        }
      }
    },
    y: {
      beginAtZero: false,
      suggestedMin: 70,
      suggestedMax: 160,
      ticks: {
        font: {
          weight: 'bold',
          size: 14
        }
      },
      title: {
        display: true,
        text: 'Values',
        font: {
          weight: 'bold',
          size: 16
        }
      }
    }
  }
}
</script>

<style scoped>
.senior-stats-container {
  font-family: 'Serif', Georgia, Times, 'Times New Roman';
  margin-top: 0px;
  height: 100vh;
  padding: 1rem 2rem 2rem 2rem;
  background-color: #d6eed6;
  display: flex;
  flex-direction: column;
}

h2 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.75rem;
}

.charts-row {
  flex: 1;
  display: flex;
  gap: 5rem;
  overflow: hidden;
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
  min-height: 250px;
  max-height: 85%;
}
</style>
