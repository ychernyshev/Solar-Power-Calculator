<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<script setup lang="ts">
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import {useOpenMeteoForecastStore} from "../../../../../store/useOpenMeteoForecastStore";
import {storeToRefs} from "pinia";

const solarForecastStore = useOpenMeteoForecastStore();
const {isLocationDenied} = storeToRefs(solarForecastStore);

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

interface ChartDataProps {
  monthName: string;
  labels: number[];
  actualPower: (number | null)[];
  forecastPower: (number | null)[];
  lastYearPower?: (number | null)[];
  twoYearsAgoPower?: (number | null)[];
  lastYearLabel?: string;
  twoYearsAgoLabel?: string;
}

const props = withDefaults(defineProps<ChartDataProps>(), {
  monthName: 'Current Month',
  labels: () => [],
  actualPower: () => [],
  forecastPower: () => [],
  lastYearPower: () => [],
  twoYearsAgoPower: () => [],
  lastYearLabel: 'Last Year',
  twoYearsAgoLabel: 'Two Years Ago'
});

// DEPRECATED
// interface ChartDataProps {
//   monthName: string;
//   labels: number[];
//   actualPower: (number | null)[];
//   forecastPower: (number | null)[];
// }
//
// const props = withDefaults(defineProps<ChartDataProps>(), {
//   monthName: 'Current Month',
//   labels: () => [],
//   actualPower: () => [],
//   forecastPower: () => []
// });

const todayDay = computed(() => new Date().getDate());

const chartData = computed(() => {
  const datasets: any[] = [
    {
      label: 'Actual generation (kWh)',
      data: props.actualPower,
      borderColor: '#a855f7',
      backgroundColor: '#a855f7',
      tension: 0.4,
      borderWidth: 4,
      pointRadius: (context: any) => context.dataIndex + 1 === todayDay.value ? 6 : 3,
      pointBackgroundColor: '#a855f7',
      spanGaps: true
    }
  ];

  if (!isLocationDenied.value) {
    datasets.push({
      label: 'Forecast generation (kWh)',
      data: props.forecastPower,
      borderColor: '#9ca3af',
      backgroundColor: '#9ca3af',
      tension: 0.4,
      borderWidth: 3,
      borderDash: [6, 4],
      pointRadius: 0,
      spanGaps: true
    });
  }

  if (props.lastYearPower && props.lastYearPower.length > 0) {
    datasets.push({
      label: props.lastYearLabel,
      data: props.lastYearPower,
      borderColor: '#3b82f6',
      backgroundColor: '#3b82f6',
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 2,
      spanGaps: true
    });
  }

  if (props.twoYearsAgoPower && props.twoYearsAgoPower.length > 0) {
    datasets.push({
      label: props.twoYearsAgoLabel,
      data: props.twoYearsAgoPower,
      borderColor: '#10b981',
      backgroundColor: '#10b981',
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 2,
      spanGaps: true
    });
  }

  return {
    labels: props.labels,
    datasets
  };
});

// DEPRECATED
// const chartData = computed(() => {
//   const datasets = [
//     {
//       label: 'Actual generation (kWh)',
//       data: props.actualPower,
//       borderColor: '#a855f7',
//       backgroundColor: '#a855f7',
//       tension: 0.4,
//       borderWidth: 4,
//       pointRadius: (context: any) => context.dataIndex + 1 === todayDay.value ? 6 : 3,
//       pointBackgroundColor: '#a855f7',
//       spanGaps: true
//     }
//   ];
//
//   if (!isLocationDenied.value) {
//     datasets.push({
//       label: 'Forecast generation (kWh)',
//       data: props.forecastPower,
//       borderColor: '#9ca3af',
//       backgroundColor: '#9ca3af',
//       tension: 0.4,
//       borderWidth: 3,
//       borderDash: [6, 4],
//       pointRadius: 0,
//       spanGaps: true
//     });
//   }
//
//   return {
//     labels: props.labels,
//     datasets
//   };
// });

const todayLinePlugin = {
  id: 'todayLine',
  afterDatasetsDraw(chart: any) {
    const { ctx, chartArea: { top, bottom }, scales: { x } } = chart;

    const todayIndex = props.labels.indexOf(todayDay.value);

    if (todayIndex !== -1) {
      const xPos = x.getPixelForValue(todayIndex);

      ctx.save();
      ctx.beginPath();
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#4b5563';
      ctx.setLineDash([4, 4]);
      ctx.moveTo(xPos, top);
      ctx.lineTo(xPos, bottom);
      ctx.stroke();

      ctx.fillStyle = '#4b5563';
      ctx.font = 'bold 10px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('TODAY', xPos, top - 8);

      ctx.restore();
    }
  }
};

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        color: '#4b5563',
        font: { family: 'inherit', weight: 'bold' }
      }
    },
    tooltip: {
      mode: isLocationDenied.value ? ('nearest' as const) : ('index' as const),
      intersect: isLocationDenied.value,
      padding: 12,
      backgroundColor: '#1f2937'
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#6b7280' }
    },
    y: {
      min: 0,
      grid: { color: 'rgba(0, 0, 0, 0.05)' },
      ticks: { color: '#6b7280' }
    }
  }
}));
</script>

<template>
  <div class="solar-chart-card p-3 position-relative">
    <div v-if="isLocationDenied" class="w-100 text-center mb-2">
      <span class="badge-content px-3 py-1-5 text-muted small tracking-wider fw-bold">
        ⚠ Forecast: Geolocation Required
      </span>
    </div>

    <div class="chart-container p-0">
      <Line :data="chartData" :options="chartOptions" :plugins="[todayLinePlugin]" />
    </div>
  </div>
</template>

<style scoped>
.solar-chart-card {
  border-radius: 20px;
  margin: 20px 0;
}
.chart-container {
  position: relative;
  height: 350px;
  width: 100%;
}

.forecast-denied-badge {
  position: absolute;
  top: 40px;
  right: 20px;
  z-index: 10;
  pointer-events: none;
}

.badge-content {
  display: inline-block;
  background: rgba(239, 68, 68, 0.05);
  border: 1px dashed #ced4da;
  border-radius: 10px;
  font-size: 0.85rem;
}

.tracking-wider {
  letter-spacing: 0.05em;
}
</style>