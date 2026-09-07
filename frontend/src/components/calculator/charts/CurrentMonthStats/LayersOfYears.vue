<script setup>
    import { storeToRefs } from "pinia";
    import {useDateRangeStore} from "../../../../../store/useDateRangeStore.js";

    const dateRangeStore = useDateRangeStore();
    const {
      compareLastYear,
      compareTwoYearsAgo,
      hasLastYearData,
      hasTwoYearsAgoData,
      selectedYear
    } = storeToRefs(dateRangeStore);
</script>

<template>
  <div class="neomorphic ml-lg-4 p-1 pt-2 pb-2 pl-3"
       :class="[!hasLastYearData ? 'text-muted opacity-50 item-transition' : 'item-transition']">
    <div class="form-check form-check-inline">
      <input class="form-check-input"
             type="checkbox"
             id="lastYearCheck"
             :checked="compareLastYear"
             :disabled="!hasLastYearData"
             @change="dateRangeStore.toggleCompareLastYear()">
      <label class="form-check-label"
             for="lastYearCheck"
             :class="{ 'text-muted opacity-50': !hasLastYearData }">add the last year</label>
    </div>
    <div class="form-check form-check-inline">
      <input class="form-check-input"
             type="checkbox"
             id="twoYearsAgoCheck"
             :checked="compareTwoYearsAgo"
             :disabled="!hasTwoYearsAgoData"
             @change="dateRangeStore.toggleCompareTwoYearsAgo()">
      <label class="form-check-label"
             for="twoYearsAgoCheck"
             :class="{ 'text-muted opacity-50': !hasTwoYearsAgoData }">add the year before last</label>
    </div>
  </div>
</template>

<style scoped>
  .item-transition {
    transition: 0.3s ease;
  }
</style>