// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>
import {computed, onMounted, ref} from "vue";
import backendApi from "../../../services/calculator/backendApi.js";
import {useOpenMeteoForecastStore} from "../../../../store/useOpenMeteoForecastStore.js";
import {storeToRefs} from "pinia";

const solarForecastStore = useOpenMeteoForecastStore();
const {isLocationDenied} = storeToRefs(solarForecastStore);
const current_month_details = ref([]);
const loading = ref(true);
const errorMsg = ref("");
const errorClass = ref("");

const date = new Date();
const currentMonthName = date.toLocaleString('en-US', {month: 'long'});

// Last month
const lastMonthDate = new Date(date);
lastMonthDate.setDate(1);
lastMonthDate.setMonth(date.getMonth() - 1);
const lastMonthName = lastMonthDate.toLocaleString('en-US', {month: 'long'});

const currentMonthDetails = async () => {
  try {
    loading.value = true;
    const response = await backendApi.get('calculator/current_month_stats/');
    if (response.data.is_empty) {
      errorMsg.value = "Add the first data for this month";
      errorClass.value = "alert-success";
    } else {
      current_month_details.value = response.data;
      errorMsg.value = "";
    }
    console.log(`Response: ${response}`)
    current_month_details.value = response.data;
  } catch (error) {
    console.error("API Error:", error);
    errorMsg.value = "Failed to load month stats";
    errorClass.value = "alert-warning";
  } finally {
    loading.value = false;
  }
}

const ifMonthTotalPowerIsNegativeOrNull = computed(() => {
  const val = current_month_details.value.difference_power_percentage;
  return val < 0 || val === null;
});

onMounted(() => {
  currentMonthDetails();
});
</script>

<template>
  <div class="mt-3 mt-md-0"></div>
  <div v-if="loading" class="text-center p-3">Loading month stats...</div>
  <div v-else-if="errorMsg" class="alert p-1" :class="errorClass">{{ errorMsg }}</div>
  <div class="row text-start">
    <p data-v-80000e9e="" class="text-purple widget-title">
      The {{ currentMonthName }} stats
    </p>
    <div class="col-6 d-inline-flex flex-column align-items-start widget-item">
      <div v-if="!loading && current_month_details" class="w-100 d-flex flex-column small align-items-start text-purple">
        <span class="fw-bold"></span>
        <span v-if="isLocationDenied" class="small">
          Sun days: <span class="fw-bold">Geolocation Required</span>
        </span>
        <span v-else-if="current_month_details.length === 0" class="small">Sun days: <span class="fw-bold">0</span></span>
        <span v-else class="small">Sun days: <span class="fw-bold">{{ current_month_details.sun_days }}</span></span>
        <span v-if="isLocationDenied" class="small">
          Avr temperature: <span class="fw-bold">Geolocation Required</span>
        </span>
        <span v-else-if="current_month_details.length === 0" class="small">Avr temperature:
          <span class="fw-bold">
            no data
          </span>
        </span>
        <span v-else class="small">Avr temperature: <span class="fw-bold">{{ current_month_details.average_temperature }}&nbsp;&deg;C</span></span>
        <span v-if="current_month_details.length === 0" class="small">
          Day avr power:
          <span class="fw-bold text-success-1">0Wh</span>
        </span>
        <span v-else class="small">Day avr power: <span class="fw-bold text-success-1">{{ current_month_details.average_power }}Wh</span></span>
        <span v-if="current_month_details.length === 0" class="small">
          Total power:
          <span class="fw-bold text-success-1">0Wh</span>
        </span>
        <span v-else class="small">Total power: <span class="fw-bold text-success-1">{{ current_month_details.current_month_total_power.toFixed(2) }}Wh</span></span>
        <span v-if="current_month_details.length === 0" class="small">
          Total savings:
          <span class="fw-bold text-sky-blue-4">0UAH</span>
        </span>
        <span v-else class="small">Total savings: <span class="fw-bold text-sky-blue-4">{{ current_month_details.current_month_savings }}UAH</span></span>
      </div>
    </div>
    <div class="col-6 d-flex flex-column w-100 align-items-end text-purple">
      <div class="text-success-1 d-flex flex-row">
          <span class="d-flex flex-column align-items-start">
            <svg v-if="current_month_details.difference_power_percentage < 0 || current_month_details.difference_power_percentage === null"  xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-down-right" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M14 13.5a.5.5 0 0 1-.5.5h-6a.5.5 0 0 1 0-1h4.793L2.146 2.854a.5.5 0 1 1 .708-.708L13 12.293V7.5a.5.5 0 0 1 1 0z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up-right" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M14 2.5a.5.5 0 0 0-.5-.5h-6a.5.5 0 0 0 0 1h4.793L2.146 13.146a.5.5 0 0 0 .708.708L13 3.707V8.5a.5.5 0 0 0 1 0z"/>
            </svg>
            <span v-if="ifMonthTotalPowerIsNegativeOrNull"
                  :class="{'text-warning': ifMonthTotalPowerIsNegativeOrNull}"
                  class="difference-power">—</span>
            <span v-else class="difference-power">+</span>
          </span>
          <div v-if="current_month_details.difference_power_percentage < 0" class="widget-huge-number text-warning mt-2">{{ Math.abs(current_month_details.difference_power_percentage) }}%</div>
          <div v-else-if="current_month_details.difference_power_percentage === null" class="widget-huge-number text-warning mt-2">100%</div>
          <div v-else-if="current_month_details.length === 0" class="widget-huge-number text-warning mt-2">0%</div>
          <div v-else class="widget-huge-number text-success-1 mt-2">{{ Math.abs(current_month_details.difference_power_percentage) }}%</div>
      </div>
      <span class="">compare to <span class="text-lowercase text-warning-2">{{ lastMonthName }}</span></span>
    </div>
  </div>

<!--  <div class="table-responsive" v-if="!loading && forecast_details">-->
<!--    <table class="table">-->
<!--      <thead>-->
<!--        <th scope="col" v-for="item in forecast_details" :key="item.id">-->
<!--          {{ item.hour || item.time }}-->
<!--        </th>-->
<!--      </thead>-->
<!--      <tbody>-->
<!--      <tr>-->
<!--        <td v-for="item in forecast_details" :key="item.id">-->
<!--          <span>{{ item.temperature }}°C</span>-->
<!--        </td>-->
<!--      </tr>-->
<!--      </tbody>-->
<!--    </table>-->
<!--  </div>-->
</template>

<style scoped>
.widget-title {
  font-size: clamp(1.2rem, 2.8vw, 1.5rem);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.widget-huge-number {
  font-size: clamp(3rem, 10vw, 3.5rem);
  font-weight: 200;
  line-height: 0.5;
}

.difference-power {
  font-size: 1.5rem;
  font-weight: 300
}
</style>