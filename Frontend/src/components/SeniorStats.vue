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
        <Line :data="bpSugarChartData" :options="lineChartOptions" :plugins="[monthLabelPlugin]" />
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
}

// Dummy Data for BP and Sugar Chart
const bpSugarChartData = {
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
  background-color: #eaf5e9;
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
