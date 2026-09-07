// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>
  import MonthGenerationChart from "@/components/calculator/charts/CurrentMonthStats/MonthGenerationChart.vue";
  import backendApi from "@/services/backendApi.js";
  import {computed, onMounted, ref} from "vue";
  import ChooseMonth from "@/components/calculator/timemachine/ChooseMonth.vue";
  import {useDateRangeStore} from "../../../../../store/useDateRangeStore.js";
  import {storeToRefs} from "pinia";
  import LayersOfYears from "@/components/calculator/charts/CurrentMonthStats/LayersOfYears.vue";

  const dateRangeStore = useDateRangeStore();
  const { monthGenerationChartData, selectedYear, selectedMonth, errorMsg, errorClass } = storeToRefs(dateRangeStore);

  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  const currentGraphTitle = computed(() => {
    return `${monthNames[selectedMonth.value]} ${selectedYear.value}`;
  });

  onMounted(async () => {
    await dateRangeStore.fetchDateRange();
    await dateRangeStore.getMonthGeneration();
  });
</script>

<template>
  <div class="modal fade" id="CurrentMonthStatsModal" data-bs-backdrop="false" aria-hidden="true" aria-labelledby="CurrentMonthStatsModalLabel" tabindex="-1">
    <div class="modal-dialog modal-xxl modal-dialog-centered">
      <div class="modal-content neomorphic p-0">
        <div class="modal-body ps-2 pe-2 pb-0">
          <div class="row pt-1 pe-2">
            <div class="row justify-content-center justify-content-lg-start align-items-center m-0">
              <div class="col-12 col-md-6 col-xl-3 d-flex justify-content-center justify-content-lg-start align-items-center mb-3 mb-lg-0">
                <choose-month />
              </div>
              <div class="col-12 col-md-6 col-xl-3 d-flex justify-content-center justify-content-lg-start mb-3 mb-lg-0">
                <layers-of-years />
              </div>
              <div class="col-12 col-xl-6 d-flex justify-content-end m-0">
                <div class="display-flex flex-row align-items-center">
                  <p class="small text-purple my-auto mr-5">Analytics for the current month with a generation power forecast and actual power generation, with a layered power generation chart for the same month in the last or/and the year before last</p>
                  <button type="button" class="btn-close p-0" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
              </div>
            </div>
            <div class="d-flex flex-row justify-content-between">
              <div class="display-flex flex-row justify-content-center align-items-center ml-3">


              </div>

            </div>
          </div>
          <month-generation-chart
              v-if="monthGenerationChartData"
              :month-name="currentGraphTitle"
              :labels="monthGenerationChartData.labels"
              :actual-power="monthGenerationChartData.actual_power"
              :forecast-power="monthGenerationChartData.forecast_power"
              :last-year-power="monthGenerationChartData.last_year_power"
              :two-years-ago-power="monthGenerationChartData.two_years_ago_power"
              :last-year-label="monthGenerationChartData.last_year_label"
              :two-years-ago-label="monthGenerationChartData.two_years_ago_label"
          />

<!--          DEPRECATED-->
<!--          <month-generation-chart-->
<!--              v-if="monthGenerationChartData"-->
<!--              :month-name="currentGraphTitle"-->
<!--              :labels="monthGenerationChartData.labels"-->
<!--              :actual-power="monthGenerationChartData.actual_power"-->
<!--              :forecast-power="monthGenerationChartData.forecast_power"-->
<!--          />-->

          <div v-else-if="!errorMsg" class="text-center p-5 text-secondary">
            Analytics loading...
          </div>

          <div v-if="errorMsg" :class="['alert', errorClass, 'text-center']">
            {{ errorMsg }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>